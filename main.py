import numpy as np
import pandas as pd
import requests as rq
from credentials import *

#API credentials
grant_type = GRAND_TYPE
cliend_id = CLIENT_ID
client_secret = CLIENT_SECRET
base_url = BASE_URL

#Check API status
def gets_status():
    status = rq.get(base_url)
    print(f"Status: {status.status_code}")

def get_token():
    url = f"{base_url}/oauth/token?client_id={cliend_id}&client_secret={client_secret}&grant_type={grant_type}"

    token_response = rq.post(
        url,
        allow_redirects=False,
        verify=False,
    )
    if token_response.status_code != 200:
        print("update_merchant: ", token_response.status_code)

    #Getting response in JSON
    token_json = token_response.json()

    return token_json.get('access_token')

#Search the merchant name and return the ID
def search_merchant(merchant_name, data):
    #Get specific merchant name
    for i in data['merchants']:
        if i['name'].lower() == merchant_name.lower():
            return i['id'] 
    return None

def get_merchants(token, merchant_name):
    url = f"{base_url}/api/merchants"
    header = {'token': f'Bearer {token}'}

    response = rq.get(
        url,
        headers = header
    )

    if response.status_code != 200:
        print("update_merchant: ", response.status_code)

    response_json = response.json()
    merchant_id = search_merchant(merchant_name, response_json)

    return merchant_id
    
#Update the is_active field of the Merchant
def update_merchant(token, merchant_id, merchant_name):
    url = f"{base_url}/api/merchants/{merchant_id}"

    header = {'token': f'Bearer {token}'}
    data = {
        "can_be_deleted": False,
        "can_be_updated": True,
        "id": f"{merchant_id}",
        "is_active": True,
        "name": f"{merchant_name}"
    }

    response = rq.put(
        url,
        headers = header,
        json = data
    )

    if response.status_code != 200:
        print("update_merchant: ", response.status_code)
    
    print(f"is_active field updated for merchant {merchant_name}")
    return response.status_code

def delete_merchant(token, merchant_name):
    merchant_id = get_merchants(token, merchant_name)

    #Check if merchant id exists
    if merchant_id:
        url = f"{base_url}/api/merchants/{merchant_id}"
        header = {'token': f'Bearer {token}'}

        response = rq.delete(
            url,
            headers = header
        )
        if response.status_code != 200:
            print("delete_merchant: ", response.status_code)

        print(f"Merchant {merchant_name} has been deleted")
    else:
        print("Merchant name not found")


def send_products(token,merchant_id,dataframe):
    branches = ("MM","RHSM")
    url = f"{base_url}/api/products"
    header = {'token': f'Bearer {token}'}

    for branch in branches:
        #Get most expensive products for each branch
        expensive_df = dataframe[dataframe["BRANCH"] == branch].nlargest(100, "PRICE")

        print(f"Sending products to API, Branch: {branch}")

        #itterate and POST the 100 most expensive products
        for i in range(0,100):
            data = {
                "merchant_id": f"{merchant_id}",
                "sku": str(expensive_df.iloc[i]['SKU']),
                "barcodes": [str(expensive_df.iloc[i]['EAN'])],
                "brand": str(expensive_df.iloc[i]['BRAND_NAME']),
                "name": str(expensive_df.iloc[i]['ITEM_NAME']),
                "description": str(expensive_df.iloc[i]['ITEM_DESCRIPTION']),
                "package": str(expensive_df.iloc[i]['PACKAGE']),
                "image_url": str(expensive_df.iloc[i]['ITEM_IMG']),
                "category": str(expensive_df.iloc[i]['CATEGORY']),
                "url": "Empty",
                "branch_products": [{
                    "branch": str(expensive_df.iloc[i]['BRANCH']),
                    "stock": int(expensive_df.iloc[i]['STOCK']),
                    "price": float(expensive_df.iloc[i]['PRICE'])
                }]
            }

            response = rq.post(
                url,
                headers = header,
                json = data    
            )

            if response.status_code != 200:
                print("send_products: ", response.status_code)
            

def process_csv_files():
    #Read CSV Files
    product_df = pd.read_csv('files/PRODUCTS.csv', sep='|')
    prices_df = pd.read_csv('files/PRICES-STOCK.csv', sep='|')

    #SKU check and assigning it as index
    product_df.set_index('SKU',inplace=True)

    #Cleaning data
    #Removing HTML Tags from Item description
    product_df['ITEM_DESCRIPTION'] = product_df['ITEM_DESCRIPTION'].str.replace(r'<[^<>]*>', '', regex=True)
    
    #Joinning categories
    product_df['CATEGORY'] = (product_df['CATEGORY']).str.cat(product_df['SUB_CATEGORY'], sep="|").str.cat(product_df['SUB_SUB_CATEGORY'], sep="|")
    product_df.drop(['SUB_CATEGORY','SUB_SUB_CATEGORY'], axis=1, inplace=True)
    #Lowercase category
    product_df['CATEGORY'] = product_df['CATEGORY'].str.lower()
    
    #Check if item descriptions contains Buy unit and package information
    units = ('UN','GR','GRS','PZA','KG','KGS','CJA','ML','LT','LB')
    for unit in units:
        product_df.loc[product_df["ITEM_DESCRIPTION"].str.contains(unit), 'BUY_UNIT'] = unit

    #Extract and create package column
    product_df["PACKAGE"] = product_df['ITEM_DESCRIPTION'].str.extract(r'(\d*\s?[UN|GR|GRS|PZA|KG|KGS|CJA|ML|LT|LB]+\.?$)')
    
    #Replacing NaN values
    product_df['BUY_UNIT'] = product_df['BUY_UNIT'].fillna('OTHER')

    #Removing products with zero Stock, and keeping only MM and RHSM
    prices_df = prices_df[(prices_df['STOCK'] > 0)]
    prices_df = prices_df[(prices_df['BRANCH'] == 'MM') | (prices_df['BRANCH'] == 'RHSM')]

    #Removing duplicates, Only leaving the items with higher stock and Higher price
    prices_df.sort_values(['SKU','STOCK','PRICE'], ascending = (True,False,False), inplace=True)
    prices_df = prices_df.drop_duplicates('SKU').sort_index()

    #Mergin Dataframes
    main_df = pd.merge(product_df, prices_df, on='SKU')

    return main_df

def run_etl(merchant_name):
    print("Processing CSV files")
    data = process_csv_files()

    print("\nGetting API credentials")
    token = get_token()
    print("\nGetting Merchant ID")
    merchant_id = get_merchants(token, merchant_name)
    print("\nUpdating is_active field")
    update_merchant(token, merchant_id, merchant_name)
    print("\nDeleting Merchant")
    delete_merchant(token, "Beauty")
    print("\nSending Products")
    send_products(token, merchant_id, data)
    print("\nProcess executed successfully.")

if __name__ == "__main__":
    run_etl("Richard's")