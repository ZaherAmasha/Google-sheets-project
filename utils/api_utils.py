from fastapi import HTTPException
import re

from utils.logger import logger


def check_shared_secret_validity(authorization, SHARED_SECRET):
    logger.debug(f"This is the authorization header: {authorization}")
    logger.debug(f"And this is the shared secret: {SHARED_SECRET}")
    if authorization != f"Bearer {SHARED_SECRET}":
        logger.exception("Incorrect SHARED_SECRET")
        raise HTTPException(status_code=401, detail="Unauthorized")


class IshtariCookie:
    def __init__(self, cookie):
        self.cookie = cookie

    def get_api_token(self):
        # extracting the api_token parameter from the cookie, it's needed as a seperate auth header
        pattern = r"api-token=([^;]+)"
        if self.cookie:
            match = re.search(pattern, self.cookie)

            if match:
                api_token = match.group(1)
                logger.debug(
                    f"This is the api_token extracted from the Ishtari cookie: {api_token}"
                )
                return api_token
            else:
                logger.info("api-token not found in the Ishtari cookie")
                return None
        else:
            logger.info("Ishtari cookie has not been set yet")
            return None


class AliexpressCookie:
    def __init__(self, cookie):
        self.cookie = cookie


# Setting the cookies to be none at the start of the server
ALIEXPRESS_COOKIE = AliexpressCookie(cookie=None)
ISHTARI_COOKIE = IshtariCookie(cookie=None)
