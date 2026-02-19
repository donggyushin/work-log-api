from fastapi import FastAPI

app = FastAPI()


@app.get("/api/v1")
async def hello():
    return {"message": "hello world"}
