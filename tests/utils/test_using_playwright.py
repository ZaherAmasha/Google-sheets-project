import pytest
import os
import sys
import re

# Get the parent directory of the current file and add it to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(
    os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__), ".."), ".."))
)

from utils.using_playwright import (
    get_aliexpress_cookie_using_playwright,
    get_ishtari_cookie_using_playwright,
)
from websites_to_fetch_from.aliexpress_api import (
    fetch_aliexpress_product_recommendations,
)
from websites_to_fetch_from.ishtari_api import fetch_ishtari_product_recommendations
from models.products import OutputFetchedProducts
from utils.logger import logger


class MockIshtariCookie:
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


class MockAliexpressCookie:
    def __init__(self, cookie):
        self.cookie = cookie


# Setting the cookies to be none at the start of the test
MOCK_ALIEXPRESS_COOKIE = MockAliexpressCookie(cookie=None)
MOCK_ISHTARI_COOKIE = MockIshtariCookie(cookie=None)


@pytest.mark.skip(reason="Takes time to run")
@pytest.mark.asyncio
async def test_expired_AliExpress_cookie_scenario():
    """Test handling of expired AliExpress cookie, fetches a new cookie and checks if valid
    by fetching products with it.
    Keeping in mind that this test depends on the fetch_aliexpress_product_recommendations()
    function to be working"""
    logger.info("This is an info logger message")
    logger.debug("This is a debug logger message")

    MOCK_ALIEXPRESS_COOKIE.cookie = await get_aliexpress_cookie_using_playwright()

    # getting some products to check if the cookie is valid
    result = await fetch_aliexpress_product_recommendations(
        "black shoes", MOCK_ALIEXPRESS_COOKIE
    )

    assert isinstance(result, OutputFetchedProducts)
    logger.debug(
        f"This is the number of products fetched in the test: {len(result.product_names)}"
    )
    assert len(result.product_names) > 0


@pytest.mark.skip(reason="Takes time to run")
@pytest.mark.asyncio
async def test_expired_Ishtari_cookie_scenario():
    """Test handling of expired Ishtari cookie, fetches a new cookie and checks if valid
    by fetching products with it.
    Keeping in mind that this test depends on the fetch_ishtari_product_recommendations()
    function to be working"""

    MOCK_ISHTARI_COOKIE.cookie = await get_ishtari_cookie_using_playwright()

    # getting some products to check if the cookie is valid
    result = await fetch_ishtari_product_recommendations(
        "black shoes", MOCK_ISHTARI_COOKIE
    )

    assert isinstance(result, OutputFetchedProducts)
    logger.debug(
        f"This is the number of products fetched in the test: {len(result.product_names)}"
    )
    assert len(result.product_names) > 0
