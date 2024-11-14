import sys
import os

# Get the parent directory of the current file and add it to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.products import OutputFetchedProducts
from utils.logger import logger

import requests
import time
import json
from dotenv import load_dotenv
import traceback

load_dotenv()

ISHTARI_TOKEN = os.getenv("ISHTARI_TOKEN")


def _fetch_products(search_keyword, product_order_id):
    """Function that fetches products from ishtari.com. Due to how the website works (not sure why), not all first
    requests return product data (they would return that we already have the data cached). In which case,
    we do another request taking the type_id from the first response and add it as a query parameter
    'path' in the api url. type_id seems to be referring to discrete product groups which could mean that
    there's a finite number of possible results to be fetched on this website and it's not a dynamic process.
    """
    NUMBER_OF_PRODUCTS_TO_FETCH = 10

    # First request to get the redirect/cache info
    initial_url = f"https://www.ishtari.com/motor/v2/index.php?route=catalog/search&key={search_keyword}&limit={NUMBER_OF_PRODUCTS_TO_FETCH}&page=0"

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Authorization": f"Bearer {ISHTARI_TOKEN}",
        # "Authorization": f"Bearer d75ce26facce58a67378e89a23910a8e7ff940ea",  # Ishtari token seem to expire every 12 hours or so
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Cookie": f"__Host-next-auth.csrf-token=e6578cc1add6b9bd1a3b91e27576b9ae416c83a807ec23be8222e5e56fb4dec8%7Ca4c2c4d8eb05d7be1b34092b60b1bc9d016b7fd249c3b5e21536c044520f0f2a; __Secure-next-auth.callback-url=https%3A%2F%2Fwww.ishtari.com; api-token={ISHTARI_TOKEN}",
        # "Cookie": f"__Host-next-auth.csrf-token=231d03e9664f7b45242fe3cdd6ecb98a81af5f0d47315f4c864237bbdd9765fa%7C018ab6b3595fbd6385e4d2ddd1962345f55d1ec219558a6f2a2dcb3cc45c3d1d; __Secure-next-auth.callback-url=https%3A%2F%2Fwww.ishtari.com; api-token=d75ce26facce58a67378e89a23910a8e7ff940ea; _gcl_au=1.1.405635998.1731360359",
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
        # '__Host-next-auth.csrf-token=53733336ab32d9c486bb724fe1c24f0f8661ffe4788fadd9bd6eb8c85031bb0c%7Cae36fcd84a54abe446877e567381a9f9f4abe2981cf906f8e10d3b3259bbf97b; __Secure-next-auth.callback-url=https%3A%2F%2Fwww.ishtari.com'
        # First request to get redirect info
        response = session.get(initial_url, headers=headers)
        response.raise_for_status()
        logger.info(f"This is the initial response: {response}")
        initial_data = response.json()
        logger.info(f"This is the initial data: {initial_data}")
        # print("This is the initial data: ")
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
            response = session.get(product_url, headers=headers)
            response.raise_for_status()
            logger.info("This is the response: {response.text}")
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
        # logger.info(f"Returning no products from Ishtari: {e}\n{traceback.format_exc()}")
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


# print(f"Bearer {ISHTARI_TOKEN}")


def _process_product_data(product_data):
    """Process the received product data"""
    # if not product_data.get("success"):
    #     raise Exception("Failed to get product data")
    logger.info(f"This is the product_data: {product_data}")
    products = product_data.get("data", {}).get("products", [])

    processed_products = []
    for product in products:
        processed_product = {
            # "id": product.get("product_id"),
            "name": product.get("full_name"),
            "price": "US " + product.get("special"),
            # "url": product.get(
            #     "product_link"
            # ),  # For some reason, this doesn't always exist
            # manually constructing the product url using the name and product id
            # example: product_id="112115", name=" Breathable Woven Black Mesh Sneaker ", The product url would be: https://www.ishtari.com/Breathable-Woven-Black-Mesh-Sneaker/p=112115
            "manual_url": f"https://www.ishtari.com/{' '.join(product.get('name')[:-2].split()).replace(' ', '-')}/p={product.get('product_id')}",
        }
        logger.info(
            f"This is the original name before constructing the URL: {product.get('name')[:-2]}"
        )
        logger.info(
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


def fetch_ishtari_product_recommendations(search_keyword, product_order_id):
    return _process_product_data(_fetch_products(search_keyword, product_order_id))


if __name__ == "__main__":
    print(fetch_ishtari_product_recommendations("white shoes", 1))

# Usage example
# try:
#     product_data = fetch_ishtari_product_recommendations(
#         "white shoes", "1"
#     )
#     print("Finished calling the fetch function")
#     products = process_product_data(product_data)
#     print(f"Found {len(products.product_names)} products:")
#     for product in products:
#         print(f"- {product}")
# except Exception as e:
#     print(f"Error: {str(e)}")
