from fastapi import HTTPException

from utils.logger import logger


def check_shared_secret_validity(authorization, SHARED_SECRET):
    logger.info(f"This is the authorization header: {authorization}")
    logger.info(f"And this is the shared secret: {SHARED_SECRET}")
    if authorization != f"Bearer {SHARED_SECRET}":
        logger.exception("Incorrect SHARED_SECRET")
        raise HTTPException(status_code=401, detail="Unauthorized")
