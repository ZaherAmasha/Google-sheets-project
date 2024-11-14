from fastapi import HTTPException
import re

from utils.logger import logger


def check_shared_secret_validity(authorization, SHARED_SECRET):
    logger.info(f"This is the authorization header: {authorization}")
    logger.info(f"And this is the shared secret: {SHARED_SECRET}")
    if authorization != f"Bearer {SHARED_SECRET}":
        logger.exception("Incorrect SHARED_SECRET")
        raise HTTPException(status_code=401, detail="Unauthorized")


class IshtariCookie:
    def __init__(self, cookie):
        self.cookie = cookie

    def get_api_token(self):
        # extracting the api_token parameter from the cookie
        pattern = r"api-token=([^;]+)"
        if self.cookie:
            match = re.search(pattern, self.cookie)

            if match:
                api_token = match.group(1)
                logger.info(
                    f"This is the api_token extracted from the Ishtari cookie: {api_token}"
                )
                return api_token
            else:
                logger.info("api-token not found in the Ishtari cookie")
                return None
        else:
            logger.info("Ishtari cookie has not been set yet")
            return None


ISHTARI_COOKIE = IshtariCookie(cookie=None)
