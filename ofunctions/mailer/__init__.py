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

__intname__ = "ofunctions.mailer"
__author__ = "Orsiris de Jong"
__copyright__ = "Copyright (C) 2014-2021 Orsiris de Jong"
__description__ = "Mail sending function that handles encryption, authentication, bulk and split mail sending"
__licence__ = "BSD 3 Clause"
__version__ = "0.3.5"
__build__ = "2021020902"

import logging
import os
import re
import smtplib
import socket
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Union, List

logger = logging.getLogger("__intname__")


def send_email(
    source_mail: str = None,
    destination_mails: Union[str, List[str]] = None,
    split_mails: bool = False,
    smtp_server: str = "localhost",
    smtp_port: int = 25,
    smtp_user: str = None,
    smtp_password: str = None,
    security: Union[str, None] = None,
    subject: str = None,
    body: str = None,
    attachment: str = None,
    filename: str = None,
    html_enabled: bool = False,
    bcc_mails: str = None,
    priority: bool = False,
    debug: bool = False,
) -> Union[bool, str]:
    """

    :param source_mail:
    :param destination_mails: Accepts space, comma or semi-colon separated email addresses or list of email addresses
    :param split_mails: When multiple mails exist, shall we create an email per addresss or an unique one
    :param smtp_server:
    :param smtp_port:
    :param smtp_user:
    :param smtp_password:
    :param security:
    :param subject:
    :param body:
    :param attachment: (str/bytes): Path to file, or inline binary data
    :param filename: (str):  specified filename in case we use inline binary data
    :param html_enabled:
    :param bcc_mails:
    :param priority: (bool) set to true to add a high priority flag
    :param debug:
    :return:
    """

    if subject is None:
        raise ValueError("No subject set")

    # Fix for empty passed auth strings
    if smtp_user is not None and len(smtp_user) == 0:
        smtp_user = None
    if smtp_password is not None and len(smtp_password) == 0:
        smtp_password = None

    if destination_mails is None:
        raise ValueError("No destination mails set")

    def _send_email(destination_mail: str) -> bool:
        """
        Actual mail sending function
        """
        nonlocal filename

        # Create a multipart message and set headers
        message = MIMEMultipart()
        message["From"] = source_mail
        message["To"] = destination_mail
        message["Subject"] = subject

        if bcc_mails is not None:
            message["Bcc"] = bcc_mails  # Recommended for mass emails

        if priority:
            message["X-Priority"] = "2"
            message["X-MSMail-Priority"] = "High"

        # Add body to email
        if body is not None:
            if html_enabled:
                message.attach(MIMEText(body, "html"))
            else:
                message.attach(MIMEText(body, "plain"))

        if attachment is not None:
            if isinstance(attachment, bytes):
                # Let's suppose we directly attach binary data
                payload = attachment
            else:
                with open(attachment, "rb") as f_attachment:
                    payload = f_attachment.read()
                    filename = os.path.basename(attachment)

            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(payload)

            # Encode file in ASCII characters to send by email
            encoders.encode_base64(part)

            # Add header as key/value pair to attachment part
            part.add_header(
                "Content-Disposition",
                "attachment; filename=%s" % filename,
            )

            # Add attachment to message and convert message to string
            message.attach(part)

        text = message.as_string()

        try:
            if security == "ssl":
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(
                    smtp_server, smtp_port, context=context
                ) as remote_server:
                    if debug:
                        remote_server.set_debuglevel(True)
                    remote_server.ehlo()
                    if smtp_user is not None and smtp_password is not None:
                        remote_server.login(smtp_user, smtp_password)
                    remote_server.sendmail(source_mail, destination_mails, text)

            elif security == "tls":
                # TLS
                context = ssl.create_default_context()
                with smtplib.SMTP(smtp_server, smtp_port) as remote_server:
                    if debug:
                        remote_server.set_debuglevel(True)
                    remote_server.ehlo()
                    remote_server.starttls(context=context)
                    remote_server.ehlo()
                    if smtp_user is not None and smtp_password is not None:
                        remote_server.login(smtp_user, smtp_password)
                    remote_server.sendmail(source_mail, destination_mails, text)

            else:
                with smtplib.SMTP(smtp_server, smtp_port) as remote_server:
                    if debug:
                        remote_server.set_debuglevel(True)
                    remote_server.ehlo()
                    if smtp_user is not None and smtp_password is not None:
                        remote_server.login(smtp_user, smtp_password)
                    remote_server.sendmail(source_mail, destination_mails, text)
        # SMTPNotSupportedError = Server does not support STARTTLS
        except (
            smtplib.SMTPAuthenticationError,
            smtplib.SMTPSenderRefused,
            smtplib.SMTPRecipientsRefused,
            smtplib.SMTPDataError,
            ConnectionRefusedError,
            ConnectionAbortedError,
            ConnectionResetError,
            ConnectionError,
            socket.gaierror,
            smtplib.SMTPNotSupportedError,
            ssl.SSLError,
        ) as exc:
            logger.error("Cannot send email: %s", exc, exc_info=True)
            return False
        return True

    if not isinstance(destination_mails, list):
        # Make sure destination mails is a list
        destination_mails = re.split(r",|;| ", destination_mails)

    rfc822_addresses = [mail for mail in destination_mails if is_mail_address(mail)]
    non_rfc822_addresses = [
        mail for mail in destination_mails if mail not in rfc822_addresses
    ]

    result = True

    if not split_mails:
        for destination_mail in rfc822_addresses:
            _result = _send_email(destination_mail)
            if not _result:
                result = _result
    else:
        _result = _send_email(",".join(rfc822_addresses))
        if not _result:
            result = _result

    if non_rfc822_addresses == []:
        logger.error("Refused non RFC 822 mails: %s", format(non_rfc822_addresses))
        result = False

    return result


def is_mail_address(string: str) -> bool:
    """
    Check email address validity against simpler than RFC822 regex
    """
    if re.match(r"[^@\s]+@[^@\s]+\.[a-zA-Z0-9][a-zA-Z0-9]+$", string):
        return True
    return False
