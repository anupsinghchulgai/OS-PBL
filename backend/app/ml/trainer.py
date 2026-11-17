from pathlib import Path
from datetime import datetime
import threading
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.model_selection import train_test_split
from .features import workload_features, FEATURE_NAMES, ALGORITHMS
from ..db import SessionLocal
from ..models import TrainingJob, ModelArtifact, Dataset, DatasetRecord
from ..services.scheduler import simulate
from ..core.config import MODEL_DIR

def _workloads(records):
    groups={}
    for r in records:
        groups.setdefault(r.workload_id,[]).append({
            "pid":r.pid,"arrival_time":r.arrival_time,"burst_time":r.burst_time,"priority":r.priority
        })
    return list(groups.values())

def _make_training_data(records, w_accuracy=1, w_waiting=1):
    X=[]; y=[]
    workloads=_workloads(records)
    for ps in workloads:
        scores=[]
        for alg in ALGORITHMS:
            m=simulate(ps,alg)["metrics"]
            # Objective is a balanced synthetic label derived from actual scheduler outcomes,
            # so the model learns from the user's dataset workloads rather than a hardcoded label.
            score=w_waiting*m["average_waiting_time"] + w_accuracy*(100-m["cpu_utilization"])
            scores.append(score)
        label=ALGORITHMS[int(np.argmin(scores))]
        X.append(workload_features(ps)[0]); y.append(label)
    return np.asarray(X), np.asarray(y)

def train_job(job_id, req):
    db=SessionLocal()
    try:
        job=db.get(TrainingJob,job_id); job.status="running"; job.message="Loading dataset…"; db.commit()
        dataset=db.get(Dataset,req.dataset_id)
        records=db.query(DatasetRecord).filter(DatasetRecord.dataset_id==req.dataset_id).all()
        if not dataset or not records: raise ValueError("Selected dataset does not exist or contains no records.")
        X,y=_make_training_data(records,req.weight_accuracy,req.weight_waiting_time)
        job.message=f"Prepared {len(y)} workloads."; db.commit()
        if len(set(y))<2:
            raise ValueError("Training requires at least two distinct algorithm labels in the selected dataset.")
        test_size=min(max(req.test_size,1/len(y)),0.49)
        if len(y)<8:
            # Small PBL datasets cannot support a stratified split reliably.
            X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=test_size,random_state=req.random_state)
        else:
            X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=test_size,random_state=req.random_state,stratify=y)
        model=RandomForestClassifier(n_estimators=req.n_estimators,max_depth=req.max_depth,random_state=req.random_state,class_weight="balanced")
        model.fit(X_train,y_train)
        pred=model.predict(X_test)
        metrics={
            "training_accuracy":float(model.score(X_train,y_train)),
            "testing_accuracy":float(accuracy_score(y_test,pred)),
            "precision":float(precision_score(y_test,pred,average="weighted",zero_division=0)),
            "recall":float(recall_score(y_test,pred,average="weighted",zero_division=0)),
            "f1_score":float(f1_score(y_test,pred,average="weighted",zero_division=0)),
            "confusion_matrix":confusion_matrix(y_test,pred,labels=model.classes_).tolist(),
            "classes":model.classes_.tolist(),
            "feature_names":FEATURE_NAMES
        }
        metrics["feature_importance"]={k:float(v) for k,v in zip(FEATURE_NAMES,model.feature_importances_)}
        version=f"rf-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-{job_id}"
        path=MODEL_DIR/f"{version}.joblib"
        joblib.dump({"model":model,"version":version,"dataset_id":dataset.id,"dataset_name":dataset.name,"metrics":metrics,"feature_names":FEATURE_NAMES},path)
        artifact=ModelArtifact(version=version,dataset_id=dataset.id,path=str(path),metrics_json=metrics,feature_importance_json=metrics["feature_importance"])
        db.add(artifact)
        job.status="completed"; job.message="Model trained and persisted successfully."; job.metrics_json=metrics; job.model_version=version; job.completed_at=datetime.utcnow(); db.commit()
    except Exception as exc:
        job=db.get(TrainingJob,job_id)
        if job:
            job.status="failed"; job.message=str(exc); job.completed_at=datetime.utcnow(); db.commit()
    finally: db.close()

def start_training(req):
    db=SessionLocal()
    job=TrainingJob(dataset_id=req.dataset_id,status="queued",message="Training queued.")
    db.add(job); db.commit(); db.refresh(job); job_id=job.id; db.close()
    threading.Thread(target=train_job,args=(job_id,req),daemon=True).start()
    return job_id
