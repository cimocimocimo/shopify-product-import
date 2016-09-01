import re, xlrd, csv

def list_of_int_from_str(s):
    return map(int, s.split(','))

def str_from_list(l):
    if isinstance(l, list):
        return ','.join(str(x) for x in l)
    else:
        return None

def list_split_strip(s):
    l = s.split(',')
    return [s.strip() for s in l]

def list_or_none_from_string(s):
    if s:
        l = s.split(',')
        return [s.strip() for s in l]
    else:
        return None

def int_from_str(s):
    my_int = 0

    # if blank string just return 0
    if s == '':
        return my_int

    # used for replaceing everthing that's not a digit or a decimal
    not_digit_or_dot = re.compile(r'[^\d.]+')
    my_int = not_digit_or_dot.sub('', s)

    # get everthing before the decimal
    my_int = my_int.split('.', 1)[0]

    return int(my_int)

def bool_from_str(s):
    s = s.lower()
    return s == 'true'

def bool_from_str_blank_true(s):
    if s == '':
        return True
    else:
        return bool_from_str(s)

def str_from_bool(b):
    return 'TRUE' if b else 'FALSE'

def two_place_float_from_str(s):
    not_digit_or_dot = re.compile(r'[^\d.]+')
    return round(float(not_digit_or_dot.sub('', s)), 2)

def spaces_to_underscores(s):
    space = re.compile(r'\s')
    return space.sub(r'_', s)

def forward_slash_to_mixedCase(s):
    return re.sub(r'/([a-zA-Z]?)', lambda m: m.group(1).upper(), s)

# converts xls file to csv
# args
# in_filename - .xls file
# sheet_name - sheet name to convert
# out_filename - .csv file to save
def convert_xls_to_csv(in_filename, sheet_name, out_filename):
    try:
        wb = xlrd.open_workbook(in_filename)
        sh = wb.sheet_by_name(sheet_name)
        csv_file = open(out_filename, 'wb')
    except IOError:
        return False

    wr = csv.writer(csv_file)

    for rownum in xrange(sh.nrows):
        wr.writerow(sh.row_values(rownum))

    csv_file.close()

    return True


