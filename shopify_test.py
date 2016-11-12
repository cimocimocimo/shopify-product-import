#!/usr/bin/env python

import shopify, inspect, dropbox
from pprint import pprint

SHOP_NAME = 'theia2'
API_KEY = '8ba2555b1e8abe16c86f5c0c558f9819'
PASSWORD = 'a5b2a46062a2e8bb20eed13610f2967f'

DROPBOX = {
    'token': 'fOy3Oa8F6yAAAAAAAAAAC_NZKRUH5GeVzFOtzYCNzk3mbPEpSBiprUKRWmMt2AjP'
}

shop_url = "https://{0}:{1}@{2}.myshopify.com/admin".format(API_KEY, PASSWORD, SHOP_NAME)
shopify.ShopifyResource.set_site(shop_url)
dbx = dropbox.Dropbox(DROPBOX['token'])

def get_all_products():
    has_more_products = True
    products = []
    page = 1
    limit = 250
    while (has_more_products):
        results = shopify.Product.find(page=page, limit=limit)
        if len(results) < limit or page == 100:
            has_more_products = False
        products = products + results
        page += 1
    return products

def get_latest_export():
    result = dbx.files_list_folder('/e-commerce')
    print(type(result))
    print("numb of entries: {}".format(len(result.entries)))
    print("has_more: {}".format(result.has_more))
    print(result.cursor)
    print(type(result.entries[0]))
    for entry in result.entries:
        # print(type(entry.server_modified))
        pprint(entry)
        break

def main():

    # Get the current shop
    shop = shopify.Shop.current()

    # Dropbox
    get_latest_export()

    # Get a specific product
    # products = get_all_products()
    # print(len(products))
    # for product in products:
    #     print(product)
    #     # pprint(inspect.getmembers(product))
    #     print(product.to_json())

    # product = shopify.Product.find(179761209)

    # Create a new product
    # new_product = shopify.Product()
    # new_product.title = "Burton Custom Freestyle 151"
    # new_product.product_type = "Snowboard"
    # new_product.vendor = "Burton"
    # success = new_product.save() #returns false if the record is invalid
    # # or
    # if new_product.errors:
    #something went wrong, see new_product.errors.full_messages() for example

    # Update a product
    # product.handle = "burton-snowboard"
    # product.save()

    # Remove a product
    # product.destroy()

    pass

if __name__ == '__main__':
    main()
