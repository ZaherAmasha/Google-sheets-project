from fastapi import FastAPI, Header, HTTPException
import uvicorn
from dotenv import load_dotenv
import os

from aliexpress_api import fetch_aliexpress_product_recommendations
from models.fastapi_endpoints import SheetUpdate

load_dotenv()

app = FastAPI()

SHARED_SECRET = os.getenv("SHARED_SECRET")


@app.get("/health")
async def read_root():
    return {"Hello": "World"}


@app.post("/trigger_product_fetch")
async def update_recommended_products(
    update: SheetUpdate, authorization: str = Header(None)
):
    # Validate the shared secret
    if authorization != f"Bearer {SHARED_SECRET}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    keyword = update.keyword
    cell_range = update.range
    print("keyword and cell_range: ", keyword, " ", cell_range)

    if fetch_aliexpress_product_recommendations(keyword):
        print("Fetching products from AliExpress went well")
        return "Fetching products from AliExpress went well"
    else:
        print("Something went bad when fetching products")
        return "Something went bad when fetching products"


print("Launched the server")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
