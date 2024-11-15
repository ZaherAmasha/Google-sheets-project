import requests
import os
from bs4 import BeautifulSoup
import re
import sys
import asyncio

# Get the parent directory of the current file and add it to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.logger import logger
from utils.using_playwright import get_aliexpress_cookie_using_playwright
from utils.api_utils import ALIEXPRESS_COOKIE
from models.products import OutputFetchedProducts


async def fetch_aliexpress_product_recommendations(
    search_keyword,
) -> OutputFetchedProducts:

    url = f"https://www.aliexpress.com/w/wholesale-{search_keyword}.html"  # ?spm=a2g0o.productlist.search.0"

    if (
        ALIEXPRESS_COOKIE.cookie is None
    ):  # ALiExpress cookie has not been set yet, this statement is only entered at the first use of this fetch function
        # fetch a new AliExpress cookie
        ALIEXPRESS_COOKIE.cookie = await get_aliexpress_cookie_using_playwright()
    else:
        logger.info("AliExpress cookie is present, no need to fetch a new one")

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "max-age=0",
        "Cookie": ALIEXPRESS_COOKIE.cookie,
        "Priority": "u=0, i",
        "Origin": "https://www.aliexpress.com",
        "Referer": f"https://www.aliexpress.com/w/wholesale-{search_keyword}.html?spm=a2g0o.home.history.1.9d5f76dbxo1lT7",
        "Sec-Ch-Ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Linux"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Site": "same-origin",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    }
    response = requests.request("GET", url, headers=headers, timeout=180)

    # Couldn't manage to make the Aliexpress cookie expire, but I've added the following statement just in case it expires
    # Check for expired cookie, in which case the response would be that the api request is unauthorized
    if response.status_code == 401:  # unauthorized
        logger.info("Cookie expired, fetching a new one.")
        ALIEXPRESS_COOKIE.cookie = asyncio.run(get_aliexpress_cookie_using_playwright())
        headers["Cookie"] = ALIEXPRESS_COOKIE.cookie  # Update with new cookie

        # Retry the initial request with a new cookie
        response = requests.request("GET", url, headers=headers, timeout=180)

    response.raise_for_status()  # to raise an exception when an exception happens, for debugging purposes. Without it, the response may be invalid and we wouldn't know immeadiately

    soup = BeautifulSoup(response.text, "html.parser")

    # fetching the titles
    titles = soup.find_all("div", class_="multi--title--G7dOCj3")
    logger.info(f"found {len(titles)} titles")
    for title in titles:
        logger.info(f"Title: {title.get_text(strip=True)}")

    # fetching the urls for the individual products
    product_urls = soup.find_all(
        "a",
        class_=re.compile(
            r"multi--container--1UZxxHY cards--card--3PJxwBm (cards--list--2rmDt5R )?search-card-item"
        ),
    )

    logger.info(f"found {len(product_urls)} product urls")
    titles = [title.get_text(strip=True) for title in titles]
    product_urls = [
        ("https:" + product_url.get("href").strip()) for product_url in product_urls
    ]

    prices = soup.find_all("div", class_="multi--price-sale--U-S0jtj")
    logger.info(f"Found {len(prices)} prices")
    for price in prices:
        logger.info(f"These are the prices: {price.get_text(strip=True)}")
    prices = [price.get_text(strip=True) for price in prices]

    return OutputFetchedProducts(
        product_names=list(titles),
        product_urls=list(product_urls),
        product_prices=list(prices),
        website_source=["AliExpress" for _ in range(len(titles))],
    )


# examples:
if __name__ == "__main__":
    print(asyncio.run(fetch_aliexpress_product_recommendations("white shoes")))
