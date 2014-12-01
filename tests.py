import product_import.convert
import unittest
import os
import csv

class TestDataFile(unittest.TestCase):
    def setUp(self):
        self.test_data = [
            ['heading','row','has','stuff'],
            ['this','is','test','data']
        ]
        with open('test.csv', 'w+') as f:
            w = csv.writer(f)
            w.writerows(self.test_data)

    def tearDown(self):
        os.remove('test.csv')

    def test_file_open(self):
        test_file = product_import.convert.DataFile('test.csv')
        test_file.load()

        self.assertEqual(test_file.data, self.test_data)

class TestConverter(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_converter_init(self):
        pass

if __name__ == '__main__':
    unittest.main()
p
