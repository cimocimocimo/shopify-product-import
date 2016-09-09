import os, sys, csv, pprint, re, collections
from urllib.parse import quote_plus
import itertools
from slugify import slugify
# import helpers
from .helpers import *

from pprint import pprint

class Product:
    def __init__(
            self,
            title,
            handle,
            body,
            collection,
            layout,
            price,
            sale_price,
            on_sale,
            permanent_markdown,
            never_markdown,
            style_number,
            oversell,
            waitlist,
            fulfillment,
            is_published):
        
        if handle:
            self.handle = handle
        else:
            self.handle = slugify(title)
        self.title = title
        self.body = body
        self.vendor = 'Theia'
        self.product_type = 'Dress'
        self.collection = collection
        self.layout = layout
        self.price = price
        self.sale_price = sale_price
        self.permanent_markdown = permanent_markdown
        self.never_markdown = never_markdown
        self.on_sale = on_sale
        self.style_number = style_number
        self.oversell = oversell
        self.waitlist = waitlist
        self.fulfillment = fulfillment
        self.is_published = is_published

        self.variants = list()
        self.tags = list()
        self.options = list()
        self.images = list()

        self.add_tag(self.style_number)
        self.add_tag(self.collection)
        # add the collection name without the year as a tag as well.
        split_collection_year = re.compile('(.*)\s+(\d{4}$)')
        coll_year_match = split_collection_year.search(self.collection)
        if coll_year_match != None:
            collection_name = coll_year_match.group(1)
            collection_year = coll_year_match.group(2)
            self.add_tag(collection_name)
            self.add_tag(collection_year)
        if not "Bridal" in self.collection:
            self.add_tag('Collections')
        else:
            self.add_tag('Bridal')
        
    def __repr__(self):
        return "<Product handle:%s title:%s body:%s>" % (self.handle, self.title, self.body)

    def add_tag(self, tag):
        self.tags.append(tag)

    def add_option(self, name, values):
        self.options.append(Option(name, values))

    def populate_variants(self, inventory=None):
        """
        generates a list of dicts for each product variant.
        """
        self.variants = list()

        option_combos = self.generate_option_combos()

        for combo in option_combos:
            self.variants.append(Variant(
                self.style_number,
                option_combo=combo,
                inventory=inventory))

    def generate_option_combos(self):
        """
        returns a list of all possible cominations of product options
        each option combo is of the form:
        ({'Option Name': 'Option Value'}, ...)
        """
        available_options = list()
        for option in self.options:
            # generate a list of dicts for every value of the option
            tmp = list()
            for value in option.values:
                tmp.append({option.name: value})

            available_options.append(tmp)

        # generate a list of tuples for each product option combination
        option_combos = list(itertools.product(*available_options))

        return option_combos

    def get_images(self):
        pass
    
    def get_price(self):
        if self.is_on_sale():
            return self.sale_price
        else:
            return self.price
        
    def get_regular_price(self):
        return self.price

    def is_on_sale(self):
        if self.never_markdown:
            return False
        else:
            return self.permanent_markdown or self.on_sale
        
class Variant:
    """
    Defines a unique combination of the product's options.
    """
    def __init__(self, style_number, option_combo, inventory=None):
        self.style_number = style_number
        self.option_combo = option_combo
        self.populate_sku()
        if inventory != None:
            self.get_quantity_from_inventory(inventory)
        else:
            self.quantity = 0

    def populate_sku(self):
        """
        From the given options and style number create a sku 
        sku starts with the style number
        """
        options = dict()
        for option in self.option_combo:
            for k, v in option.items():
                options[k] = v

        if (self.style_number != None and
            'Size' in options and
            'Color' in options):
            self.sku = generate_sku(self.style_number, options['Size'], options['Color'])
        else:
            self.sku = None

    def get_quantity_from_inventory(self, inventory):
        self.quantity = inventory.get_quantity(self.sku)

    def option_term_exists(self, term):
        for option in self.option_combo:
            for k, v in option.items():
                if k == term:
                    return True
        return False

    def get_option_value_by_term(self, term):
        if self.option_term_exists(term):
            for option in self.option_combo:
                for k, v in option.items():
                    if k == term:
                        return v
        return None

def generate_sku(style_number, size, color):

    color = spaces_to_underscores(str(color))
    color = forward_slash_to_mixedCase(color)

    sku_parts = [
        str(style_number),
        str(size),
        str(color)
    ]

    return '-'.join(sku_parts)


class Option:
    """
    Defines the range of all possible values for a specific Product Option.
    """
    def __init__(self, name, values):
        self.name = name
        self.values = values


class DataFile:
    """
    Opens a text csv file and creates a two dimentional array containing the data.
    """
    def __init__(self, filename, schema):
        self.filename = filename
        self.schema = schema
        self.columns = list()
        self.data = list()

    def map_columns(self, headers):
        # map each column's schema for each column that is in the data
        for i, header in enumerate(headers):
            self.columns.append(self.schema.columns[header])

    def load(self):
        try:
            f = open(self.filename, 'r')
        except IOError:
            return
        
        rows = csv.reader(f)
        try:
            headers = next(rows)
        except StopIteration:
            return
        
        self.map_columns(headers)

        # load the data according to the loaded schema
        for row in csv.reader(f):
            item = collections.OrderedDict()
            for i, column in enumerate(row):
                item[self.columns[i].name] = self.columns[i].load(column)
            self.data.append(item)

        f.close()

    def save(self):

        # create a list of the column headers for the csv file
        headers = list()
        for k, v in self.schema.columns.items():
            headers.append(k)

        # create the rows of data to write to the file
        for row in self.data:
            for k, v in row.items():
                # call the appropriate save function for each column according to the schema
                row[k] = self.schema.columns[k].save(v)
            
        # save the processed data
        with open(self.filename, 'w+') as f:
            w = csv.DictWriter(f, fieldnames=headers)
            w.writeheader()
            w.writerows(self.data)


class Schema:
    """
    Encapsulates the logic for reading and writing each CSV format.
    describes how each of the columns in the rows of a CSV file map
    to Products and vice versa.
    """

    def __init__(self, columns):
        self.columns = collections.OrderedDict()

        for key, value in columns.items():
            self.columns[key] = Column(key, value[0], value[1])
    
class Column:
    def __init__(self, name, load_fn, save_fn):
        self.name = name

        if callable(load_fn):
            self.load = load_fn
        else:
            self.load = lambda x: x

        if callable(save_fn):
            self.save = save_fn
        else:
            self.save = lambda x: x


class ImageGallery:
    """
    Contains all the images for the products and their variants
    """

    def __init__(self, directory=None):
        if directory is None:
            return

        self.directory = directory.rstrip('/')
        self.collections = list(listdir_nohidden(self.directory))
        self.files = dict()
        self.images = list()

        for collection in self.collections:
            collection_dir = self.directory + '/' + collection
            self.files[collection] = list(listdir_nohidden(collection_dir))
            self.load_images(self.files[collection], collection)

    def load_images(self, files, collection):
        """ Creates Image objects for all the files in the collection """

        for f in files:
            self.images.append(Image(f, collection))

    def get_product_images(self, style_number):
        return [ image for image in self.images if image.style_number == style_number ]
    
    def get_tags(self, style_number):
        # all images should have the same collection so we only need one.
        images = self.get_product_images(style_number)
        return

class Image:
    base_url = 'http://cimocimocimo.s3.amazonaws.com/theia-images/'

    def __init__(self, filename, collection):
        self.filename = filename
        self.collection = collection
        self.style_number, self.color, self.description = self.parse_image_filename(self.filename)
        if self.description.startswith('swatch'):
            self.image_type = 'swatch'
        else:
            self.image_type = 'productImage'

    def get_url(self):
        return self.base_url + self.collection + '/' + quote_plus(self.filename)

    def get_img_alt_data_string(self):
        """
        creates a data packed string like this:
        'color%PAIR%blue%ITEM%type%PAIR%swatch%DATA%This is the alt text'
        unpacked in the shopify strings
        """
        return 'color%PAIR%{}%ITEM%type%PAIR%{}%DATA%{}'.format(self.color, self.image_type, self.description)
    
    @staticmethod
    def parse_image_filename(filename):
        """ Pulls out the data from the image filename. """
        
        # regexes
        starts_with_six_digits = re.compile(r'^\d{6}')
        capital_letter = re.compile(r'([A-Z]{1})')
        plus = re.compile(r'\+')

        # split the filename and extention
        filename, extension = os.path.splitext(filename)
        style_number, color, description = filename.split('_')

        style_number = int(style_number)

        # decode the color
        # intCaps -> int/caps
        color = capital_letter.sub(r'/\1', color).lower()
        # plus+to+space -> plus to space
        color = plus.sub(r' ', color)

        # decode the description
        description = plus.sub(r' ', description)

        return style_number, color, description
    
class LeftToSellData:
    """
    Contains the data from the left to sell spreadsheet
    """

    def __init__(self, data):
        """
        loads the left to sell data
        """
        self.products = dict()
        for item in data:
            style_number = item["Style"]
            
            if style_number not in self.products:
                product = {"price": item["price"]}
                self.products[style_number] = product
                
    def get_price(self, style_number):
        if style_number in self.products:
            return self.products[style_number]["price"]
    
    
class Inventory:
    """
    contains the inventory information for all the available inventory provided in the Left To Sell report.
    """

    def __init__(self, data):
        """
        loads the DataFile
        """
        self.items = dict()
        for item in data:

            key = generate_sku(item['Style'], item['Size Desc'], item['Color Desc'])
            value = item['Left to Sell']

            self.items[key] = value


    def get_quantity(self, sku):
        """
        returns an int of the available inventory in the LTS report or 0 if not found.
        """

        try:
            quantity = self.items[sku]
        except KeyError:
            quantity = 0

        return quantity

def listdir_nohidden(path):
    for f in os.listdir(path):
        if not f.startswith('.'):
            yield f
