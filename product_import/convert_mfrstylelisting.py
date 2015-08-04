import collections, re, pprint
import schema
from models import *

def are_all_list_items_empty(list):
    for item in list:
        if item:
            return False
    return True

def main():
    try:
        f = open('data/mfrstylelisting.csv', 'r')
    except IOError:
        return

    # read all lines of the csv into a 2D list, rows as the first level, columns 2nd.
    rows_list = [list(line) for line in csv.reader(f)][12:]

    products = list()

    style_number_only = re.compile('^\d{6}$')
    year_from_season = re.compile('\d{4}$')

    building_item = False
    for row in rows_list:
        if are_all_list_items_empty(row):
            continue

        if style_number_only.match(row[0]) != None and building_item == False:
            # first row of the product
            item = collections.OrderedDict()
            item["Style Number"] = row[0]
            item["Dress Name"] = row[0]
            item["Collection"] = "Bridal " + year_from_season.search(row[5]).group(0)
            item["Price (USD)"] = int_from_string(row[13].strip())

            item["Oversell"] = False
            item["Waitlist"]  = False
            item["Fulfillment"] = 'js-group'
            item["Sizes"] = [0,2,4,6,8,10,12,14,16]
            item["Colors"] = ['white']

            building_item = True
            continue

        if building_item == True:
            item["Dress Description"] = row[0]
            products.append(item)
            building_item = False

    target = DataFile(filename='data/mfrstylelisting_export.csv', schema=schema.js_group_dresses)
    target.data = products
    target.save()

if __name__ == '__main__':
    main()
