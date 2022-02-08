import pytest as pt
import pandas as pd
from main import process_csv_files, get_token, get_merchants, update_merchant
from credentials import *

df = process_csv_files()
token = get_token()

def test_buy_unit():
    assert df.iloc[0]["BUY_UNIT"] == "GR", "Buy unit test failed"

def test_package():
    assert df.iloc[0]["PACKAGE"] == "9GR", "Package test failed"

def test_category():
    #Check if category, sub category and sub sub category are joined and lowercase
    assert df.iloc[0]["CATEGORY"] == "hardlines|automotive|apariencia automovil", "Category test failed"

def test_stock():
    #Check if all items have stock higher than 0
    column = df['STOCK']
    count = column[column > 0].count()
    assert count == 248640, "Stock test failed"

def test_token():
    #Check if API returns credentials
    assert token is not None, "Token test failed"

def test_merchant_id():
    #Check if returns the Richard's merchant ID
    merchant_id = get_merchants(token, "Richard's")
    assert merchant_id == "ae9c81fe-163e-4546-8349-19dbf63715c7", "Merchant ID test failed"

def test_active_field():
    #Check if the proccess is updating the is_active field
    status_code = update_merchant(token, "ae9c81fe-163e-4546-8349-19dbf63715c7", "Richard's")
    assert status_code == 200, "Is active field test failed"



