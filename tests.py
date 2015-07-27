from product_import.models import ImageGallery, Image, Product, Option, Variant, Inventory
from product_import.helpers import *
import unittest, os, csv, collections, shutil


class TestImageGallery(unittest.TestCase):
    def setUp(self):

        def touch(fname, times=None):
            with open(fname, 'a'):
                os.utime(fname, times)

        collection_paths = [
            './test_gallery/Test-2014',
            './test_gallery/Test-2015']

        for path in collection_paths:
            os.makedirs(path)

        images = {
            'Test-2014': [
                '882243_silverTaupe_front.jpg',
                '882234_tangerine_front.jpg',
                '882405_midnightAzure_from+front.jpg',
                '882301_aqua+splash_back.jpg'],
            'Test-2015': [
                '772243_someColor_front.jpg',
                '772234_single_front.jpg',
                '772405_anotherColor_testing+space.jpg',
                '772301_color+with+spaces_back.jpg']}

        for collection_name, filenames in images.iteritems():
            for filename in filenames:
                touch('./test_gallery/' + collection_name + '/' + filename)

    def tearDown(self):
        shutil.rmtree('./test_gallery')


    def test_parse_image_filename(self):
        filenames = [
            '882243_silverTaupe_front.jpg',
            '882234_tangerine_front.jpg',
            '882405_midnightAzure_from+front.jpg',
            '882301_aqua+splash_back.jpg'
        ]
        expected = [
            (882243, 'silver/taupe', 'front'),
            (882234, 'tangerine', 'front'),
            (882405, 'midnight/azure', 'from front'),
            (882301, 'aqua splash', 'back')
        ]
        results = list()

        for i, fn in enumerate(filenames):
            style_number, color, description = Image.parse_image_filename(fn)
            self.assertEqual(style_number, expected[i][0])
            self.assertEqual(color, expected[i][1])
            self.assertEqual(description, expected[i][2])

    def test_image_gallery_init(self):

        gallery = ImageGallery('./test_gallery/')

        self.assertIn('Test-2014', gallery.collections)
        self.assertIn('772234_single_front.jpg', gallery.files['Test-2015'])

    def test_load_images(self):

        gallery = ImageGallery('./test_gallery/')

        self.assertIsInstance(gallery.images[0], Image)

    def test_get_product_images(self):

        gallery = ImageGallery('./test_gallery/')

        image  = gallery.get_product_images(882301)

        self.assertEqual(image[0].filename, '882301_aqua+splash_back.jpg')

    def test_get_image_url(self):

        image = Image('234987_color+name_description.jpg', 'test')

        self.assertEqual(image.get_url(), 'http://cimocimocimo.s3.amazonaws.com/theia-images/test/234987_color%2Bname_description.jpg')

    def test_image_properties(self):

        filenames = [
            '882243_silverTaupe_front.jpg',
            '882234_tangerine_front.jpg',
            '882405_midnightAzure_from+front.jpg',
            '882301_aqua+splash_back.jpg'
        ]
        expected = [
            (882243, 'silver/taupe', 'front'),
            (882234, 'tangerine', 'front'),
            (882405, 'midnight/azure', 'from front'),
            (882301, 'aqua splash', 'back')
        ]

        for i, filename in enumerate(filenames):
            image = Image(filename, None)
            self.assertEqual(image.style_number, expected[i][0])
            self.assertEqual(image.color, expected[i][1])
            self.assertEqual(image.description, expected[i][2])


class TestProduct(unittest.TestCase):

    def setUp(self):
        self.test_product = Product(
            title="Test Product Title",
            body="<p>some content</p>",
            collection="Test Collection Name",
            price="999",
            style_number=123456,
            oversell=True,
            fulfillment='test-fulfilment',
            is_published=True
        )
        self.test_product.add_option('Size', ['S', 'M', 'L'])
        self.test_product.add_option('Color', ['Red', 'Blue'])
        pass

    def tearDown(self):
        pass

    def test_init(self):
        pass

    def test_populate_variants(self):

        self.test_product.populate_variants()

        self.assertIsInstance(self.test_product.variants, list)
        self.assertIsInstance(self.test_product.variants[0], Variant)
        self.assertEqual({'Size': 'S'}, self.test_product.variants[0].option_combo[0])
        self.assertEqual({'Color': 'Red'}, self.test_product.variants[0].option_combo[1])
        self.assertEqual('123456-S-Red', self.test_product.variants[0].sku)
        pass

class TestVariant(unittest.TestCase):
    def setUp(self):
        self.test_variant = Variant(
            option_combo=({'Size': 'S'}, {'Color': 'Blue'}),
            style_number=123456,
        )
        pass

    def tearDown(self):
        pass

    def test_init(self):
        """
        Given a set of options this options the Variant __init__ method should initialize the Variant instance.
        """
        blank_variant = Variant(0, tuple())
        self.assertEqual(tuple(), blank_variant.option_combo)
        self.assertEqual(0, blank_variant.style_number)
        self.assertEqual(None, blank_variant.sku)
        self.assertEqual(0, blank_variant.quantity)
        pass

    def test_generate_sku(self):
        self.test_variant.populate_sku()
        self.assertEqual('123456-S-Blue', self.test_variant.sku)
        self.assertEqual(0, self.test_variant.quantity)
        pass


class TestInventory(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_init(self):
        pass
        

if __name__ == '__main__':
    unittest.main()
