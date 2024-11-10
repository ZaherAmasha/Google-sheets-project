from fastapi import FastAPI, Header, HTTPException
import uvicorn
from dotenv import load_dotenv
import os
import time

from aliexpress_api import fetch_aliexpress_product_recommendations
from models.fastapi_endpoints import SheetUpdate
from logger import logger

load_dotenv()

app = FastAPI()

SHARED_SECRET = os.getenv("SHARED_SECRET")


@app.get("/health")
async def read_root():
    logger.info("Health check endpoint was accessed")
    return {"Hello": "World"}


@app.post("/trigger_product_fetch")
async def update_recommended_products(
    update: SheetUpdate, authorization: str = Header(None)
):
    try:
        logger.info("Starting product fetch")
        # Validate the shared secret
        if authorization != f"Bearer {SHARED_SECRET}":
            logger.exception("Incorrect SHARED_SECRET")
            raise HTTPException(status_code=401, detail="Unauthorized")

        keywords = update.keywords
        logger.info(f"keywords: {keywords}")
        # dropping the empty keywords
        keywords = [keyword for keyword in keywords if keyword.strip()]
        logger.info(f"filtered keywords: {keywords}")
        for product_order_id, keyword in enumerate(keywords):
            if fetch_aliexpress_product_recommendations(
                keyword, product_order_id + 1
            ):  # the +1 is because it starts from 0
                logger.info("Fetching products from AliExpress went well")
                time.sleep(2)
            else:
                logger.error("Something went bad when fetching products")
                return "Something went bad when fetching products"

        return "Fetching products from AliExpress went well"
    except Exception as e:
        logger.exception(f"The exception printed: {e}")
        raise HTTPException(status_code=500, detail=f"This is the exception: {e}")


logger.info("Launched the server")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
