from product_import.models import ImageGallery, Image, Product, Option, Variant, Inventory
# from product_import.helpers import *
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

        for collection_name, filenames in images.items():
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
            '882301_aqua+splash_back.jpg',
            '882243_silverTaupe_swatch.jpg',
            '882234_tangerine_swatch.jpg',
        ]
        expected = [
            (882243, 'silver/taupe', 'front', 'productImage'),
            (882234, 'tangerine', 'front', 'productImage'),
            (882405, 'midnight/azure', 'from front', 'productImage'),
            (882301, 'aqua splash', 'back', 'productImage'),
            (882243, 'silver/taupe', 'swatch', 'swatch'),
            (882234, 'tangerine', 'swatch', 'swatch'),
        ]

        for i, filename in enumerate(filenames):
            image = Image(filename, None)
            self.assertEqual(image.style_number, expected[i][0])
            self.assertEqual(image.color, expected[i][1])
            self.assertEqual(image.description, expected[i][2])
            self.assertEqual(image.image_type, expected[i][3])

    def test_img_alt_data_string(self):
        
        filenames = [
            '882243_silverTaupe_front.jpg',
            '882234_tangerine_front.jpg',
            '882405_midnightAzure_from+front.jpg',
            '882301_aqua+splash_back.jpg',
            '882243_silverTaupe_swatch.jpg',
            '882234_tangerine_swatch.jpg',
        ]
        expected = [
            "color%PAIR%silver/taupe%ITEM%type%PAIR%productImage%DATA%front",
            "color%PAIR%tangerine%ITEM%type%PAIR%productImage%DATA%front",
            "color%PAIR%midnight/azure%ITEM%type%PAIR%productImage%DATA%from front",
            "color%PAIR%aqua splash%ITEM%type%PAIR%productImage%DATA%back",
            "color%PAIR%silver/taupe%ITEM%type%PAIR%swatch%DATA%swatch",
            "color%PAIR%tangerine%ITEM%type%PAIR%swatch%DATA%swatch",
        ]

        for i, filename in enumerate(filenames):
            image = Image(filename, None)
            self.assertEqual(image.get_img_alt_data_string(), expected[i])
            
            
class TestProduct(unittest.TestCase):

    def setUp(self):
        self.test_product = Product(
            title="Test Product Title",
            handle="Test Product Handle",
            body="<p>some content</p>",
            collection="Test Collection Name",
            layout="test product layout",
            price=999,
            sale_price=759,
            on_sale=False,
            permanent_markdown=False,
            never_markdown=False,
            style_number=123456,
            oversell=True,
            waitlist=False,
            fulfillment='test-fulfilment',
            is_published=True
        )
        self.test_product.add_option('Size', ['S', 'M', 'L'])
        self.test_product.add_option('Color', ['Red', 'Blue'])
        
        self.test_product_sale = Product(
            title="Test Product On Sale",
            handle="Test Product Handle",
            body="<p>some content</p>",
            collection="Test Collection Name",
            layout="test product layout",
            price=999,
            sale_price=759,
            on_sale=True,
            permanent_markdown=False,
            never_markdown=False,
            style_number=123457,
            oversell=False,
            waitlist=False,
            fulfillment='test-fulfilment',
            is_published=True
        )
        self.test_product_sale.add_option('Size', ['S', 'M', 'L'])
        self.test_product_sale.add_option('Color', ['Green', 'Yellow'])
        
        self.test_product_never_markdown = Product(
            title="Test Product Never Markdown",
            handle="Test Product Handle",
            body="<p>some content</p>",
            collection="Test Collection Name",
            layout="test product layout",
            price=999,
            sale_price=759,
            on_sale=True,
            permanent_markdown=True,
            never_markdown=True,
            style_number=123458,
            oversell=False,
            waitlist=False,
            fulfillment='test-fulfilment',
            is_published=True
        )
        self.test_product_sale.add_option('Size', ['S', 'M', 'L'])
        self.test_product_sale.add_option('Color', ['Orange', 'Pink'])
        
        
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
    
    def test_get_price(self):
        self.assertEqual(self.test_product.get_price(), 999)
        
    def test_sale_price(self):
        self.assertEqual(self.test_product_sale.get_price(), 759)
        
    def test_get_regular_price(self):
        self.assertEqual(self.test_product_sale.get_regular_price(), 999)

    def test_is_on_sale(self):
        self.assertEqual(self.test_product.is_on_sale(), False)
        self.assertEqual(self.test_product_sale.is_on_sale(), True)
        self.assertEqual(self.test_product_never_markdown.is_on_sale(), False)
        
        
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
