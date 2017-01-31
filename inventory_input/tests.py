from django.test import TestCase
from django.conf import settings
import shopify, dropbox

from pprint import pprint

# Dropbox tests
class DropboxTestCase(TestCase):

    test_folder_path = '/testing'

    @classmethod
    def setUpClass(cls):
        cls.dbx = dropbox.Dropbox(settings.DROPBOX_TOKEN)
        # create test folder
        cls.dbx.files_create_folder(cls.test_folder_path)
        cls.dbx.files_upload('test', cls.test_folder_path + '/file1.txt')

    @classmethod
    def tearDownClass(cls):
        cls.dbx.files_delete(cls.test_folder_path)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_latest_files_from_folder(self):
        new_filename = 'file2.txt'

        # get file list
        results = self.dbx.files_list_folder(self.test_folder_path)

        # add a file
        self.dbx.files_upload('test', self.test_folder_path + '/' + new_filename)

        # get new file list
        new_results = self.dbx.files_list_folder_continue(results.cursor)

        # check for the new file
        self.assertEqual(new_filename, new_results.entries[0].name)


    def test_list_folder(self):
        result = self.dbx.files_list_folder(settings.DROPBOX_EXPORT_FOLDER)
        self.assertIsInstance(result, dropbox.files.ListFolderResult)


    def test_init_dropbox_file_cache(self):

        pass
