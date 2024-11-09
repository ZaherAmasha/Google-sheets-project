from pydantic import BaseModel
from typing import List


# for the incoming data in the trigger_product_fetch post endpoint
class SheetUpdate(BaseModel):
    # keyword: str
    keywords: List[str]
    # range: str
