import gspread
from google.oauth2.service_account import Credentials
import os


def get_google_sheet_workbook():
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
    client = gspread.authorize(creds)

    # get this from the url of the google sheet. It's between the /d/ and the /edit
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    workbook = client.open_by_key(sheet_id)

    return workbook
