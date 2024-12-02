import sys
import os
from dotenv import load_dotenv

load_dotenv()

USE_ROTATING_IPS_WITH_SCRAPERAPI = bool(
    os.getenv("USE_ROTATING_IPS_WITH_SCRAPERAPI").strip()
)
SCRAPERAPI_KEY = os.getenv("SCRAPERAPI_KEY")

# Get the parent directory of the current file and add it to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.logger import logger

from playwright.async_api import async_playwright
from time import time


async def get_aliexpress_cookie_using_playwright():
    start_time = time()
    logger.info("Fetching the AliExpress Cookie using Playwright")
    async with async_playwright() as p:
        # Launch chrome browser
        if USE_ROTATING_IPS_WITH_SCRAPERAPI:
            proxy = {
                # need to include the country_code to be 'US' here, firstly to get the desired results and secondly
                # it appears to be the fastest proxy server
                "server": f"http://scraperapi.country_code=us:{SCRAPERAPI_KEY}@proxy-server.scraperapi.com:8001",
                "username": "scraperapi",
                "password": SCRAPERAPI_KEY,
            }

            browser = await p.chromium.launch(headless=True, proxy=proxy)

            # Open a new browser context (isolated session).
            context = await browser.new_context(
                proxy=proxy,
            )
        else:
            browser = await p.chromium.launch(headless=True)

            # Even though I'm setting the location to be US it's not working
            context = await browser.new_context(
                geolocation={
                    "latitude": 37.7749,
                    "longitude": -122.4194,
                },  # San Francisco, USA
                locale="en-US",  # English locale
                timezone_id="America/Los_Angeles",  # U.S. Pacific Timezone
            )
        # Open a new page
        page = await context.new_page()

        # Navigate to the main URL
        await page.goto("http://aliexpress.com", timeout=300000)  # in millisecond

        cookie_for_requests = await context.cookies("https://aliexpress.com")

        # Close the browser
        await browser.close()

        print("Process finished")
        cookie = ""
        for item in cookie_for_requests:

            cookie = cookie + f"{item['name']}={item['value']}; "

        # changing the language from Arabic to English and changing the location to the US/international
        cookie = (
            cookie.strip()[:-1]
            .replace("region=LB&site=ara", "site=glo&province=&city=")
            .replace("aep_usuc_f=site=ara", "aep_usuc_f=site=glo&province=&city=")
            .replace("x_locale=ar_MA", "x_locale=en_US")
            .replace("intl_locale=ar_MA", "intl_locale=en_US")
            .replace("b_locale=ar_MA", "b_locale=en_US")
            .replace("c_tp=LBP", "c_tp=USD")
            .replace(
                "site=glo&c_tp=SGD&region=SG",
                "site=glo&province=&city=&c_tp=USD&region=LB",
            )  # this is because playwright is picking up on Singapore when deployed on render
        )
        logger.info(
            f"Getting the AliExpress Cookie using Playwright took: {time()-start_time}"
        )
        return cookie


async def get_ishtari_cookie_using_playwright():
    start_time = time()
    logger.info("Fetching the Ishtari Cookie using Playwright")
    async with async_playwright() as p:
        # Launch chrome browser
        if USE_ROTATING_IPS_WITH_SCRAPERAPI:
            logger.debug(
                "Fetching the Ishtari cookie using rotating IPs with ScraperAPI"
            )
            proxy = {
                # need to include the country_code to be 'US' here, firstly to get the desired results and secondly
                # it appears to be the fastest proxy server
                "server": f"http://scraperapi.country_code=us:{SCRAPERAPI_KEY}@proxy-server.scraperapi.com:8001",
                "username": "scraperapi",
                "password": SCRAPERAPI_KEY,
            }
            browser = await p.chromium.launch(headless=True, proxy=proxy)

            # Open a new browser context (isolated session).
            context = await browser.new_context(proxy=proxy, ignore_https_errors=True)
        else:
            logger.debug(
                "Fetching the Ishtari cookie without using rotating IPs using ScraperAPI"
            )
            browser = await p.chromium.launch(headless=True)

            # Open a new browser context (isolated session).
            # Even though I'm setting the location to be US, it's not working
            context = await browser.new_context(
                geolocation={
                    "latitude": 37.7749,
                    "longitude": -122.4194,
                },  # San Francisco, USA
                locale="en-US",  # English locale
                timezone_id="America/Los_Angeles",  # U.S. Pacific Timezone
            )

        # Open a new page
        page = await context.new_page()

        # Navigate to the main URL
        await page.goto("https://www.ishtari.com", timeout=200000)  # in millisecond
        # tm.sleep(100)
        await page.wait_for_load_state(
            "networkidle", timeout=400000
        )  # Wait until the page is fully loaded, otherwise we would get no cookies

        cookie_for_requests = await context.cookies("https://www.ishtari.com")
        logger.debug(f"These are the cookies from Ishtari.com: {cookie_for_requests}")

        # Close the browser
        await browser.close()

        logger.info("Process finished")
        # same process as the AliExpress cookie
        cookie = ""
        for item in cookie_for_requests:
            cookie = cookie + f"{item['name']}={item['value']}; "
        cookie = cookie.strip()[:-1]
        logger.info(
            f"Getting the Ishtari cookie using Playwright took: {time()-start_time}"
        )
        logger.debug(f"This is the Ishtari cookie: {cookie}")
        return cookie


# Run the Playwright function
# response = get_aliexpress_cookie_using_playwright()
# print("this is the cookie: ", response)
# with open("playwright_response.txt", "w") as output:
#     output.write(str(response))


# Define the entry point
# async def main():
#     cookies = await get_ishtari_cookie_using_playwright()
#     print("Cookies fetched:", cookies)


# asyncio.run(main())
