import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds']

print(os.environ.get('json_credentials'))

# credentials = ServiceAccountCredentials.from_json(
#     os.environ.get('json_credentials'), scope)

credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    os.environ.get('json_credentials'))

print(credentials)
gc = gspread.authorize(credentials)
wks = gc.open_by_key('1o-C-3WwfcEYWipIFb112tkuM-XOI8pVVpA9_sag9Ph8')
list_of_items = wks.sheet1.get_all_values()[:5]
headers = list_of_items.pop(0)

print(wks.sheet1)
