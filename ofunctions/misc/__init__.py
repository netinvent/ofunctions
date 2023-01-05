#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# This file is part of ofunctions package

"""
ofunctions is a general library for basic repetitive tasks that should be no brainers :)

Versioning semantics:
    Major version: backward compatibility breaking changes
    Minor version: New functionality
    Patch version: Backwards compatible bug fixes

"""

__intname__ = "ofunctions.misc"
__author__ = "Orsiris de Jong"
__copyright__ = "Copyright (C) 2014-2023 Orsiris de Jong"
__description__ = "Collection of various functions"
__licence__ = "BSD 3 Clause"
__version__ = "1.5.0"
__build__ = "2023010501"
__compat__ = "python2.7+"


# python 2.7 compat fixes
try:
    from typing import Optional, List, Any
except ImportError:
    pass


# Restrict number n between minimum and maximum
restrict_numbers = lambda n, n_min, n_max: max(min(n_max, n), n_min)


def rot13(string):
    # type: (str) -> str
    """
    Rot13 for only A-Z and a-z characters
    """
    return "".join(
        [
            chr(ord(n) + (13 if "Z" < n < "n" or n < "N" else -13))
            if ("a" <= n <= "z" or "A" <= n <= "Z")
            else n
            for n in string
        ]
    )


def _rot47(string):
    # type: (str) -> str
    """
    rot47 for alphanumeric characters
    """
    x = []
    for i in range(len(string)):
        j = ord(string[i])
        if 33 <= j <= 126:
            x.append(chr(33 + ((j + 14) % 94)))
        else:
            x.append(string[i])
    return "".join(x)


def bytes_to_string(bytes_to_convert, strip_null=False):
    # type: (List[int], bool) -> Optional[str]
    """
    Litteral bytes to string
    :param bytes_to_convert: list of bytes in integer format
    :param strip_null: Remove trailing and ending null bytes
    :return: resulting string
    """
    try:
        value = "".join(chr(i) for i in bytes_to_convert)
        if strip_null:
            return value.strip("\x00")
        return value
    # AttributeError when None object has no strip attribute
    except (ValueError, TypeError, AttributeError):
        return None


def time_is_between(current_time, time_range):
    # type: (str, tuple) -> bool
    """
    https://stackoverflow.com/a/45265202/2635443
    print(is_between("11:00", ("09:00", "16:00")))  # True
    print(is_between("17:00", ("09:00", "16:00")))  # False
    print(is_between("01:15", ("21:30", "04:30")))  # True
    """

    if time_range[1] < time_range[0]:
        return current_time >= time_range[0] or current_time <= time_range[1]
    return time_range[0] <= current_time <= time_range[1]


def reverse_dict(dictionary):
    # type: (dict) -> dict
    """
    Return a reversed dictionary ie {value: key}
    """
    return {value: key for key, value in dictionary.items()}


def get_key_from_value(haystack, needle):
    # type: (dict, str) -> str
    """
    Returns a dict key by it's value, ie get_key_from_value({key: value}, value) returns key
    """
    return next((k for k, v in haystack.items() if v == needle), None)


def deep_dict_update(dict_original, dict_update):
    # type: (dict, dict) -> dict
    """
    Update a nested dictionnary with another nested dictionnary
    Balant copy from https://stackoverflow.com/a/60435617/2635443
    """
    if isinstance(dict_original, dict) and isinstance(dict_update, dict):
        output = dict(dict_original)
        keys_original = set(dict_original.keys())
        keys_update = set(dict_update.keys())
        similar_keys = keys_original.intersection(keys_update)
        similar_dict = {
            key: deep_dict_update(dict_original[key], dict_update[key])
            for key in similar_keys
        }
        new_keys = keys_update.difference(keys_original)
        new_dict = {key: dict_update[key] for key in new_keys}
        output.update(similar_dict)
        output.update(new_dict)
        return output
    else:
        return dict_update


def is_nan(var):
    # type: (Any) -> bool
    """
    Simple check if a variable is a numpy NaN
    based on the simple check where (nan is nan) gives True but (nan == nan) gives False
    """
    return not var == var


class BytesConverter(float):
    """
    float subclass that adds multiple properties in order to make computer guys life easier
    Internal always reasons in byte unit represented as float
    So why float ? Because on multiple python versions, int is limited to 2**32, which is only 4GB

    Converting bytes to other units:

    kilobytes = BytesConverter(2049).kbytes
    print(kilobytes)
    > 2

    terabits = BytesConverter(1000000000000).tbits
    print(terabits)
    > 7.2

    Getting human readable output

    print(BytesConverter(4350580).human)
    > 4.1 MB
    Getting bytes from human readable input

    print(BytesConverter("64 KB"))
    > 65536
    """

    byte_units = ["EB", "PB", "TB", "GB", "MB", "KB", "B"]
    bits_units = ["Eb", "Pb", "Tb", "Gb", "Mb", "Kb", "b"]
    units = {
        "b": 8,
        "B": 1,
        "KB": 1024,
        "Kb": 1024,
        "MB": 1024**2,
        "Mb": 1024**2,
        "GB": 1024**3,
        "Gb": 1024**3,
        "TB": 1024**4,
        "Tb": 1024**4,
        "PB": 1024**5,
        "Pb": 1024**5,
        "EB": 1024**6,
        "Eb": 1024**6,
    }

    def __new__(cls, value, *args, **kwargs):
        """
        Creates a new int type object
        We can give an int parameter (which will be bytes) or a str parameter (like '500KB') which will be translated to bytes
        """

        # If a string was given, we'll try to convert it's unit to bytes
        if isinstance(value, str):
            converted_value = None
            for unit in cls.byte_units + cls.bits_units:
                result = value.split(unit)
                if len(result) == 2:
                    converted_value = float(result[0]) * cls.units[unit]
                    if unit in cls.bits_units:
                        converted_value /= 8
                    break
            if not converted_value:
                try:
                    converted_value = float(value)
                except ValueError:
                    pass
                raise ValueError(
                    'Given string "{}" cannot be converted to bytes'.format(value)
                )
            value = converted_value
        if value < 0:
            raise ValueError("Negative bytes should not exist")
        return super(cls, cls).__new__(cls, value)

    def _from_units_to_bytes(self, string):
        # Check if we have value:
        value = None
        for unit in self.byte_units + self.bits_units:
            result = string.split(unit)
            if len(result) == 2:
                value = float(result[0]) * self.units[unit]
                if unit in self.bits_units:
                    value /= 8
                break
        if not value:
            try:
                return float(string)
            except ValueError:
                pass
            raise ValueError(
                'Given string "{}" cannot be converted to bytes'.format(string)
            )
        return value

    def _from_bytes_to_unit(self, unit):
        result = round(self / self.units[unit], 1)
        if unit in self.bits_units:
            result *= 8
        return result

    @property
    def bytes(self):
        return self

    @property
    def bits(self):
        return round(self * 8, 0)

    @property
    def kbytes(self):
        return self._from_bytes_to_unit("KB")

    @property
    def kbits(self):
        return self._from_bytes_to_unit("Kb")

    @property
    def mbytes(self):
        return self._from_bytes_to_unit("MB")

    @property
    def mbits(self):
        return self._from_bytes_to_unit("Mb")

    @property
    def gbytes(self):
        return self._from_bytes_to_unit("GB")

    @property
    def gbits(self):
        return self._from_bytes_to_unit("Gb")

    @property
    def tbytes(self):
        return self._from_bytes_to_unit("TB")

    @property
    def tbits(self):
        return self._from_bytes_to_unit("Tb")

    @property
    def pbytes(self):
        return self._from_bytes_to_unit("PB")

    @property
    def pbits(self):
        return self._from_bytes_to_unit("Pb")

    @property
    def ebytes(self):
        return self._from_bytes_to_unit("EB")

    @property
    def ebits(self):
        return self._from_bytes_to_unit("Eb")

    def _to_human(self, units):
        """
        Converts an int / float to a human readable format with less than 5 significant digits
        """
        for unit in units:
            operation = self.units[unit]

            result = self / operation
            if unit in self.bits_units:
                result *= 8
            
            # Check whether the int part of our result is to small
            if len(str(result).split("e-")) == 2:
                continue
            integer_result = str(result).split(".")[0]
            if integer_result == "0":
                continue
            if len(integer_result) <= 4:
                return "{} {}".format(round(result, 1), unit)
        return "{} {}".format(result, unit)

    @property
    def human_bytes(self):
        return self._to_human(self.byte_units)

    @property
    def human(self):
        return self.human_bytes

    @property
    def human_bits(self):
        return self._to_human(self.bits_units)
