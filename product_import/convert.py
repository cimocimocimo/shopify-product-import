import collections
import schema
from models import *
import pprint

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


def main():

    # open the data files and unserialze the data according to their schema
    source = DataFile(filename='data/TheiaDresses.csv', schema=schema.js_group_dresses)
    source.load()

    # load in the available inventory from the LTS report
    left_to_sell = DataFile(filename='data/LeftToSell.csv', schema=schema.left_to_sell_items)
    left_to_sell.load()

    inventory = Inventory(left_to_sell.data)

    # initialize the output csv file.
    target = DataFile(filename='data/shopify_products.csv', schema=schema.shopify_product)

    # load the images from the gallery
    # **todo** modify to use boto to list all the files in the s3 bucket directly.
    # that way we don't need to keep the local directory and bucket in sync.
    gallery = ImageGallery(directory='data/images')

    # using the source data create a set of Product instances
    products = list()
    for item in source.data:
        product = Product(
            title=item['Dress Name'],
            body=item['Dress Description'],
            collection=item['Collection'],
            price=item['Price (USD)'],
            style_number=item['Style Number'],
            oversell=item['Oversell'],
            fulfillment=item['Fulfillment'],
            is_published=True
        )
        product.add_option('Size', item['Sizes'])
        product.add_option('Color', item['Colors'])
        if item['Waitlist']:
            product.add_tag('waitlist')
        product.populate_variants(inventory)

        products.append(product)

    # remove products that have no instock variants and are not in the Sprint 2015 collection
    for product in products:

        product.in_stock = False
        for variant in product.variants:
            if variant.quantity > 0:
                product.in_stock = True
        

    # using these Product instances create the target data matching the target schema
    for product in products:

        # we are not selling the out of stock items on the site so we don't add them to the export
        # we are only preselling the spring 2015 collection
        if not product.in_stock and product.collection != 'Spring 2015':
            print('continue')
            continue

        images = gallery.get_product_images(product.style_number)
        for i, img in enumerate(images):
            if 'front' in img.description:
                featured_image = images.pop(i)

        product_rows = list()

        # we will need x number of rows where x is equal to the number of
        # variants plus the number of extra product images (not associated
        # with a specific variant.

        first = True

        for variant in product.variants:

            row = collections.OrderedDict()

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

                row["Image Src"] = featured_image.get_url()
                row["Image Alt Text"] = featured_image.description

            # following rows are data for the variants

            # add each option
            for i, option in enumerate(variant.option_combo, start=1):
                option_name_header = "Option%s Name" % i
                option_value_header = "Option%s Value" % i

                # unpack the single item dictionary
                for k, v in option.iteritems():
                    option_name = k
                    option_value = v

                row[option_name_header] = option_name
                row[option_value_header] = option_value

                # if option_name == 'Color':
                #     for i, img in enumerate(images):
                #         if option_value == img.color and img.description == 'front':
                #             row['Variant Image'] = img.get_url()
                #             break

            row["Variant SKU"] = variant.sku
            row["Variant Inventory Tracker"] = "shopify"
            row["Variant Inventory Qty"] = variant.quantity
            row["Variant Inventory Policy"] = "continue" if product.oversell else "deny"
            row["Variant Fulfillment Service"] = product.fulfillment
            row["Variant Requires Shipping"] = True
            row["Variant Price"] = product.price

            product_rows.append(row)

        # additional rows are needed for extra images
        for img in images:
            row = collections.OrderedDict()
            row["Handle"] = product.handle
            row["Image Src"] = img.get_url()
            row["Image Alt Text"] = img.description
            product_rows.append(row)


        # add row(s) to the data file
        target.data += product_rows


    # save the target file
    target.save()

if __name__ == '__main__':
    main()
