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


__intname__ = "tests.ofunctions.mailer"
__author__ = "Orsiris de Jong"
__copyright__ = "Copyright (C) 2020-2024 Orsiris de Jong"
__licence__ = "BSD 3 Clause"
__build__ = "2022041601"


from ofunctions.mailer import *


def test_mailer():
    mailer = Mailer(smtp_server="localhost", smtp_port=25000)
    result = mailer.send_email(
        sender_mail="me@them.com",
        recipient_mails="me@them.or",
        subject="test",
        body="Here is some sleek body",
    )
    print("We don't really send mails here.")
    assert result is False, "We will not really test this but it sure must fail"


def test_is_mail_address():
    valid = ["me@them.hop", "some@example.org", "herew_we@are.now", "t@td.ff"]
    invalid = ["m@t", "mee@them.t", "s@xlk"]

    for mail in valid:
        assert (
            is_mail_address(mail) is True
        ), "Valid mail address check failed: {} = {}".format(
            mail, is_mail_address(mail)
        )
    for mail in invalid:
        assert (
            is_mail_address(mail) is False
        ), "Invalid mail address check succeed: {} = {}".format(
            mail, is_mail_address(mail)
        )


if __name__ == "__main__":
    print("Example code for %s, %s" % (__intname__, __build__))
    test_is_mail_address()
    test_mailer()
