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
__copyright__ = "Copyright (C) 2020-2025 Orsiris de Jong"
__licence__ = "BSD 3 Clause"
__build__ = "2025050201"


from ofunctions.mailer import *


# The following settings need to be overridden by an import file in prod tests
# Of course, we cannot send mails on github actions

SMTP_SERVER = "localhost"
SMTP_PORT = 587
SMTP_USER = ""
SMTP_PASSWORD = ""
SECURITY = "tls"  # or "ssl" or None
SENDER_MAIL = "some@one.tld"
RECIPIENT_MAIL = "single@example.tld"
RECIPIENT_MAILS = ["one@example.tld", "two@example.tld"]
ATTACHMENT = [__file__]
FILENAME = [__file__]
ATTACHMENTS = [b"ABC", b"DEF"]
BODY = "Here is some sleek body"


try:
    from test_mailer_config import *
except ImportError:
    print("No test_mailer_config.py found, using default settings")


def test_mailer():
    mailer = Mailer(smtp_server=SMTP_SERVER, smtp_port=SMTP_PORT, smtp_user=SMTP_USER, smtp_password=SMTP_PASSWORD, security=SECURITY)
    result = mailer.send_email(
        sender_mail=SENDER_MAIL,
        recipient_mails=RECIPIENT_MAIL,
        subject="test test_mailer",
        body=BODY,
    )

    if SMTP_PASSWORD:
        assert result is True, "When set, we should have a valid result"
    else:
        print("We don't really send mails here.")
        assert result is False, "We will not really test this but it sure must fail"


def test_mailer_multi_recipient():
    mailer = Mailer(smtp_server=SMTP_SERVER, smtp_port=SMTP_PORT, smtp_user=SMTP_USER, smtp_password=SMTP_PASSWORD, security=SECURITY)
    result = mailer.send_email(
        sender_mail=SENDER_MAIL,
        recipient_mails=RECIPIENT_MAILS,
        subject="test test_mailer_multi_recipient",
        body=BODY,
    )

    if SMTP_PASSWORD:
        assert result is True, "When set, we should have a valid result"
    else:
        print("We don't really send mails here.")
        assert result is False, "We will not really test this but it sure must fail"


def test_mailer_multi_recipient_split():
    mailer = Mailer(smtp_server=SMTP_SERVER, smtp_port=SMTP_PORT, smtp_user=SMTP_USER, smtp_password=SMTP_PASSWORD, security=SECURITY)
    result = mailer.send_email(
        sender_mail=SENDER_MAIL,
        recipient_mails=RECIPIENT_MAILS,
        subject="test test_mailer_multi_recipient_split",
        body=BODY,
        split_mails=True,
    )
    if SMTP_PASSWORD:
        assert result is True, "When set, we should have a valid result"
    else:
        print("We don't really send mails here.")
        assert result is False, "We will not really test this but it sure must fail"

def test_mailer_single_attachment():
    mailer = Mailer(smtp_server=SMTP_SERVER, smtp_port=SMTP_PORT, smtp_user=SMTP_USER, smtp_password=SMTP_PASSWORD, security=SECURITY)
    result = mailer.send_email(
        sender_mail=SENDER_MAIL,
        recipient_mails=RECIPIENT_MAIL,
        attachment=ATTACHMENT,
        filename=FILENAME,
        subject="test test_mailer_single_attachment",
        body=BODY,
    )
    
    if SMTP_PASSWORD:
        assert result is True, "When set, we should have a valid result"
    else:
        print("We don't really send mails here.")
        assert result is False, "We will not really test this but it sure must fail"  


def test_mailer_multi_attachment():
    mailer = Mailer(smtp_server=SMTP_SERVER, smtp_port=SMTP_PORT, smtp_user=SMTP_USER, smtp_password=SMTP_PASSWORD, security=SECURITY)
    result = mailer.send_email(
        sender_mail=SENDER_MAIL,
        recipient_mails=RECIPIENT_MAIL,
        attachment=ATTACHMENTS,
        subject="test test_mailer_multi_attachment",
        body=BODY,
    )
    if SMTP_PASSWORD:
        assert result is True, "When set, we should have a valid result"
    else:
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
    test_mailer_multi_recipient()
    test_mailer_multi_recipient_split()
    test_mailer_single_attachment()
    test_mailer_multi_attachment()