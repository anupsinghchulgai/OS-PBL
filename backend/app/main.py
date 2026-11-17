from datetime import datetime
from pathlib import Path
import io, json, random, uuid
import pandas as pd
from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from .core.config import CORS_ORIGINS, MODEL_DIR
from .db import Base, engine, get_db
from .models import Dataset, DatasetRecord, TrainingJob, ModelArtifact, SimulationRecord
from .schemas.common import ProcessIn, SimulateRequest, CompareRequest, GenerateProcessesRequest, TrainRequest, RecommendationRequest
from .services.scheduler import simulate, compare, ALGORITHMS
from .ml.trainer import start_training
from .ml.features import workload_features

Base.metadata.create_all(bind=engine)

app=FastAPI(title="CPU Scheduling Visualizer API",version="1.0.0",description="FastAPI backend for CPU scheduling simulation and Random Forest recommendation.")
app.add_middleware(CORSMiddleware,allow_origins=CORS_ORIGINS or ["*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])

@app.get("/")
def root(): return {"name":"CPU Scheduling Visualizer API","version":"1.0.0","status":"ok"}

@app.get("/health")
def health(): return {"status":"ok","service":"cpu-scheduling-api","timestamp":datetime.utcnow().isoformat()}

@app.post("/simulate")
def simulate_endpoint(req:SimulateRequest,db:Session=Depends(get_db)):
    try: result=simulate([p.model_dump() for p in req.processes],req.algorithm,req.quantum)
    except ValueError as e: raise HTTPException(400,str(e))
    db.add(SimulationRecord(algorithm=req.algorithm,payload_json=req.model_dump(),result_json=result));db.commit()
    return result

@app.post("/compare")
def compare_endpoint(req:CompareRequest,db:Session=Depends(get_db)):
    try: return compare([p.model_dump() for p in req.processes],req.algorithms,req.quantum)
    except ValueError as e: raise HTTPException(400,str(e))

@app.post("/generate-processes")
def generate(req:GenerateProcessesRequest):
    return {"processes":[{"pid":f"P{i+1}","arrival_time":random.randint(0,max(0,req.count//2)),"burst_time":random.randint(1,12),"priority":random.randint(1,5)} for i in range(req.count)]}

@app.post("/upload")
async def legacy_upload(file:UploadFile=File(...)):
    data=await file.read()
    return {"filename":file.filename,"size":len(data),"status":"uploaded"}

@app.get("/export")
def legacy_export(db:Session=Depends(get_db)):
    rows=db.query(SimulationRecord).order_by(desc(SimulationRecord.created_at)).limit(100).all()
    csv=pd.DataFrame([{"id":r.id,"algorithm":r.algorithm,"created_at":r.created_at.isoformat()} for r in rows]).to_csv(index=False)
    return StreamingResponse(io.BytesIO(csv.encode()),media_type="text/csv",headers={"Content-Disposition":"attachment; filename=simulations.csv"})

def _dataset_summary(d,db):
    recs=db.query(DatasetRecord).filter(DatasetRecord.dataset_id==d.id).all()
    return {"id":d.id,"name":d.name,"version":d.version,"source_filename":d.source_filename,"created_at":d.created_at.isoformat() if d.created_at else None,"record_count":len(recs),"workloads":len(set(r.workload_id for r in recs)),"missing_values":0}


@app.post("/datasets")
def create_dataset(payload: dict, db: Session = Depends(get_db)):
    name = str(payload.get("name") or "").strip()
    if not name:
        raise HTTPException(400, "Dataset name is required.")
    d = Dataset(name=name, version=str(payload.get("version") or "1.0"), source_filename="manual")
    db.add(d); db.commit(); db.refresh(d)
    return _dataset_summary(d, db)

@app.post("/datasets/synthetic")
def synthetic_dataset(payload: dict, db: Session = Depends(get_db)):
    name = str(payload.get("name") or "Synthetic Dataset").strip()
    workloads = max(1, min(int(payload.get("workloads") or 10), 1000))
    processes_per_workload = max(1, min(int(payload.get("processes_per_workload") or 6), 100))
    d = Dataset(name=name, version="1.0", source_filename="synthetic")
    db.add(d); db.flush()
    for w in range(workloads):
        count = processes_per_workload
        for i in range(count):
            db.add(DatasetRecord(
                dataset_id=d.id,
                pid=f"P{i+1}",
                arrival_time=random.randint(0, max(0, count)),
                burst_time=random.randint(1, 12),
                priority=random.randint(1, 5),
                workload_id=f"workload-{w+1}"
            ))
    db.commit(); db.refresh(d)
    return _dataset_summary(d, db)

@app.post("/datasets/upload")
async def dataset_upload(file:UploadFile=File(...),db:Session=Depends(get_db)):
    suffix=Path(file.filename or "").suffix.lower()
    if suffix not in [".csv",".xlsx",".xls"]: raise HTTPException(400,"Only CSV and Excel files are supported.")
    raw=await file.read()
    try:
        if suffix==".csv": df=pd.read_csv(io.BytesIO(raw))
        else: df=pd.read_excel(io.BytesIO(raw))
    except Exception as e: raise HTTPException(400,f"Could not parse dataset: {e}")
    cols={str(c).strip().lower().replace(" ","_"):c for c in df.columns}
    def col(*names):
        for n in names:
            if n in cols:return cols[n]
        return None
    pidc=col("pid","process_id","id"); atc=col("arrival_time","arrival","arrival_time_ms"); btc=col("burst_time","burst","burst_time_ms"); prc=col("priority","prio")
    if not pidc or not atc or not btc: raise HTTPException(400,"Dataset must contain PID, Arrival Time and Burst Time columns.")
    d=Dataset(name=Path(file.filename).stem,source_filename=file.filename,version="1.0");db.add(d);db.flush()
    for i,row in df.iterrows():
        try:
            db.add(DatasetRecord(dataset_id=d.id,pid=str(row[pidc]),arrival_time=float(row[atc]),burst_time=float(row[btc]),priority=float(row[prc]) if prc and pd.notna(row[prc]) else 1,workload_id=str(row.get("workload_id",row.get("workload", "workload-1")))))
        except Exception: continue
    db.commit();db.refresh(d)
    return _dataset_summary(d,db)

@app.get("/datasets")
def datasets(db:Session=Depends(get_db)):
    return [_dataset_summary(d,db) for d in db.query(Dataset).order_by(desc(Dataset.created_at)).all()]

@app.get("/datasets/{dataset_id}")
def dataset(dataset_id:int,db:Session=Depends(get_db)):
    d=db.get(Dataset,dataset_id)
    if not d: raise HTTPException(404,"Dataset not found.")
    out=_dataset_summary(d,db);out["records"]=[{"id":r.id,"pid":r.pid,"arrival_time":r.arrival_time,"burst_time":r.burst_time,"priority":r.priority,"workload_id":r.workload_id} for r in d.records];return out

@app.post("/datasets/{dataset_id}/records")
def add_record(dataset_id:int,record:ProcessIn,db:Session=Depends(get_db)):
    if not db.get(Dataset,dataset_id):raise HTTPException(404,"Dataset not found.")
    r=DatasetRecord(dataset_id=dataset_id,pid=record.pid,arrival_time=record.arrival_time,burst_time=record.burst_time,priority=record.priority,workload_id="workload-1");db.add(r);db.commit();db.refresh(r);return {"id":r.id,"pid":r.pid,"arrival_time":r.arrival_time,"burst_time":r.burst_time,"priority":r.priority,"workload_id":r.workload_id}

@app.put("/datasets/{dataset_id}/records/{record_id}")
def update_record(dataset_id:int,record_id:int,record:ProcessIn,db:Session=Depends(get_db)):
    r=db.query(DatasetRecord).filter_by(id=record_id,dataset_id=dataset_id).first()
    if not r:raise HTTPException(404,"Record not found.")
    r.pid=record.pid;r.arrival_time=record.arrival_time;r.burst_time=record.burst_time;r.priority=record.priority;db.commit();return {"id":r.id,"status":"updated"}

@app.delete("/datasets/{dataset_id}/records/{record_id}")
def delete_record(dataset_id:int,record_id:int,db:Session=Depends(get_db)):
    r=db.query(DatasetRecord).filter_by(id=record_id,dataset_id=dataset_id).first()
    if not r:raise HTTPException(404,"Record not found.")
    db.delete(r);db.commit();return {"status":"deleted"}

@app.delete("/datasets/{dataset_id}")
def delete_dataset(dataset_id:int,db:Session=Depends(get_db)):
    d=db.get(Dataset,dataset_id)
    if not d:raise HTTPException(404,"Dataset not found.")
    db.delete(d);db.commit();return {"status":"deleted"}

@app.get("/datasets/{dataset_id}/download")
def download_dataset(dataset_id:int,db:Session=Depends(get_db)):
    d=db.get(Dataset,dataset_id)
    if not d:raise HTTPException(404,"Dataset not found.")
    df=pd.DataFrame([{"PID":r.pid,"Arrival Time":r.arrival_time,"Burst Time":r.burst_time,"Priority":r.priority,"workload_id":r.workload_id} for r in d.records])
    buf=io.StringIO();df.to_csv(buf,index=False)
    return StreamingResponse(io.BytesIO(buf.getvalue().encode()),media_type="text/csv",headers={"Content-Disposition":f'attachment; filename="{d.name}.csv"'})

@app.post("/ml/train")
def train(req:TrainRequest):
    job_id=start_training(req);return {"job_id":job_id,"status":"queued","message":"Training job created."}

@app.get("/ml/train/{job_id}/status")
def train_status(job_id:int,db:Session=Depends(get_db)):
    j=db.get(TrainingJob,job_id)
    if not j:raise HTTPException(404,"Training job not found.")
    return {"job_id":j.id,"dataset_id":j.dataset_id,"status":j.status,"message":j.message,"metrics":j.metrics_json,"model_version":j.model_version,"created_at":j.created_at.isoformat() if j.created_at else None,"completed_at":j.completed_at.isoformat() if j.completed_at else None}

@app.get("/ml/models")
def models(db:Session=Depends(get_db)):
    return [{"id":m.id,"version":m.version,"dataset_id":m.dataset_id,"created_at":m.created_at.isoformat(),"metrics":m.metrics_json} for m in db.query(ModelArtifact).order_by(desc(ModelArtifact.created_at)).all()]

@app.post("/ml/evaluate")
def evaluate(payload:dict,db:Session=Depends(get_db)):
    version=payload.get("model_version")
    m=db.query(ModelArtifact).filter_by(version=version).first() if version else db.query(ModelArtifact).order_by(desc(ModelArtifact.created_at)).first()
    if not m:return {"status":"not_available","message":"No trained model exists."}
    return {"model_version":m.version,"metrics":m.metrics_json,"feature_importance":m.feature_importance_json}

@app.get("/ml/feature-importance")
def feature_importance(db:Session=Depends(get_db)):
    m=db.query(ModelArtifact).order_by(desc(ModelArtifact.created_at)).first()
    if not m:return {"feature_importance":{}}
    return {"model_version":m.version,"feature_importance":m.feature_importance_json}

@app.get("/ml/training-history")
def training_history(db:Session=Depends(get_db)):
    rows=db.query(TrainingJob).order_by(desc(TrainingJob.created_at)).all()
    out=[]
    for j in rows:
        d=db.get(Dataset,j.dataset_id) if j.dataset_id else None
        metrics=j.metrics_json or {}
        out.append({"training_id":j.id,"dataset_name":d.name if d else None,"dataset_version":d.version if d else None,"model_version":j.model_version,"training_date":j.created_at.isoformat() if j.created_at else None,"workloads":metrics.get("workloads"),"accuracy":metrics.get("testing_accuracy"),"f1_score":metrics.get("f1_score"),"status":j.status,"metrics":metrics,"message":j.message})
    return out

@app.post("/ml/recommend")
def recommend(req:RecommendationRequest,db:Session=Depends(get_db)):
    artifact=db.query(ModelArtifact).order_by(desc(ModelArtifact.created_at)).first()
    if not artifact or not Path(artifact.path).exists():
        raise HTTPException(409,"Random Forest model is not trained yet. Please visit the Model Training page and train the model using your dataset.")
    bundle=__import__("joblib").load(artifact.path);model=bundle["model"];X=workload_features([p.model_dump() for p in req.processes])
    pred=model.predict(X)[0];proba=model.predict_proba(X)[0]
    probs={str(c):float(v) for c,v in zip(model.classes_,proba)}
    dataset=db.get(Dataset,artifact.dataset_id)
    return {"recommended_algorithm":str(pred),"probabilities":probs,"model_version":artifact.version,"dataset_id":artifact.dataset_id,"dataset_name":dataset.name if dataset else None,"model_evaluation":artifact.metrics_json}

@app.get("/ml/model")
def current_model(db:Session=Depends(get_db)):
    m=db.query(ModelArtifact).order_by(desc(ModelArtifact.created_at)).first()
    if not m:return {"trained":False}
    return {"trained":True,"version":m.version,"dataset_id":m.dataset_id,"metrics":m.metrics_json}
