from utils.logger import logger

from playwright.sync_api import sync_playwright
from time import time


def get_aliexpress_cookie_using_playwright():
    start_time = time()
    with sync_playwright() as p:
        # Launch chrome browser
        browser = p.chromium.launch(headless=True)

        # Open a new browser context (isolated session). Even though I'm setting the location to be US
        # it's not working
        context = browser.new_context(
            geolocation={
                "latitude": 37.7749,
                "longitude": -122.4194,
            },  # San Francisco, USA
            locale="en-US",  # English locale
            timezone_id="America/Los_Angeles",  # U.S. Pacific Timezone
        )

        # Open a new page
        page = context.new_page()

        # Navigate to the main URL
        page.goto("https://aliexpress.com", timeout=60000)  # in millisecond

        cookie_for_requests = context.cookies("https://aliexpress.com")

        # Close the browser
        browser.close()

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
