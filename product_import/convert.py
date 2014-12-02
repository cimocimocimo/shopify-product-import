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


def main(argv = None):

    # get input and output filenames
    if argv is None:
        argv = sys.argv

    # open the data files and unserialze the data according to their schema
    source = DataFile(filename=argv[1], schema=schema.js_group_dress)
    source.load()

    target = DataFile(filename=argv[2], schema=schema.shopify_product)

    # using the source data create a set of Product instances
    products = list()
    for item in source.data:
        product = Product(
            title=item['Dress Name'],
            body=item['Dress Description'],
            collection=item['Collection'],
            price=item['Price (USD)'],
            is_published=True
        )
        product.add_tag(item['Style Number'])
        product.add_tag(item['Collection'])
        product.add_option('Size', item['Sizes'])
        product.add_option('Color', item['Colors'])
        
        products.append(product)

    # using these Product instances create the target data matching the target schema
    for product in products:

        # get a list of all combinations of the product options
        variants = product.get_variants()

        product_rows = list()

        # we will need x number of rows where x is equal to the number of
        # variants plus the number of extra product images (not associated
        # with a specific variant.

        first = True
        for variant in variants:

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

            # following rows are data for the variants

            # add each option
            for i, option in enumerate(variant, start=1):
                option_name_header = "Option%s Name" % i
                option_value_header = "Option%s Value" % i

                # unpack the single item dictionary
                for k, v in option.iteritems():
                    option_name = k
                    option_value = v

                row[option_name_header] = option_name
                row[option_value_header] = option_value

            row["Variant Inventory Tracker"] = "shopify"
            row["Variant Inventory Qty"] = 100
            row["Variant Inventory Policy"] = "deny"
            row["Variant Fulfillment Service"] = "manual"
            row["Variant Price"] = product.price

            product_rows.append(row)

        # the first variant should be merged into the main product row

        # additional rows are needed for extra images

        



        # add row(s) to the data file
        target.data += product_rows


    # save the target file
    target.save()

if __name__ == '__main__':
    main()
