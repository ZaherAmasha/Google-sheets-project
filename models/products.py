from pydantic import BaseModel
from typing import Dict, List


# For the output of functions that fetch products (for a single keyword) from websites (AliExpress, Ishtari, ...)
class OutputFetchedProducts(BaseModel):
    product_names: List[str]
    product_urls: List[str]
    product_prices: List[str]


# same as output, but I want the data validation to happen twice. This is for the input of the update_spreadsheet_with_fetched_products function
class InputFetchedProducts(BaseModel):
    product_names: List[str]
    product_urls: List[str]
    product_prices: List[str]
