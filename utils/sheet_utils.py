import sys
import os

# Get the parent directory of the current file and add it to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from models.products import InputFetchedProducts
from utils.logger import logger
from utils.similarity_calculation import analyze_product_similarities

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
    input_product_data: InputFetchedProducts, product_order_id, keyword
):
    try:
        workbook = _get_google_sheet_workbook()
        sheet1 = workbook.worksheet("User Input")
        sheet2 = workbook.worksheet("Sheet2")

        keyword_sim = analyze_product_similarities(
            keyword, input_product_data.product_names
        )

        # adding the name of the keyword of each product group on top of it
        values = [
            [f"Products for keyword: {keyword}"] + input_product_data.product_names,
            [""] + input_product_data.product_prices,
            [""] + input_product_data.product_urls,
            [""] + input_product_data.website_source,
            [""] + keyword_sim,
        ]
        transposed_values = list(zip(*values))
        # print("Transposed values: ", transposed_values)

        # getting the number of rows in sheet2 so far
        current_number_of_rows = len(sheet2.col_values(1))
        num_of_products_to_update = (
            len(input_product_data.product_names) + 1
        )  # The +1 is because we are adding the name of the keyword on top of each product group

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

        # to add an empty row between products for different keywords
        add_line_between = 1 if product_order_id > 1 else 0
        start_row = current_number_of_rows + 1 + add_line_between
        end_row = len(transposed_values) + 1 + current_number_of_rows + add_line_between

        # From A to E because we have 5 columns to fill with values
        sheet2.update(
            range_name=f"A{start_row}:E{end_row}",
            values=transposed_values,
        )

        # batching the format operations to save api calls and time
        white_smoke_rgb = (
            230 / 255
        )  # normalizing the rgb values of white smoke to between 0 and 1 because that's how the format method accepts them
        products_range = f"A{start_row}:E{end_row}"
        keyword_name_range = f"A{start_row}:E{start_row}"
        url_range = f"C{start_row + 1}:C{end_row}"  # Skip the keyword row

        formats = [
            {
                "range": products_range,
                "format": {
                    "textFormat": {
                        "bold": False,
                    },
                    "backgroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0},
                },
            },
            {
                "range": keyword_name_range,
                "format": {
                    "backgroundColor": {
                        "green": white_smoke_rgb,
                        "red": white_smoke_rgb,
                        "blue": white_smoke_rgb,
                    },
                    "horizontalAlignment": "CENTER",
                    "textFormat": {"bold": True},
                },
            },
            {
                "range": url_range,
                "format": {
                    "backgroundColor": {
                        "green": 1.0,
                        "red": 1.0,
                        "blue": 1.0,
                    },
                    "hyperlinkDisplayType": "LINKED",
                    "textFormat": {"bold": False},
                },
            },
        ]
        sheet2.batch_format(formats=formats)
        # sheet2.format(
        #     f"A{start_row}:E{end_row}",
        #     format={
        #         "textFormat": {"bold": False},
        #         "backgroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0},
        #     },
        # )  # unsetting the formatting for the product rows

        # keyword_name_range = f"A{start_row}:E{start_row}"
        # white_smoke_rgb = (
        #     230 / 255
        # )  # normalizing the rgb values of white smoke to between 0 and 1 because that's how the format method accepts them
        # sheet2.format(
        #     keyword_name_range,
        #     format={
        #         "backgroundColor": {
        #             "green": white_smoke_rgb,
        #             "red": white_smoke_rgb,
        #             "blue": white_smoke_rgb,
        #         },
        #         "horizontalAlignment": "CENTER",
        #         "textFormat": {"bold": True},
        #     },
        # )

        sheet2.merge_cells(name=keyword_name_range, merge_type="merge_rows")

        # # Apply hyperlink formatting to URL column (column C)
        # url_range = f"C{start_row + 1}:C{end_row}"  # Skip the keyword row
        # sheet2.format(
        #     url_range,
        #     format={
        #         "textFormat": {"bold": False},
        #         "backgroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0},
        #         "hyperlinkDisplayType": "LINKED",
        #     },
        # )
        # start_loop = start_row + 1
        # new_hyperlinked_urls = [[f'=HYPERLINK("{url}", "{url}")'] for row in range(start_loop, start_loop + len(transposed_values[1:])) if row[2]]
        # sheet2.update(f"C")

        # Update the URLs with hyperlink formulas
        hyperlinked_updates = []
        for _, row in enumerate(
            transposed_values[1:], start=start_row + 1
        ):  # Skip header row
            if row[2]:  # Check if URL exists in column C (index 2)
                # cell = f"C{idx}"
                url = row[2]
                hyperlinked_updates.append([f'=HYPERLINK("{url}", "{url}")'])

        update_range = f"C{start_row + 1}:C{start_row + len(hyperlinked_updates)}"
        sheet2.update(update_range, hyperlinked_updates, raw=False)

        sheet1.update_acell(f"B{product_order_id+1}", "Fetched Products Successfully")
        sheet1.format(
            f"B{product_order_id+1}", format={"backgroundColor": {"green": 1.0}}
        )
    except Exception as e:
        logger.error(f"Something went wrong while updating the sheet: {e}")
        raise HTTPException(500, f"Something went wrong while updating the sheet: {e}")


# update_spreadsheet_with_fetched_products(
#     input_product_data=InputFetchedProducts(
#         product_names=["hi", "this", "a", "test"],
#         product_urls=["hi", "this", "another", "test"],
#         product_prices=["hi", "this", "also another", "test"],
#         website_source=["this", "is the", "website", "source"],
#     ),
#     product_order_id=2,
# )


def signal_start_of_product_retrieval():
    try:
        workbook = _get_google_sheet_workbook()
        sheet1 = workbook.worksheet("User Input")

        # deleting the previous output messages in col B, sheet1 to write new ones
        current_number_of_rows_sheet1 = len(
            sheet1.col_values(2)
        )  # gets the number of rows in col B
        print("current number of row col B sheet 1: ", current_number_of_rows_sheet1)

        sheet1.batch_clear([f"B2:B{current_number_of_rows_sheet1}"])
        sheet1.format(
            f"B2:B{current_number_of_rows_sheet1}",
            format={
                "backgroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}
            },  # This is white
        )
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
        return True
    except Exception as e:
        logger.error(
            f"Something went wrong with updating the B status cells in sheet 1: {e}"
        )
        return False


def signal_end_of_product_retrieval():
    try:
        workbook = _get_google_sheet_workbook()
        sheet1 = workbook.worksheet("User Input")
        sheet1.update_acell("C2", "Retrieved the Products, See Sheet 2 and Sheet 3")
        return True
    except Exception as e:
        logger.error(
            f"Something went wrong with updating the C2 status cell in sheet 1: {e}"
        )
        return False
