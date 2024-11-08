from pydantic import BaseModel


# for the incoming data in the trigger_product_fetch post endpoint
class SheetUpdate(BaseModel):
    keyword: str
    range: str
