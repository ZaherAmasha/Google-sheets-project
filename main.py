from fastapi import FastAPI, Header, HTTPException
import uvicorn
from dotenv import load_dotenv
import os
import time
import asyncio
from typing import Dict
import sys

# Get the parent directory of the current file and add it to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from websites_to_fetch_from.aliexpress_api import (
    fetch_aliexpress_product_recommendations,
)

# from websites_to_fetch_from.ishtari_api import
from models.fastapi_endpoints import SheetUpdate
from utils.utils import remove_elements_with_whitespaces_and_empty_from_list
from utils.api_utils import check_shared_secret_validity
from utils.sheet_utils import (
    signal_end_of_product_retrieval,
    update_spreadsheet_with_fetched_products,
)
from utils.logger import logger

load_dotenv()

app = FastAPI()

SHARED_SECRET = os.getenv("SHARED_SECRET")


@app.get("/health")
async def read_root():
    logger.info("Health check endpoint was accessed")
    return {"Hello": "World"}


# Store active fetch tasks and cancellation flags for each task
active_tasks: Dict[str, asyncio.Task] = {}
cancel_flags: Dict[str, bool] = {}


async def fetch_products_async(task_id: str, keywords: list):
    """
    A async wrapper on top of the fetch_aliexpress_product_recommendations() function so that
    we can cancel the product fetch when we want by canceling the async task associated with it
    """
    try:
        cancel_flags[task_id] = False
        keywords = remove_elements_with_whitespaces_and_empty_from_list(keywords)
        logger.info(f"filtered keywords: {keywords}")

        for product_order_id, keyword in enumerate(keywords):
            # Check if cancellation was requested
            if cancel_flags[task_id]:
                logger.info(f"Task {task_id} was cancelled")
                return False
            update_spreadsheet_with_fetched_products(
                fetch_aliexpress_product_recommendations(keyword, product_order_id + 1),
                product_order_id + 1,
            )
            logger.info(
                f"Successfully fetched products from AliExpress for keyword: {keyword}"
            )
            await asyncio.sleep(
                2
            )  # Using asyncio.sleep instead of time.sleep since we are dealing with concurrency now

            # if fetch_aliexpress_product_recommendations(keyword, product_order_id + 1):
            #     logger.info(f"Successfully fetched products for keyword: {keyword}")
            #     await asyncio.sleep(
            #         2
            #     )  # Using asyncio.sleep instead of time.sleep since we are dealing with concurrency now
            # else:
            #     logger.error(f"Failed to fetch products for keyword: {keyword}")
            #     return False
        # signify end of product retrieval by updating the status cell in sheet 1
        if not signal_end_of_product_retrieval():
            return False
        return True

    except Exception as e:
        logger.exception(f"Error in fetch_products_async: {e}")
        return False
    finally:
        # Cleanup
        if task_id in active_tasks:
            del active_tasks[task_id]
        if task_id in cancel_flags:
            del cancel_flags[task_id]


@app.post("/trigger_product_fetch")
async def update_recommended_products(
    update: SheetUpdate, authorization: str = Header(None)
):
    """This endpoint serves as a trigger to start the product fetch. It returns the async task ID instead
    of it blocking the program and making the client wait for the product fetch to finish to get a response.
    This task ID is used on the client side to trigger the cancellation endpoint if need be, and cancel the
    particular task with this task ID"""
    try:
        logger.info("Starting product fetch")
        # Validate the shared secret
        check_shared_secret_validity(authorization, SHARED_SECRET)

        # Generates a unique task ID every time
        task_id = str(int(time.time()))

        # Create and store the task
        task = asyncio.create_task(fetch_products_async(task_id, update.keywords))
        active_tasks[task_id] = task

        return {"message": "Product fetch started", "task_id": task_id}

        # keywords = update.keywords
        # logger.info(f"keywords: {keywords}")
        # # dropping the empty keywords
        # keywords = remove_elements_with_whitespaces_and_empty_from_list(keywords)

        # logger.info(f"filtered keywords: {keywords}")
        # for product_order_id, keyword in enumerate(keywords):
        #     if fetch_aliexpress_product_recommendations(
        #         keyword, product_order_id + 1
        #     ):  # the +1 is because it starts from 0
        #         logger.info("Fetching products from AliExpress went well")
        #         time.sleep(2)
        #     else:
        #         logger.error("Something went bad when fetching products")
        #         return "Something went bad when fetching products"

        # return "Fetching products from AliExpress went well"
    except Exception as e:
        logger.exception(f"The exception printed: {e}")
        raise HTTPException(status_code=500, detail=f"This is the exception: {e}")


@app.post("/cancel_product_fetch")
async def cancel_fetching_recommended_products(authorization: str = Header(None)):
    try:
        # Validate the shared secret
        check_shared_secret_validity(authorization, SHARED_SECRET)

        # Get the most recent task (if any)
        if not active_tasks:
            raise HTTPException(
                status_code=404, detail="No active product fetch to cancel"
            )

        task_id = list(active_tasks.keys())[-1]

        # Set cancellation flag
        cancel_flags[task_id] = True

        logger.info(f"Cancelling task {task_id}")
        return {"message": "Product fetch cancellation requested", "task_id": task_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error in cancel_product_fetch: {e}")
        raise HTTPException(status_code=500, detail=f"This is the exception: {e}")


@app.get("/fetch_status")
async def get_fetch_status(authorization: str = Header(None)):
    check_shared_secret_validity(authorization, SHARED_SECRET)

    return {
        task_id: {
            "running": not task.done(),
            "cancelled": cancel_flags.get(task_id, False),
        }
        for task_id, task in active_tasks.items()
    }


logger.info("Launched the server")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
