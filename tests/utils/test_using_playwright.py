import pytest
import os
import sys

# Get the parent directory of the current file and add it to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(
    os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__), ".."), ".."))
)

from websites_to_fetch_from.aliexpress_api import (
    fetch_aliexpress_product_recommendations,
)
from websites_to_fetch_from.ishtari_api import fetch_ishtari_product_recommendations
from models.products import OutputFetchedProducts
from utils.logger import logger

# pytest by default loads the conftest.py fixtures when the test files are being run. so there's no
# need for an explicit import of conftest.py. We are using here from it mock_aliexpress_cookie and
# mock_ishtari_cookie fixtures


# @pytest.mark.skip(reason="Takes time to run")
@pytest.mark.asyncio
async def test_expired_AliExpress_cookie_scenario(mock_aliexpress_cookie):
    """Test handling of expired AliExpress cookie, fetches a new cookie and checks if valid
    by fetching products with it.
    Keeping in mind that this test depends on the fetch_aliexpress_product_recommendations()
    function to be working"""

    # getting some products to check if the cookie is valid
    result = await fetch_aliexpress_product_recommendations(
        "black shoes", mock_aliexpress_cookie
    )

    assert isinstance(result, OutputFetchedProducts)
    logger.debug(
        f"This is the number of products fetched in the test: {len(result.product_names)}"
    )
    assert len(result.product_names) > 0


# @pytest.mark.skip(reason="Takes time to run")
@pytest.mark.asyncio
async def test_expired_Ishtari_cookie_scenario(mock_ishtari_cookie):
    """Test handling of expired Ishtari cookie, fetches a new cookie and checks if valid
    by fetching products with it.
    Keeping in mind that this test depends on the fetch_ishtari_product_recommendations()
    function to be working"""

    # getting some products to check if the cookie is valid
    result = await fetch_ishtari_product_recommendations(
        "black shoes", mock_ishtari_cookie
    )

    assert isinstance(result, OutputFetchedProducts)
    logger.debug(
        f"This is the number of products fetched in the test: {len(result.product_names)}"
    )
    assert len(result.product_names) > 0
