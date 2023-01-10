#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# This file is part of ofunctions module

"""
Versioning semantics:
    Major version: backward compatibility breaking changes
    Minor version: New functionality
    Patch version: Backwards compatible bug fixes
"""


__intname__ = "tests.ofunctions.misc"
__author__ = "Orsiris de Jong"
__copyright__ = "Copyright (C) 2023 Orsiris de Jong"
__licence__ = "BSD 3 Clause"
__build__ = "2023011001"


from ofunctions.misc import *


def test_bytesconverter():
    

    x = BytesConverter(1024)
    assert x.bits == 8192, 'Bogus BytesConverter result for 1024: {}'.format(x.bits)
    assert x.kbytes == 1, 'Bogus ByesConverter result for 1024: {}'.format(x.kbytes)

    x = BytesConverter("50GB")
    assert x.human == '50.0 GB', 'Bogus human conversion for 50GB: {}'.format(x.human)
    assert x == 50000000000, 'Bogus byte conversion for 50GB: {}'.format(x)

    x = BytesConverter("50GiB")
    assert x.human == '53.7 GB', 'Bogus human conversion for 50GB: {}'.format(x.human)
    assert x == 53687091200, 'Bogus byte conversion for 50GB: {}'.format(x)

    assert BytesConverter(2049).kbytes == 2
    assert BytesConverter(1000000000000).tbits == 7.2
    assert BytesConverter(4350580).human == "4.4 MB"
    assert BytesConverter("64 KiB") == 65536
    assert BytesConverter("64 KB") == 64000
    assert BytesConverter("64 Kib") == 65536 / 8
    assert BytesConverter("64 Kb") == 64000 / 8

    x = BytesConverter("20MB")
    print(x.human)
    print(x.human_iec_bytes)
    print(x.human_bits)
    print(x.human_iec_bits)
    assert x.human == "20.0 MB"
    assert x.human_iec_bytes == "19.1 MiB"
    assert x.human_bits == "160.0 Mb"
    assert x.human_iec_bits == "152.6 Mib"

    assert BytesConverter(0).mbits == 0
    assert BytesConverter('0 b') == 0
    assert BytesConverter('0 EB') == 0


if __name__ == "__main__":
    print("Example code for %s, %s" % (__intname__, __build__))
    test_bytesconverter()