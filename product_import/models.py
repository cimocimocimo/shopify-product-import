import os, sys, csv, pprint, re, collections, urllib
import itertools
from slugify import slugify

from pprint import pprint

class Product:
    def __init__(
            self,
            title,
            body,
            collection,
            price,
            style_number,
            is_published):

        self.handle = slugify(title)
        self.title = title
        self.body = body
        self.vendor = 'Theia'
        self.product_type = 'Dress'
        self.collection = collection
        self.price = price
        self.style_number = style_number
        self.is_published = is_published
        self.tags = list()
        self.options = list()
        self.images = list()

    def __repr__(self):
        return "<Product handle:%s title:%s body:%s>" % (self.handle, self.title, self.body)

    def add_tag(self, tag):
        self.tags.append(tag)

    def add_option(self, name, values):
        self.options.append(Option(name, values))

    def get_variants(self):
        """
        generates a list of dicts for each product variant.
        """
        # get a list of dicts for each of the differnt options
        options_list = list()
        for option in self.options:
            tmp = list()
            for value in option.values:
                tmp.append({option.name: value})

            options_list.append(tmp)

        # generate a list of tuples for each product option combination
        combined_options = list(itertools.product(*options_list))

        # merge the dicitionaries stored in each tuple in the list and get the new list
        variants = [collections.OrderedDict(x[1].items() + x[0].items()) for x in combined_options]

        return combined_options

    def get_images():
        pass
        

class Option:
    def __init__( self, name, values ):
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
            headers = rows.next()
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
        for k, v in self.schema.columns.iteritems():
            headers.append(k)

        # create the rows of data to write to the file
        for row in self.data:
            for k, v in row.iteritems():
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

        for key, value in columns.iteritems():
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
        self.collections = os.listdir(self.directory)
        self.files = dict()
        self.images = list()

        for collection in self.collections:
            collection_dir = self.directory + '/' + collection
            self.files[collection] = os.listdir(collection_dir)
            self.load_images(self.files[collection], collection)

    def load_images(self, files, collection):
        """ Creates Image objects for all the files in the collection """

        for f in files:
            self.images.append(Image(f, collection))

    def get_product_images(self, style_number):
        return [ image for image in self.images if image.style_number == style_number ]



class Image:
    base_url = 'http://cimocimocimo.s3.amazonaws.com/theia-images/'

    def __init__(self, filename, collection):
        self.filename = filename
        self.collection = collection
        self.style_number, self.color, self.description = self.parse_image_filename(self.filename)

    def get_url(self):
        return self.base_url + self.collection + '/' + urllib.quote_plus(self.filename)

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

