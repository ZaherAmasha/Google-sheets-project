import pytest
import os
import sys

# Get the parent directory of the current file and add it to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(
    os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__), ".."), ".."))
)

from models.products import OutputFetchedProducts
from websites_to_fetch_from.hicart_api import fetch_hicart_product_recommendations
from utils.logger import logger


# Testing the fetch_aliexpress_product_recommendations and fetch_ishtari_product_recommendations
# functions require a valid cookie. And We already have a test for the validity of the fetched
# cookies using playwright that also calls the above methods. So there's no need for seperate
# tests for the two above methods because they are inter-related with the cookie fetch functions.
# But this is not the case for the HiCart function because it doesn't require a cookie.


# @pytest.mark.skip(reason="Takes time to run")
@pytest.mark.asyncio
async def test_hicart_product_fetch():
    """Test the validity of retrieved products from HiCart"""

    # getting some products to check if the function is working
    result = await fetch_hicart_product_recommendations("black shoes")

    assert isinstance(result, OutputFetchedProducts)
    logger.debug(
        f"This is the number of products fetched in the test: {len(result.product_names)}"
    )

    assert len(result.product_names) > 0
