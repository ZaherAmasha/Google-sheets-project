from utils.logger import logger

from playwright.async_api import async_playwright
from time import time


async def get_aliexpress_cookie_using_playwright():
    start_time = time()
    logger.info("Fetching the AliExpress Cookie using Playwright")
    async with async_playwright() as p:
        # Launch chrome browser
        browser = await p.chromium.launch(headless=True)

        # Open a new browser context (isolated session). Even though I'm setting the location to be US
        # it's not working
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
        await page.goto("https://aliexpress.com", timeout=120000)  # in millisecond

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
                "site=glo&c_tp=SGD&region=SG", "site=glo&c_tp=SGD&region=SG"
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
        browser = await p.chromium.launch(headless=True)

        # Open a new browser context (isolated session). Even though I'm setting the location to be US
        # it's not working
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
        await page.goto("https://aliexpress.com", timeout=120000)  # in millisecond

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
        )
        logger.info(
            f"Getting the AliExpress using Playwright took: {time()-start_time}"
        )
        return cookie


# Run the Playwright function
# response = get_aliexpress_cookie_using_playwright()
# print("this is the cookie: ", response)
# with open("playwright_response.txt", "w") as output:
#     output.write(str(response))
