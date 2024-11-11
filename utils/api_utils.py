from fastapi import HTTPException

from logger import logger


def check_shared_secret_validity(authorization, SHARED_SECRET):
    if authorization != f"Bearer {SHARED_SECRET}":
        logger.exception("Incorrect SHARED_SECRET")
        raise HTTPException(status_code=401, detail="Unauthorized")
