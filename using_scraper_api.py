from dotenv import load_dotenv
import os
import requests
import cloudscraper

load_dotenv()

SCRAPERAPI_KEY = os.getenv("SCRAPERAPI_KEY")

# with scraperAPI, on every new call a new IP address is used


def get_request_using_scraperapi(
    url: str, test_ip=False, country_code: str = None, **kwargs
) -> requests.Response:

    payload = {
        "api_key": SCRAPERAPI_KEY,
        "url": (
            "http://httpbin.org/ip" if test_ip else url
        ),  # This url gets the ip address of the client sending to it
    }
    if country_code:
        payload.update({"country_code": country_code})
    print(f"This the payload from the get_requests_using_scraperapi: {payload}")
    response = requests.get("https://api.scraperapi.com", params=payload, **kwargs)

    return response


def get_request_from_session_with_scraperapi(
    session: requests.Session, url: str, test_ip=False, **kwargs
) -> requests.Response:

    payload = {
        "api_key": SCRAPERAPI_KEY,
        "url": (
            "http://httpbin.org/ip" if test_ip else url
        ),  # This url gets the ip address of the client sending to it
    }
    response = session.get("https://api.scraperapi.com", params=payload, **kwargs)

    return response


def get_request_using_cloudscraper_with_scraperapi(
    cloudscraper: cloudscraper.CloudScraper, url: str, test_ip=False, **kwargs
) -> requests.Response:

    payload = {
        "api_key": SCRAPERAPI_KEY,
        "url": (
            "http://httpbin.org/ip" if test_ip else url
        ),  # This url gets the ip address of the client sending to it
    }
    response = cloudscraper.get("https://api.scraperapi.com", params=payload, **kwargs)

    return response


if __name__ == "__main__":
    # scraper = cloudscraper.create_scraper()
    session = requests.Session()
    response = get_request_from_session_with_scraperapi(session, "", test_ip=True)
    # response = get_request_using_cloudscraper_with_scraperapi(scraper, "", test_ip=True)
    print(response.text)
