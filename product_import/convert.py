import schema
from models import *

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

    test = DataFile(filename='test.csv', schema=schema.js_group_dress)
    test.data = source.data
    test.save()

    # using the source data create a set of Product instances

    # using these Product instances create the target data matching the target schema

    # save the target file
    target.save()

if __name__ == '__main__':
    main()
