from app.db import Base, engine, SessionLocal
from app.models import Dataset, DatasetRecord

Base.metadata.create_all(bind=engine)
db=SessionLocal()
if db.query(Dataset).count()==0:
    d=Dataset(name="Demo Workloads",version="1.0",source_filename="seed")
    db.add(d);db.flush()
    rows=[
        ("P1",0,7,2,"w1"),("P2",2,4,1,"w1"),("P3",4,1,3,"w1"),
        ("P1",0,3,2,"w2"),("P2",1,8,1,"w2"),("P3",2,2,3,"w2"),("P4",5,4,2,"w2"),
        ("P1",0,5,1,"w3"),("P2",0,2,3,"w3"),("P3",3,6,2,"w3"),("P4",5,1,1,"w3")
    ]
    for pid,a,b,p,w in rows: db.add(DatasetRecord(dataset_id=d.id,pid=pid,arrival_time=a,burst_time=b,priority=p,workload_id=w))
    db.commit()
print("Seed complete.")
