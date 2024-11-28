# No need to import the functions of this file, pytest recognizes the name conftest.py by default and loads it
# in the test files

import pytest_asyncio
import os
import sys

# Get the parent directory of the current file and add it to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.using_playwright import (
    get_aliexpress_cookie_using_playwright,
    get_ishtari_cookie_using_playwright,
)
from utils.api_utils import AliexpressCookie, IshtariCookie


@pytest_asyncio.fixture
async def mock_aliexpress_cookie():
    cookie_value = await get_aliexpress_cookie_using_playwright()
    return AliexpressCookie(cookie=cookie_value)


@pytest_asyncio.fixture
async def mock_ishtari_cookie():
    cookie_value = await get_ishtari_cookie_using_playwright()
    return IshtariCookie(cookie=cookie_value)
