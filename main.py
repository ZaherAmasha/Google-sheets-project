from fastapi import FastAPI
import uvicorn

app = FastAPI()


@app.post("/")
def read_root():
    return {"Hello": "World"}


print("Launched the server")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
