from fastapi import FastAPI, Header, HTTPException
import uvicorn
from dotenv import load_dotenv
import os

from aliexpress_api import fetch_aliexpress_product_recommendations

load_dotenv()

app = FastAPI()

SHARED_SECRET = os.getenv("SHARED_SECRET")


@app.get("/health")
def read_root():
    return {"Hello": "World"}


@app.post("/trigger_product_fetch")
def update_recommended_products(authorization: str = Header(None)):
    # Validate the shared secret
    if authorization != f"Bearer {SHARED_SECRET}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    if fetch_aliexpress_product_recommendations("black shoes"):
        print("Fetching products from AliExpress went well")
        return "Fetching products from AliExpress went well"
    else:
        print("Something went bad when fetching products")
        return "Something went bad when fetching products"


print("Launched the server")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
