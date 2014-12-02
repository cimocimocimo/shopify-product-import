import re

def list_of_int_from_str(s):
    return map(int, s.split(','))

def str_from_list(l):
    return ','.join(str(x) for x in l)

def list_split_strip(s):
    l = s.split(',')
    return [s.strip() for s in l]

def int_from_string(s):
    not_digit_or_dot = re.compile(r'[^\d.]+')
    return int(not_digit_or_dot.sub('', s))

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

