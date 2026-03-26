from fastapi import FastAPI
from .tasks import master_fetch_task

app = FastAPI(title="Automation API")

@app.post("/run-automation", status_code=202)
async def run_automation():
    task = master_fetch_task.delay()
    return {
        "task_id": task.id,
        "message": "User sync started in background"
    }

@app.get("/")
async def root():
    return {"message": "API is running. POST to /run-automation to start automation."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)