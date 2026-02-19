from fastapi import FastAPI

app = FastAPI()


@app.get("/api/v1")
def hello():
    return {"message": "hello world"}
