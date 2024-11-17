import sys
import os

# Get the parent directory of the current file and add it to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.products import OutputFetchedProducts
from utils.logger import logger
from utils.api_utils import ISHTARI_COOKIE
from utils.using_playwright import get_ishtari_cookie_using_playwright

import requests
import time
import json
import traceback
import asyncio


async def get_ishtari_cookie_using_playwright_async_wrapper():
    cookie = await get_ishtari_cookie_using_playwright()
    return cookie


async def _fetch_products(search_keyword):
    """Function that fetches products from ishtari.com. Due to how the website works (not sure why), not all first
    requests return product data (they would return that we already have the data cached). In which case,
    we do another request taking the type_id from the first response and add it as a query parameter
    'path' in the api url. type_id seems to be referring to discrete product groups which could mean that
    there's a finite number of possible results to be fetched on this website and it's not a dynamic process.
    """
    NUMBER_OF_PRODUCTS_TO_FETCH = 10

    # First request to get the redirect/cache info
    initial_url = f"https://www.ishtari.com/motor/v2/index.php?route=catalog/search&key={search_keyword}&limit={NUMBER_OF_PRODUCTS_TO_FETCH}&page=0"

    if (
        ISHTARI_COOKIE.cookie is None
    ):  # Ishtari cookie has not been set yet, this statement is only entered at the first use of this fetch function
        # fetch a new Ishtari cookie
        ISHTARI_COOKIE.cookie = await get_ishtari_cookie_using_playwright()
    else:
        logger.info("Ishtari cookie is present, no need to fetch a new one")

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Authorization": f"Bearer {ISHTARI_COOKIE.get_api_token()}",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Cookie": ISHTARI_COOKIE.cookie,
        "Referer": f"https://www.ishtari.com/search?keyword={search_keyword}",
        "Sec-Ch-Ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Linux"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    }

    try:
        # using a session maintains cookies across different requests
        session = requests.Session()
        # First request to get redirect info
        response = session.get(initial_url, headers=headers)

        # Check for expired cookie, in which case the response would be that the api request is unauthorized
        if response.status_code == 401:
            logger.info("Cookie expired, fetching a new one.")
            ISHTARI_COOKIE.cookie = asyncio.run(get_ishtari_cookie_using_playwright())
            headers["Cookie"] = ISHTARI_COOKIE.cookie  # Update with new cookie
            headers["Authorization"] = f"Bearer {ISHTARI_COOKIE.get_api_token()}"

            # Retry the initial request with a new cookie
            response = session.get(initial_url, headers=headers)

        response.raise_for_status()
        initial_data = response.json()
        logger.debug(f"This is the initial data: {initial_data}")

        if not initial_data.get("success"):
            raise Exception(f"Initial request failed: {response.text}")
        # with open("ishtari_response.txt", "w") as output:
        #     output.write(str(response.json()).replace("'", '"'))

        # If we got a redirect, make the second request
        if initial_data["data"].get("redirect") == "1":
            logger.info("trying the fetch again")
            # a failed first request looks like: {"success":true,"data":{"redirect":"1","type":"category","type_id":"4006","is_cache":true}}
            type_id = initial_data["data"].get("type_id")

            # Construct the new URL for the actual product data. We assign the type id in the url, following how the website handles these redirects
            product_url = f"https://www.ishtari.com/motor/v2/index.php?route=catalog/category&path={type_id}&source_id=1&limit={NUMBER_OF_PRODUCTS_TO_FETCH}"

            # Add cache-busting parameters. Although the second call works without them, I'm keeping them.
            headers.update(
                {
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0",
                }
            )

            # Small delay to prevent rate limiting
            time.sleep(2)

            # Making the second request
            response = requests.get(product_url, headers=headers)

            # response.raise_for_status()
            logger.debug(f"This is the response: {response.text}")
            logger.debug(
                f"This is the products list: {response.json().get('data', {}).get('products', [])}"
            )
            # if there are no products to show at the page, raise an exception so that the except block would catch it and return no products found
            if len(response.json().get("data", {}).get("products", [])) == 0:
                raise Exception("No products found in the response")

            try:
                product_data = response.json()
                return product_data
            except json.JSONDecodeError:
                logger.error("Failed to decode JSON response:")
                logger.error(response.text)
                raise
        else:
            # If no redirect, return the initial data
            return initial_data
    except Exception as e:
        logger.error(
            f"Returning no products from Ishtari: {e}\n{traceback.format_exc()}"
        )
        return {
            "data": {
                "products": [
                    {
                        "product_id": "null",
                        "full_name": "No matched products from Ishtari.com",
                        "name": "No matched products from Ishtari.com",
                        "special": "",
                    }
                ]
            }
        }


async def _process_product_data(product_data):
    """Process the received product data"""

    logger.debug(f"This is the product_data: {product_data}")
    products = product_data.get("data", {}).get("products", [])

    processed_products = []
    for product in products:
        processed_product = {
            "name": product.get("full_name"),
            "price": "US " + product.get("special"),
            # "url": product.get(
            #     "product_link"
            # ),  # For some reason, this doesn't always exist
            # manually constructing the product url using the name and product id
            # example: product_id="112115", name=" Breathable Woven Black Mesh Sneaker ", The product url would be: https://www.ishtari.com/Breathable-Woven-Black-Mesh-Sneaker/p=112115
            "manual_url": f"https://www.ishtari.com/{' '.join(product.get('name')[:-2].split()).replace(' ', '-')}/p={product.get('product_id')}",
        }
        logger.debug(
            f"This is the original name before constructing the URL: {product.get('name')[:-2]}"
        )
        logger.debug(
            f"This is the name after constructing the URL: {product.get('name')[:-2].replace(' ', '-')}"
        )
        processed_products.append(processed_product)

    output_products = OutputFetchedProducts(
        product_names=[product["name"] for product in processed_products],
        product_urls=[product["manual_url"] for product in processed_products],
        product_prices=[product["price"] for product in processed_products],
        website_source=["Ishtari" for _ in range(len(processed_products))],
    )
    return output_products


async def fetch_ishtari_product_recommendations(search_keyword):
    return await _process_product_data(await _fetch_products(search_keyword))


if __name__ == "__main__":
    print(asyncio.run(fetch_ishtari_product_recommendations("black shoes")))
    # time.sleep(2)
    # print(fetch_ishtari_product_recommendations("black shoes"))
