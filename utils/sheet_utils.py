import sys
import os

# Get the parent directory of the current file and add it to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from utils.logger import logger
from models.products import InputFetchedProducts

import gspread
from google.oauth2.service_account import Credentials
from fastapi import HTTPException


def _get_google_sheet_workbook():
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
    client = gspread.authorize(creds)

    # get this from the url of the google sheet. It's between the /d/ and the /edit
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    workbook = client.open_by_key(sheet_id)

    return workbook


def update_spreadsheet_with_fetched_products(
    input_product_data: InputFetchedProducts, product_order_id
):
    try:
        workbook = _get_google_sheet_workbook()
        sheet1 = workbook.worksheet("User Input")
        sheet2 = workbook.worksheet("Sheet2")

        values = [
            input_product_data.product_names,
            input_product_data.product_urls,
            input_product_data.product_prices,
        ]
        transposed_values = list(zip(*values))
        # print("Transposed values: ", transposed_values)
        # to add an empty row between products for different keywords
        if product_order_id > 1:
            add_line_between = 1
        else:
            add_line_between = 0

        # getting the number of rows in sheet2 so far
        current_number_of_rows = len(sheet2.col_values(1))
        num_of_products_to_update = len(input_product_data.product_names)
        logger.info(f"num of products: {num_of_products_to_update}")
        # print("num of products: ", len(transposed_values))
        # print("row count: ", len(sheet.col_values(1)))

        # deleting the previous output messages in col B, sheet1 to write new ones
        if product_order_id == 1:
            current_number_of_rows_sheet1 = len(
                sheet1.col_values(2)
            )  # gets the number of rows in col B
            print(
                "current number of row col B sheet 1: ", current_number_of_rows_sheet1
            )
            # sheet1.delete_dimension(
            #     gspread.utils.Dimension.rows, 2, current_number_of_rows_sheet1
            # )
            sheet1.batch_clear([f"B2:B{current_number_of_rows_sheet1}"])
            sheet1.format(
                f"B2:B{current_number_of_rows_sheet1}",
                format={
                    "backgroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}
                },  # This is white
            )
            # sheet1.range(f"B2:B{current_number_of_rows_sheet1}").clear()
            # sheet1.delete_named_range(f"B2:B{current_number_of_rows_sheet1}")
            num_of_keywords = len(sheet1.col_values(1)) - 1
            print("number of keywords: ", num_of_keywords)
            sheet1.update(
                f"B2:B{num_of_keywords+1}",
                [["Fetching Product Recommendations"] for _ in range(num_of_keywords)],
            )
            sheet1.format(
                f"B2:B{num_of_keywords+1}",
                format={"backgroundColor": {"red": 1.0, "green": 1.0}},
            )  # this is yellow in RGB

        if product_order_id == 1 and current_number_of_rows > 1:
            sheet2.delete_rows(
                2, current_number_of_rows
            )  # clearing the cells from previous calls
            current_number_of_rows = (
                1  # setting this manually instead of fetching using gspread
            )

        # Ensure enough rows are available to accommodate new data. The .update method can't update non-existant rows
        required_rows = current_number_of_rows + num_of_products_to_update
        if required_rows > sheet2.row_count:
            sheet2.add_rows(required_rows - sheet2.row_count)  # Add missing rows

        sheet2.update(
            range_name=f"A{current_number_of_rows+1+add_line_between}:C{len(transposed_values)+1+current_number_of_rows+add_line_between}",
            values=transposed_values,
        )

        sheet1.update_acell(f"B{product_order_id+1}", "Fetched Products Successfully")
        sheet1.format(
            f"B{product_order_id+1}", format={"backgroundColor": {"green": 1.0}}
        )
        # sheet1.update_acell(f"C2", "Retrieved the Products, See Sheet 2")
    except Exception as e:
        logger.error(f"Something went wrong while updating the sheet: {e}")
        raise HTTPException(500, f"Something went wrong while updating the sheet: {e}")


# sheet.format("A1:C1", format={"textFormat": {"bold": True}})
# update_spreadsheet_with_fetched_products(
#     input_product_data=InputFetchedProducts(
#         product_names=["hi", "this", "a", "test"],
#         product_urls=["hi", "this", "another", "test"],
#         product_prices=["hi", "this", "also another", "test"],
#     ),
#     # ["hi", "this", "a", "test"],
#     # ["hi", "this", "another", "test"],
#     # ["hi", "this", "also another", "test"],
#     product_order_id=2,
# )


def signal_end_of_product_retrieval():
    try:
        workbook = _get_google_sheet_workbook()
        sheet1 = workbook.worksheet("User Input")
        sheet1.update_acell("C2", "Retrieved the Products, See Sheet 2")
        return True
    except Exception as e:
        logger.error(f"Something went wrong with updating the C2 cell in sheet 1: {e}")
        return False
