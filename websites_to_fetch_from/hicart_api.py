import os
from bs4 import BeautifulSoup
import sys
import asyncio
import traceback
from dotenv import load_dotenv

load_dotenv()

USE_ROTATING_IPS_WITH_SCRAPERAPI = bool(
    os.getenv("USE_ROTATING_IPS_WITH_SCRAPERAPI").strip()
)

# Get the parent directory of the current file and add it to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.logger import logger
from models.products import OutputFetchedProducts
from using_scraper_api import get_request_using_cloudscraper_with_scraperapi

import cloudscraper

# Doesn't require a cookie to fetch the needed product data from HiCart


async def fetch_hicart_product_recommendations(
    search_keyword: str,
) -> OutputFetchedProducts:
    # cloudscraper is designed specifically to bypass cloudflare protection, which is the case with hicart.com. Clouflare picks up on bot behaviour
    # and cloudscraper tries to mimick browser behaviour like handling JavaScript related tasks
    scraper = cloudscraper.create_scraper()

    # turning multi-word search keywords into %20 notation
    search_keyword = search_keyword.strip().replace(" ", "%20")

    url = f"https://www.hicart.com/catalogsearch/result/?q={search_keyword}"

    try:
        # no need to define the headers here because cloudscraper defines them automatically. And there's no needed cookie
        # by hicart.com to call this endpoint and fetch product data. I think it mainly relies on cloudflare for protection.
        if USE_ROTATING_IPS_WITH_SCRAPERAPI:
            response = get_request_using_cloudscraper_with_scraperapi(
                cloudscraper=scraper, url=url
            )
        else:
            response = scraper.get(url)

        # with open("hicart_response.txt", "w") as output:
        #     output.write(response.text)

        response.raise_for_status()  # to raise an exception when an exception happens, for debugging purposes. Without it, the response may be invalid and we wouldn't know immeadiately

        soup = BeautifulSoup(response.text, "html.parser")

        # getting the titles
        product_names = soup.find_all("h2", class_="product-name")
        # only the first 10 or less
        if len(product_names) > 10:
            product_names = product_names[:10]
        titles = [product.a.get_text(strip=True) for product in product_names]

        # getting the product urls
        product_urls = [product.a.get("href") for product in product_names]

        logger.debug(f"These are the fetched titles: {titles}\n")
        logger.debug(f"These are the fetched product urls: {product_urls}\n")
        logger.debug(f"This is the number of fetched products: {len(product_names)}")

        # getting the product prices.
        price_boxes_with_discount = soup.find_all("div", class_="price-box")
        price_boxes_without_discount = soup.find_all("div", class_="price-box-min")
        logger.debug(
            f"This is the number of fetched price boxes with discount: {len(price_boxes_with_discount)}"
        )
        logger.debug(
            f"This is the number of fetched price boxes without discount: {len(price_boxes_without_discount)}"
        )

        # checking if the price is original or if there's a discount, the extraction differs for each case
        prices_with_discount = [
            "US "
            + (
                price.find("p", class_="special-price")
                .find("span", class_="price")
                .get_text(strip=True)  # gets the discounted price
                if price.find("p", class_="special-price")
                else price.find("span", class_="regular-price")
                .find("span", class_="price")
                .get_text(strip=True)  # gets the regular price
            )
            for price in price_boxes_with_discount
        ]

        prices_without_discount = [
            "US " + (price.find("p", class_="minimal-price").get_text(strip=True))
            for price in price_boxes_without_discount
        ]
        # concatenating the prices with and without discount together with more emphasis on the ones with discount
        prices = prices_with_discount + prices_without_discount

        logger.debug(f"These are the prices with discount: {prices_with_discount}")
        logger.debug(
            f"These are the prices without discount: {prices_without_discount}"
        )
        logger.info(
            f"This is the number of fetched products from HiCart: {len(prices)}"
        )

        # only the first 10 or less
        if len(prices) > 10:
            prices = prices[:10]

        # if no products are returned, rout the code to return the default no products found
        if len(prices) == 0:
            raise Exception("No products were found in the response from HiCart")

    except Exception as e:
        logger.info(f"Returning no products from HiCart: {e}\n{traceback.format_exc()}")
        titles = ["No matched products from HiCart.com"]
        product_urls = ["https://www.HiCart.com/No-matched-products-from-HiCart"]
        prices = ["US"]

    return OutputFetchedProducts(
        product_names=list(titles),
        product_urls=list(product_urls),
        product_prices=list(prices),
        website_source=["HiCart" for _ in range(len(titles))],
    )


# examples:
if __name__ == "__main__":
    print(asyncio.run(fetch_hicart_product_recommendations("wrist band")))
