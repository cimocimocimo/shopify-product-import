from django.db import models

# Dropbox Files

# Need to get all the files in the folder on the first init

# Only need to get the changed files since the last time we checked

# dropbox file
class DropboxFile(models.Model):
    '''
    id – A unique identifier for the file.
    server_modified – The last time the file was modified on Dropbox.
    size – The file size in bytes.
    name – The last component of the path (including extension). This never contains a slash.
    path_lower – The lowercased full path in the user’s Dropbox. This always starts with a slash. This field will be null if the file or folder is not mounted.
    path_display – The cased path to be used for display purposes only. In rare
    instances the casing will not correctly match the user’s filesystem, but this
    behavior will match the path provided in the Core API v1. Changes to the casing
    of paths won’t be returned by
    dropbox.dropbox.Dropbox.files_list_folder_continue(). This field will be null if
    the file or folder is not mounted.
    '''
    file_id = models.CharField(max_length=4096)
    server_modified = models.DateTimeField()
    size = models.BigIntegerField()
    name = models.CharField(max_length=4096)
    path_lower = models.CharField(max_length=4096)
    path_display = models.CharField(max_length=4096)

# cursors
