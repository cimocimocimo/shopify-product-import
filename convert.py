#!/usr/bin/env python

import collections, re, json, csv, argparse
from pprint import pprint
import product_import.schema as schema
from product_import.models import Product, Variant, Option, DataFile, Schema, Column, ImageGallery, Image, LeftToSellData, Inventory
import product_import.helpers as helpers

class Converter:
    """
    Takes two DataFiles and converts the formatted data in one and
    converts it to another data format.
    """

    def __init__(self, item_model):
        self.item_model = item_model
        self.items = list()

    def import_data(self, source, item_map):
        pass

    def export_data(self, target, item_mapper):
        pass

# fix color name abbreviations
def correct_color_name(color):
    color_abbreviations = {"blk/watermelon": "black/watermelon",
                           "blush/mid": "blush/midnight",
                           "prb  - prussian blue": "prussian blue",
                           "blk/midnight": "black/midnight",
                           "blk pewter": "black pewter",
                           "blk/teal": "black/teal",
                           "blk/gold": "black/gold",
                           "blk/white": 'black/white',
                           'fucshia': 'fuchsia',
                           'fushia multi': 'fuchsia multi',
                           "champ/silver": "champagne/silver",
                           "creme": "cream"}

    if color in color_abbreviations:
        return color_abbreviations[color]
    else:
        return color


def prepare_left_to_sell_file():

    helpers.convert_xls_to_csv('data/lefttosell_summary_js.xls', 'leftToSell_summary_JS.rpt', 'data/TestLeftToSell.csv');

    try:
        f = open('data/NewLeftToSell.csv', 'r')
    except IOError:
        return

    # read all lines of the csv into a 2D list, rows as the first level, columns 2nd.
    rows_list = [list(line) for line in csv.reader(f)]

    # the size labels
    sizes = rows_list[22][5:14]

    # matches 882451 / / MID  midnight
    # matches 882451X / / MID  midnight
    pattern = re.compile("(^\d{6})X?\s/\s/\s(\w{3})\s{2}(.+)")

    variants = list()

    # the dress inventories
    for row in rows_list[24:]:
        match = pattern.match(row[0])
        if not match:
            continue
        style = match.group(1)
        color_code = match.group(2)
        color_name = match.group(3)

        # fix color name abbreviations
        color_name = correct_color_name(color_name)

        price = helpers.int_from_str(row[1].strip())

        # the sheet is incorrect. the first column under size 0 is the total of all dresses
        # the column under 2 is for size 0 and it continues that way for the other sizes
        quantities = row[6:15]

        # create rows for each of the sizes
        for index, size in enumerate(sizes):
            item = collections.OrderedDict()
            item["Style"] = style
            item["Color"] = color_code
            item["Color Desc"] = color_name
            item["Size Desc"] = size
            item["Left to Sell"] = int(float(quantities[index]))
            item["price"] = price

            variants.append(item)

    # initialize the output csv file.
    target = DataFile(filename='data/LeftToSell.csv', schema=schema.left_to_sell_items)

    target.data = variants

    target.save()

def main(input_file):

    # this prepares the LTS report from the weird table layout to the old LTS report format that's
    # specified in the schema.
    prepare_left_to_sell_file()

    # open the data files and unserialze the data according to their schema
    source = DataFile(filename=input_file, schema=schema.js_group_dresses)
    source.load()

    # load in the available inventory from the LTS report
    left_to_sell = DataFile(filename='data/LeftToSell.csv', schema=schema.left_to_sell_items)
    left_to_sell.load()

    # set up a list of colours
    colors = list();
    # file to keep the color names
    color_names = DataFile(filename='data/color_names.csv', schema=schema.color_names)

    # check for styles in the LTS data that are missing from the main dress list
    for lts_item in left_to_sell.data:
        lts_item_missing_in_main_data = True
        for main_item in source.data:
            if main_item["Style Number"] == lts_item["Style"]:
                lts_item_missing_in_main_data = False
                break
        if lts_item_missing_in_main_data:
            # print(lts_item["Style"], lts_item['Color Desc'])
            pass


    inventory = Inventory(left_to_sell.data)
    left_to_sell_data = LeftToSellData(left_to_sell.data)

    # initialize the output csv file.
    target = DataFile(filename='data/shopify_products.csv', schema=schema.shopify_product)

    # missing image list
    missing_image_list = DataFile(filename='data/prods_missing_images.csv', schema=schema.dresses_missing_images)

    # load the images from the gallery
    # **todo** modify to use boto to list all the files in the s3 bucket directly.
    # that way we don't need to keep the local directory and bucket in sync.
    gallery = ImageGallery(directory='data/images')

    # using the source data create a set of Product instances
    products = list()
    for item in source.data:
        product = Product(
            title=item['Dress Name'],
            handle=item['Handle'],
            body=item['Dress Description'],
            collection=item['Collection'],
            layout=item['Layout Format'],
            price=item['Price (USD)'],
            sale_price=item['Sale Price'],
            on_sale=item['On Sale'],
            permanent_markdown=item['Permanent Markdown'],
            never_markdown=item['Never Markdown'],
            style_number=item['Style Number'],
            oversell=item['Oversell'],
            waitlist=item['Waitlist'],
            fulfillment=item['Fulfillment'],
            is_published=True
        )
        product.add_option('Color', item['Colors'])
        # only add the sizes if they are not blank
        if item['Sizes']:
            product.add_option('Size', item['Sizes'])

        # add colors to the list of colours
        colors.extend(item['Colors'])

        if item['Waitlist']:
            product.add_tag('waitlist')

        if item['Tags']:
            for tag in item['Tags']:
                product.add_tag(tag)

        if product.layout:
            product.add_tag(product.layout)

        if product.is_on_sale():
            product.add_tag("Sale")

        product.populate_variants(inventory)

        products.append(product)

    # check inventory levels for each product
    # mark product as in stock if any variants have any stock
    for product in products:
        product.in_stock = False
        for variant in product.variants:
            if variant.quantity > 0:
                product.in_stock = True

    # using these Product instances create the target data matching the target schema
    for product in products:

        if product.in_stock or product.waitlist:
            # add to 'Shop' Collection
            product.product_type = 'Theia Shop'
        else:
            product.product_type = 'Theia Collection'

        # get the product images
        images = gallery.get_product_images(product.style_number)

        # don't add the product if it's missing an image.
        if len(images) == 0:
            product_missing_images = collections.OrderedDict()
            product_missing_images["Style Number"] = product.style_number
            product_missing_images["Dress Name"] = product.title
            product_missing_images["Collection"] = product.collection

            missing_image_list.data.append(product_missing_images)

            continue

        # default is None
        featured_image = None
        if len(images) > 0:
            # check for a front view image
            for i, img in enumerate(images):
                if 'front' in img.description:
                    featured_image = img
            # if nothing found then just set to the first image
            if featured_image == None:
                featured_image = img

        product_rows = list()

        # we will need x number of rows where x is equal to the number of
        # variants plus the number of extra product images (not associated
        # with a specific variant.

        first = True

        for variant in product.variants:

            row = collections.OrderedDict()

            # check for an image to use for this variant
            variant_color = variant.get_option_value_by_term('Color')

            variant_image = None
            for image in images:

                if image.color == variant_color and 'front' in image.description:
                    variant_image = image
                    break

            # if no variant_image skip this row and go to the next variant
            if variant_image == None:
                continue

            row["Handle"] = product.handle

            if first:
                first = False

                # 1st row is the general product data
                row["Title"] = product.title
                row["Body (HTML)"] = product.body
                row["Vendor"] = product.vendor
                row["Type"] = product.product_type
                row["Tags"] = product.tags
                row["Published"] = product.is_published
                # don't add the collection to the shopify_import file
                # we are using tags to organize the dresses
                row["Collection"] = '' # product.collection

                if variant_image == None:
                     row["Image Src"] = ''
                     row["Image Alt Text"] = ''
                else:
                    row["Image Src"] = variant_image.get_url()
                    row["Image Alt Text"] = variant_image.get_img_alt_data_string()

            # following rows are data for the variants

            # add each option
            for i, option in enumerate(variant.option_combo, start=1):
                option_name_header = "Option%s Name" % i
                option_value_header = "Option%s Value" % i

                # unpack the single item dictionary
                for k, v in option.items():
                    option_name = k
                    option_value = v

                row[option_name_header] = option_name
                row[option_value_header] = option_value

            row["Variant SKU"] = variant.sku
            row["Variant Inventory Tracker"] = "shopify"
            row["Variant Inventory Qty"] = variant.quantity
            row["Variant Inventory Policy"] = "continue" if product.oversell else "deny"
            row["Variant Fulfillment Service"] = product.fulfillment
            row["Variant Requires Shipping"] = True
            row["Variant Price"] = product.get_price()
            if product.is_on_sale():
                row["Variant Compare At Price"] = product.get_regular_price()

            # Weight unit and Variant Grams are independent of eachother
            row["Variant Weight Unit"] = 'lb' # used for displaying the weight
            row["Variant Grams"] = 900 # used inside Shopify, must always be in grams
            row["Variant Image"] = variant_image.get_url()

            # pprint(product)
            # pprint(row)

            product_rows.append(row)

        # additional rows are needed for extra images
        for img in images:
            row = collections.OrderedDict()
            row["Handle"] = product.handle
            row["Image Src"] = img.get_url()
            row["Image Alt Text"] = img.get_img_alt_data_string()
            product_rows.append(row)

        # add row(s) to the data file
        target.data += product_rows

    # split the color names separated with a /
    # and join the lists as a flat list with sum()
    colors = sum([ c.split('/', 1) for c in colors ], [])
    # get unique colors with set(), then create a sorted list
    colors = sorted(list(set(colors)))

    # store the color names in the DataFile instance
    import product_import.color_dictionary as color_dictionary
    for c in color_dictionary.colors:
        row = collections.OrderedDict()

        row["Color Name"] = c
        row["Hex Value"] = color_dictionary.find_hex_from_string(c)
        color_names.data.append(row)

    color_names.save()

    # write the colors to the csv file
    # save the target file
    target.save()

    # save the missing images.
    missing_image_list.save()

if __name__ == '__main__':
    # get command line args
    parser = argparse.ArgumentParser(description='Create a Shopify proudct import spreadsheet.')
    parser.add_argument('-i', '--input',
                        default='data/ForSaleTheiaDresses.csv',
                        dest='input_file')
    args = parser.parse_args()

    main(args.input_file)
