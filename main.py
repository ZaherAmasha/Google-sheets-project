from fastapi import FastAPI
import uvicorn

from aliexpress_api import fetch_aliexpress_product_recommendations

app = FastAPI()


@app.get("/health")
def read_root():
    return {"Hello": "World"}


@app.post("/trigger_product_fetch")
def update_recommended_products():
    if fetch_aliexpress_product_recommendations("black shoes"):
        print("Fetching products from AliExpress went well")
    else:
        print("Something went bad when fetching products")


print("Launched the server")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
