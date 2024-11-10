import gspread.utils
import requests
import os
from bs4 import BeautifulSoup
import gspread
from google.oauth2.service_account import Credentials
import re
from dotenv import load_dotenv

from logger import logger
from utils.utils import remove_elements_with_whitespaces_and_empty_from_list

load_dotenv()


def _update_spreadsheet_with_fetched_products(
    titles, image_names, prices, product_order_id
):
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
    client = gspread.authorize(creds)

    # get this from the url of the google sheet. It's between the /d/ and the /edit
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    # logger.info(f"this is the sheet id: {sheet_id}")
    workbook = client.open_by_key(sheet_id)
    sheet1 = workbook.worksheet("User Input")
    sheet2 = workbook.worksheet("Sheet2")

    values = [titles, image_names, prices]
    transposed_values = list(zip(*values))
    # print("Transposed values: ", transposed_values)
    # to add an empty row betwee products for different keywords
    if product_order_id > 1:
        add_line_between = 1
    else:
        add_line_between = 0

    # getting the number of rows in sheet2 so far
    current_number_of_rows = len(sheet2.col_values(1))
    num_of_products_to_update = len(titles)
    logger.info(f"num of products: {num_of_products_to_update}")
    # print("num of products: ", len(transposed_values))
    # print("row count: ", len(sheet.col_values(1)))

    # deleting the previous output messages in col B, sheet1 to write new ones
    if product_order_id == 1:
        current_number_of_rows_sheet1 = len(
            sheet1.col_values(2)
        )  # gets the number of rows in col B
        print("current number of row col B sheet 1: ", current_number_of_rows_sheet1)
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
    sheet1.format(f"B{product_order_id+1}", format={"backgroundColor": {"green": 1.0}})
    # sheet1.update_acell(f"C2", "Retrieved the Products, See Sheet 2")


# sheet.format("A1:C1", format={"textFormat": {"bold": True}})
# _update_spreadsheet_with_fetched_products(
#     ["hi", "this", "a", "test"],
#     ["hi", "this", "another", "test"],
#     ["hi", "this", "another", "test"],
#     2,
# )


def fetch_aliexpress_product_recommendations(search_keyword, product_order_id):

    url = f"https://www.aliexpress.com/w/wholesale-{search_keyword}.html?spm=a2g0o.productlist.search.0"

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "max-age=0",
        "Cookie": 'lzd_cid=4c582dbc-b52b-4e9b-a38a-103581980fc1; xlly_s=1; global_sid=178ccb1ce7dbefac9fd368bda9f8625f; _tb_token_=e37bb3330eb55; lzd_uid=7100002185002; ali_apache_id=33.22.100.123.1730979784748.411678.9; cna=XGKzH/Mc8icCAdXMcm24qNi7; e_id=pt10; _gcl_au=1.1.250438436.1730979958; x_router_us_f=x_alimid=6077075735; sgcookie=E100a7FiHzKz6zrjyIqHhfnKDMaiDnTKmT4GPLFUDahtHQZrc4jwgPhVSHOZU6dwyyS1cbFnZ2sFKKMj2ytpXLIucwPDeWECY6tHtFcoswQ9Ses=; aep_common_f=aVGBvqdFWDPceW/M8C0VgwurH8zzE/DWl0SnsYoPAGzL7HK4yXnbwQ==; xman_f=JBQ0dur8yjtHqu6hQGnRZRdYxNgfv/uXbiz3sk9fUDUvaUrm/YPX7PJIlpPYeKGnmVJ7GLt4nysSrnUqQ/8nR1XHXJtohBg0XZXgnxgX4AJfv5fFIyyOb2QLnrLsIoNrouYARV33FR7Hyvawq7peI98pvzCA0fpCGlMMEIjmiJu5EJVtIAPZ+X6GZW4bDZ13PHxI21CoHBnMb78ZsPTXYCn3JHIVPanyNHhIN7iDC9acihffDLoRaTNCq+TNfanq2/kVIkI+wwMN9msV2iJrimUmHuovtlHXohzcQr6JmbgLefFmFDD6xkddYIUBJlev6j+bc3Xo8b6MfBFeGFATPqDMGA4X3vP5B3gRxIRm7IgcRpwhy+onxp0CBruRtfV/NfyR4X2NS7iQUhnuAHl7By7G4440kkosk9ljh2J7NxbeZRq5a2C3mw==; ali_apache_tracktmp=W_signed=Y; _history_login_user_info={"userName":"amashaazaherrr","avatar":"","accountNumber":"amashaazaherrr@gmail.com","phonePrefix":"","expiresTime":1733572117276}; AB_DATA_TRACK=108603_6147.108597_6291; AB_ALG=; AB_STG=st_SE_1729754453849%23stg_3624%2Cst_SE_1730118732538%23stg_3648; intl_locale=en_US; lwrid=AgGTBnW7melOCGyc7oYw2RpuI5ay; join_status=; aep_usuc_f=site=glo&province=&city=&c_tp=LBP&x_alimid=6077075735&isb=y&region=LB&b_locale=en_US&ae_u_p_s=2; _gid=GA1.2.1619919357.1730980203; lwrtk=AAEEZy0Z6J+sujIGXv4Ak2IFfv/Lfw0AVkVlC/FmBg+BTvkCE94BVf8=; lwrtk=AAEEZy0Z6J+sujIGXv4Ak2IFfv/Lfw0AVkVlC/FmBg+BTvkCE94BVf8=; _pin_unauth=dWlkPU9UbGxaak15WTJZdFptWmpZeTAwT0Rrd0xUazRNalV0TmpZeU5EQTVaREkxWVdFMA; _fbp=fb.1.1730980207699.201376450717234808; _gac_UA-17640202-1=1.1730980253.Cj0KCQiA57G5BhDUARIsACgCYnzslr7dkd-AgSVLRggRlKmR1f2rnN3toTlSBkk_mZoRrIMR9BjhUZ8aAtqEEALw_wcB; _gcl_gs=2.1.k1$i1730980252$u3375712; aeu_cid=61e49c3bf6f3490ba80334f9f8de2f9b-1730980254247-05561-UneMJZVf; traffic_se_co=%7B%22src%22%3A%22Google%22%2C%22timestamp%22%3A1730980254249%7D; ali_apache_track=mt=1|mid=lb1242431135scdae; acs_usuc_t=acs_rt=2693ca3557464bed8aa8269b2fa946ca&x_csrf=jw0w24xc4pi4; xman_t=+/4Nb83TUEMY1jlMo16emijPIlzq/X20QkIcknuGcDoUMHhao9xODdqzvXY7td9d; _gcl_aw=GCL.1730980769.Cj0KCQiA57G5BhDUARIsACgCYnzslr7dkd-AgSVLRggRlKmR1f2rnN3toTlSBkk_mZoRrIMR9BjhUZ8aAtqEEALw_wcB; _gcl_dc=GCL.1730980769.Cj0KCQiA57G5BhDUARIsACgCYnzslr7dkd-AgSVLRggRlKmR1f2rnN3toTlSBkk_mZoRrIMR9BjhUZ8aAtqEEALw_wcB; xman_us_f=x_locale=en_US&x_l=0&x_user=LB|amashaazaherrr|user|ifm|6077075735&x_lid=lb1242431135scdae&x_c_chg=1&x_as_i=%7B%22aeuCID%22%3A%2261e49c3bf6f3490ba80334f9f8de2f9b-1730980254247-05561-UneMJZVf%22%2C%22affiliateKey%22%3A%22UneMJZVf%22%2C%22channel%22%3A%22PREMINUM%22%2C%22cv%22%3A%222%22%2C%22isCookieCache%22%3A%22N%22%2C%22ms%22%3A%221%22%2C%22pid%22%3A%22178094261%22%2C%22tagtime%22%3A1730980254247%7D&acs_rt=2693ca3557464bed8aa8269b2fa946ca; _m_h5_tk=979bda01032e94ed94e2bdbbda94b999_1730988569306; _m_h5_tk_enc=5491fdb0106fdfd501f2ad453eec7157; AKA_A2=A; intl_common_forever=Js+w4SO3ZrTXvJm0uXfUCdkd7aVoDaTJx65VE3vGcamks3ssuH4Fhg==; RT="z=1&dm=aliexpress.com&si=0e9f9830-39e6-4a3d-ade2-6471c72f60c2&ss=m378wzfu&sl=l&tt=2s76&obo=2&rl=1"; __rtbh.uid=%7B%22eventType%22%3A%22uid%22%2C%22id%22%3A%226077075735%22%2C%22expiryDate%22%3A%222025-11-07T14%3A04%3A38.422Z%22%7D; __rtbh.lid=%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%221ISBzWYyoRO5bescZ2X7%22%2C%22expiryDate%22%3A%222025-11-07T14%3A04%3A38.422Z%22%7D; _ga_VED1YSGNC7=GS1.1.1730986220.2.1.1730988278.32.0.0; _ga=GA1.1.1069184324.1730979959; cto_bundle=JXta6F9HeW96aHlYWGFVMXE1M1BFSk02UEowSEtIQ2tIRjQ3M0tCMFJ5U0xWZlVnZ2YzcFhkZVdtMlUxTnF0UUlBUmhjNFFNJTJCMyUyQm5pS2hObWtVVUtNb1ZkVlcxcWVnc3pibXhlcWVyYlpLbEY1Y3c4OHVNNko5bW9hWkY3c3ZjemRmQVB4RFZvM3I3empvdHFSRDBmUzBBUVVoSnQzbU5lQmpvcXY3dlpMMkZlS1Y2dFhqNnNHclZhNUglMkJLanJucG1RWUVyU3lmQTlXNlppczBKMHl3WXVLYUZnJTNEJTNE; isg=BO3tqAR3dmDSKxIM6_z9jIph_IBnSiEcIaxq_S_yOwS2pg1Y95kU7Xt0kGJAJjnU; tfstk=f1lK0GVtit4Ied7OBT9gq97P-SLiwb3E7DufZuqhFcntlqS3Fpokw_3EPzD3xkDT2ciTAMVCtan-bmCH80YE6LgK-ablETvWF23hraXlEL9SJ2blrT05yzNEsvfuxHP-PmVJmnADi2uUT7tDmaZWZHN7PQq7ZCqIV7PWmhvuRmbuamPS7FcS5FUurM1IVuN61lzROyi7ARs_kzP7N7i71Pauk_sCd8g1Clz7Nui7NUUepuxg0_HoT6IyAN-dw_hT5erjJPza7fULpow_7_gn6yeLc2GhfjEYkxhTnvTBdrF8b2lgpI50aVDx2YiXj9qIHrnLBAxRAult5XMS7ML_MVHinJH9A_Eitzn4k0dVUVy7kDPIOhjLw5U4EYnHb_ZnHViTnfjGiSMqXbebGgPEijEajiqYr9T9WTWzdP8VlYDZXvrWYPEDSFXPURnLWoY9WTWzdPzTmFuRUTytv; epssw=7*RzDss6zJb6Sh667vTadsT2bs6UD4OX367X65-s9bPup3sjkehxYr4OJrK9r8zC8deYHDovGQTHDL1F16sdssv2l2a6ssss3vTassmBo-GB8TigFuuBsjLwLTZa3GNWy_sumqvGQiAgzCi2l2z6jcO63nUTIR7_pT8suNTGe0RmU78ZrVRroGZwe87ssRdehvObRtspqLCDMJn65sO1k8MOQfC50staA2jyNUprj2CDP8r-9y-OfORYoOOeh3zEss_suQ3CewKJctJeb2srrbOs6hOsRbOs3KIW_JWKQs9hdmjbOR3s6sshohO3LV7hd.',
        "Priority": "u=0, i",
        "Origin": "https://www.aliexpress.com",
        "Referer": f"https://www.aliexpress.com/w/wholesale-{search_keyword}.html?spm=a2g0o.home.history.1.9d5f76dbxo1lT7",
        "Sec-Ch-Ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Linux"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Site": "same-origin",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    }
    response = requests.request("GET", url, headers=headers)
    response.raise_for_status()  # to raise an exception when an exception happens, for debugging purposes. Without it, the response may be invalid and we wouldn't know immeadiately

    # with open("white_shoes_response_text.txt", "w") as output:
    #     output.write(response.text)

    soup = BeautifulSoup(response.text, "html.parser")

    # fetching the titles
    titles = soup.find_all("div", class_="multi--title--G7dOCj3")
    logger.info(f"found {len(titles)} titles")
    for title in titles:
        logger.info(f"Title: {title.get_text(strip=True)}")

    # fetching the urls for the individual products
    product_urls = soup.find_all(
        "a",
        class_=re.compile(
            r"multi--container--1UZxxHY cards--card--3PJxwBm (cards--list--2rmDt5R )?search-card-item"
        ),
    )

    logger.info(f"found {len(product_urls)} product urls")
    titles = [title.get_text(strip=True) for title in titles]
    product_urls = [
        ("https:" + product_url.get("href").strip()) for product_url in product_urls
    ]

    prices = soup.find_all("div", class_="multi--price-sale--U-S0jtj")
    logger.info(f"Found {len(prices)} prices")
    for price in prices:
        logger.info(f"These are the prices: {price.get_text(strip=True)}")
    prices = [price.get_text(strip=True) for price in prices]

    _update_spreadsheet_with_fetched_products(
        titles=list(titles),
        image_names=list(product_urls),
        prices=list(prices),
        product_order_id=product_order_id,
    )

    return True


# examples:
# fetch_aliexpress_product_recommendations("black shoes")
# fetch_aliexpress_product_recommendations("white shoes", 1)
# fetch_aliexpress_product_recommendations("zzzzzzzzzzzzzzzzzzzzzz")
