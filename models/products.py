from pydantic import BaseModel, model_validator
from typing import List


# For the output of functions that fetch products (for a single keyword) from websites (AliExpress, Ishtari, ...)
class OutputFetchedProducts(BaseModel):
    product_names: List[str]
    product_urls: List[str]
    product_prices: List[str]
    website_source: List[str]

    def concatenate(self, other: "OutputFetchedProducts") -> "OutputFetchedProducts":
        """To merge the products fetched from multiple websites into a single product group to
        be displayed in the spreadsheet"""
        return OutputFetchedProducts(
            product_names=self.product_names + other.product_names,
            product_urls=self.product_urls + other.product_urls,
            product_prices=self.product_prices + other.product_prices,
            website_source=self.website_source + other.website_source,
        )

    @model_validator(mode="after")
    def check_lengths_match(self):
        # Ensure all lists have the same length
        lengths = {
            "product_names": len(self.product_names),
            "product_urls": len(self.product_urls),
            "product_prices": len(self.product_prices),
            "website_source": len(self.website_source),
        }
        if len(set(lengths.values())) != 1:
            raise ValueError(
                f"All lists must have the same length. Lengths found: {lengths}"
            )
        return self


# same as output, but I want the data validation to happen twice. This is for the input of the update_spreadsheet_with_fetched_products function
class InputFetchedProducts(BaseModel):
    product_names: List[str]
    product_urls: List[str]
    product_prices: List[str]
    website_source: List[str]
