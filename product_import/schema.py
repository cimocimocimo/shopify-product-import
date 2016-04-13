import collections
from models import Schema
from helpers import *

color_names = Schema(collections.OrderedDict([
    ("Color Name", (str, str)),
    ("Hex Value", (str, str)),
]))

# each row maps to a variant of a product.
left_to_sell_items = Schema(collections.OrderedDict([
    ("Style", (int, int)),
    ("Color", (str, str)),
    ("Color Desc", (str, str)),
    ("Size Desc", (int, int)),
    ("Left to Sell", (int, int)),
    ("price", (int_from_str, int)),
]))

# each row maps to a product with lists of options.
js_group_dresses = Schema(collections.OrderedDict([
    ("Style Number", (int, int)),
    ("Dress Name", (str, str)),
    ("Handle", (str, str)),
    ("Dress Description", (str, str)),
    ("Collection", (str, str)),
    ("Layout Format", (str, str)),
    ("Oversell", (bool_from_str, str_from_bool)),
    ("Waitlist", (bool_from_str, str_from_bool)),
    ("Fulfillment", (str, str)),
    ("Sizes", (list_of_int_from_str, str_from_list)),
    ("Colors", (list_split_strip, str_from_list)),
    ("Price (USD)", (int_from_str, int)),
    ("Sale Price", (int_from_str, int)),
    ("On Sale", (bool_from_str, str_from_bool)),
    ("Permanent Markdown", (bool_from_str, str_from_bool)),
    ("Tags", (list_or_none_from_string, str_from_list)),
]))

shopify_product = Schema(collections.OrderedDict([
    ("Handle", (str, str)),
    ("Title", (str, str)),
    ("Body (HTML)", (str, str)),
    ("Vendor", (str, str)),
    ("Type", (str, str)),
    ("Tags", (list_split_strip, str_from_list)),
    ("Collection", (str, str)),
    ("Published", (bool_from_str_blank_true, str_from_bool)),
    ("Image Src", (str, str)),
    ("Image Alt Text", (str, str)),
    ("SEO Title", (str, str)),
    ("SEO Description", (str, str)),
    ("Option1 Name", (str, str)),
    ("Option1 Value", (str, str)),
    ("Option2 Name", (str, str)),
    ("Option2 Value", (str, str)),
    ("Option3 Name", (str, str)),
    ("Option3 Value", (str, str)),
    ("Variant SKU", (str, str)),
    ("Variant Grams", (int, int)),
    ("Variant Inventory Tracker", (str, str)),
    ("Variant Inventory Qty", (int, int)),
    ("Variant Inventory Policy", (str, str)),
    ("Variant Fulfillment Service", (str, str)),
    ("Variant Price", (two_place_float_from_str, None)),
    ("Variant Compare At Price", (two_place_float_from_str, None)),
    ("Variant Requires Shipping", (bool_from_str, str_from_bool)),
    ("Variant Taxable", (bool_from_str, str_from_bool)),
    ("Variant Barcode", (str, str)),
    ("Variant Image", (str, str)),
    ("Variant Weight Unit", (None, None)),
    ("Gift Card", (None, None)),
    ("Google Shopping / MPN", (None, None)),
    ("Google Shopping / Age Group", (None, None)),
    ("Google Shopping / Gender", (None, None)),
    ("Google Shopping / Google Product Category", (None, None)),
    ("Google Shopping / AdWords Grouping", (None, None)),
    ("Google Shopping / AdWords Labels", (None, None)),
    ("Google Shopping / Condition", (None, None)),
    ("Google Shopping / Custom Product", (None, None)),
    ("Google Shopping / Custom Label 0", (None, None)),
    ("Google Shopping / Custom Label 1", (None, None)),
    ("Google Shopping / Custom Label 2", (None, None)),
    ("Google Shopping / Custom Label 3", (None, None)),
    ("Google Shopping / Custom Label 4", (None, None))
]))

# each row maps to a product with lists of options.
dresses_missing_images = Schema(collections.OrderedDict([
    ("Style Number", (int, int)),
    ("Dress Name", (str, str)),
    ("Collection", (str, str)),
]))
