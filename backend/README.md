# CPU Scheduling Visualizer — FastAPI Backend

This backend is a complete working FastAPI service for the supplied frontend.

## Windows PowerShell

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

# Optional: create demo dataset
python seed.py

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API docs:
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/redoc

## Backend capabilities

### Scheduling
- FCFS
- SJF
- SRTF
- Round Robin
- Preemptive Priority
- Non-preemptive Priority
- Actual Gantt timelines
- Waiting / turnaround / response metrics
- CPU utilization
- Throughput
- Context switches

### Dataset management
- Dataset creation
- Synthetic dataset generation
- CSV upload
- Excel upload
- Dataset listing/details
- Record CRUD
- Dataset deletion
- Dataset CSV download
- Persistent SQLite storage

### Machine learning
- User-selected dataset
- Random Forest training
- Background training jobs
- Training status polling
- Persistent `.joblib` model artifacts
- Accuracy / precision / recall / F1
- Confusion matrix
- Feature importance
- Training history
- Recommendation probabilities
- Model-not-trained error

## Database

SQLite is used by default at:

```text
backend/cpu_scheduler.db
```

Model artifacts are stored in:

```text
backend/storage/models/
```

Uploaded files can be stored in:

```text
backend/storage/uploads/
```

## Notes about ML labels

The training labels are not hardcoded algorithm recommendations. For each workload in the selected dataset, the backend actually executes the six scheduling algorithms and derives the best algorithm from the configured objective weights (waiting time and CPU utilization). The Random Forest then learns from those generated labels and predicts the best algorithm for new workloads.

This keeps the recommendation pipeline tied to the real scheduling engine and the user's selected dataset.
