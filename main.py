import numpy as np
import pandas as pd
import regex as re

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
    
    #Check if item descriptions contains Buy unit information
    units = ('UN','GR','PZA','KG','ML','LT','LB')
    for unit in units:
        product_df.loc[product_df["ITEM_DESCRIPTION"].str.contains(unit), 'BUY_UNIT'] = unit

    #Replacing NaN values
    product_df['BUY_UNIT'] = product_df['BUY_UNIT'].fillna('OTHER')


    #Removing products with zero Stock, and keeping only MM and RHSM
    prices_df = prices_df[(prices_df['STOCK'] > 0)]
    prices_df = prices_df[(prices_df['BRANCH'] == 'MM') | (prices_df['BRANCH'] == 'RHSM')]

    #Removing duplicates, Only leaving the items with higher stock and lower price
    prices_df.sort_values(['SKU','STOCK','PRICE'], ascending = (True,False,True), inplace=True)
    prices_df = prices_df.drop_duplicates('SKU').sort_index()

    #print(prices_df[prices_df['SKU']==321542])
    print(prices_df)

    
if __name__ == "__main__":
    process_csv_files()
