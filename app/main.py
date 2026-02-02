from fastapi import FastAPI

app = FastAPI(
    title="Python Backend Case Study",
    description="API for Case Study",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Service is up and running"}
