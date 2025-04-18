#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# This file is part of ofunctions package

"""
ofunctions.mailer is that nice email class that does all the security and bulk sending for you

Versioning semantics:
    Major version: backward compatibility breaking changes
    Minor version: New functionality
    Patch version: Backwards compatible bug fixes

"""

__intname__ = "ofunctions.mailer"
__author__ = "Orsiris de Jong"
__copyright__ = "Copyright (C) 2014-2025 Orsiris de Jong"
__description__ = "Mail sending class that handles encryption, authentication, bulk and split mail sending"
__licence__ = "BSD 3 Clause"
__version__ = "1.2.2"
__build__ = "2025040401"
__compat__ = "python2.7+"

import logging
import os
import re
import smtplib
import socket
import ssl
import sys
from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid

# Python 2.7 compat fixes
try:
    from typing import Union, List, Optional
except ImportError:
    pass

try:
    SMTPNotSupportedError = smtplib.SMTPNotSupportedError
except AttributeError:

    class SMTPNotSupportedError(smtplib.SMTPConnectError):
        pass


if sys.version_info[0] < 3:

    class ConnectionError(OSError):
        pass

    class ConnectionRefusedError(ConnectionError):
        pass

    class ConnectionAbortedError(ConnectionError):
        pass

    class ConnectionResetError(ConnectionError):
        pass


logger = logging.getLogger(__intname__)


class Mailer:
    """
    :param sender_mail:
    :param recipient_mails: Accepts space, comma or semi-colon separated email addresses or list of email addresses
    :param split_mails: When multiple mails exist, shall we create an email per address or an unique one
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

    def __init__(
        self,
        smtp_server="localhost",  # type: str
        smtp_port=25,  # type: int
        smtp_user=None,  # type: str
        smtp_password=None,  # type: str
        security=None,  # type: Optional[str]
        verify_certificates=True,  # type: bool
        hostname=None,  # type: Optional[str]
        encoding="utf-8",  # type: str
        debug=False,  # type: bool
    ):
        # type: (...) -> None
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.security = security
        self.verify_certificates = verify_certificates
        self.hostname = hostname
        self.encoding = encoding
        self.debug = debug

        # Fix for empty passed auth strings
        if self.smtp_user is not None and len(smtp_user) == 0:
            smtp_user = None
        if smtp_password is not None and len(smtp_password) == 0:
            smtp_password = None

    def send_email(
        self,
        sender_mail=None,  # type: str
        recipient_mails=None,  # type: Union[str, List[str]]
        subject=None,  # type: str
        body=None,  # type: str
        attachment=None,  # type: str
        filename=None,  # type: str
        html_enabled=False,  # type: bool
        bcc_mails=None,  # type: str
        priority=False,  # type: bool
        split_mails=False,  # type: bool
    ):
        # (...) -> bool
        if subject is None:
            logger.warning(
                "No subject set for mail from {} to {}.".format(
                    sender_mail, recipient_mails
                )
            )

        if recipient_mails is None:
            raise ValueError("No destination mails set")

        def _send_email(
            recipient_mail,  # type: Union[str,List[str]]
        ):
            # type: (...) -> bool
            """
            Actual mail sending function
            """

            # Create a multipart message and set headers
            message = MIMEMultipart()
            message["From"] = sender_mail
            if isinstance(recipient_mail, list):
                message["To"] = ",".join(recipient_mail)
            else:
                message["To"] = recipient_mail
            message["Date"] = formatdate(localtime=False)
            message["LocalDate"] = formatdate(localtime=True)
            message["Message-Id"] = make_msgid()
            message["Subject"] = Header(subject, self.encoding)
            message["Subject"] = subject

            if bcc_mails is not None:
                message["Bcc"] = bcc_mails  # Recommended for mass emails

            if priority:
                message["X-Priority"] = "2"
                message["X-MSMail-Priority"] = "High"

            # Add body to email
            if body is not None:
                if html_enabled:
                    message.attach(MIMEText(body, "html", self.encoding))
                else:
                    message.attach(MIMEText(body, "plain", self.encoding))

            if attachment is not None: #Use Multiples Attachments to your mail if needed
                if isinstance(attachment, (bytes, bytearray)):
                    attachment_list = [attachment]
                    att_filename_list = [filename] if filename else [None]
                elif isinstance(attachment, str):
                    attachment_list = [attachment]
                    att_filename_list = [filename if filename else os.path.basename(attachment)]
                elif isinstance(attachment, list):
                    attachment_list = attachment
                    if isinstance(filename, str):
                        att_filename_list = [filename] * len(attachment_list)
                    else:
                        att_filename_list = [os.path.basename(file_path) for file_path in attachment_list]
                else:
                    attachment_list = []
                    att_filename_list = []

                for each_attachment, each_filename in zip(attachment_list, att_filename_list):
                    if isinstance(each_attachment, (bytes, bytearray)):
                        payload = each_attachment
                        att_filename = each_filename if each_filename else "attachment.bin"
                    else:
                        with open(each_attachment, "rb") as f_attachment:
                            payload = f_attachment.read()
                        att_filename = each_filename if each_filename else os.path.basename(each_attachment)

                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(payload)
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", "attachment; filename=%s" % att_filename)
                    message.attach(part)


            text = message.as_string()

            try:
                if self.security and self.security.lower() in ["ssl", "tls"]:
                    context = ssl.create_default_context()
                    if not self.verify_certificates:
                        context.check_hostname = False
                        context.verify_mode = False

                if self.security and self.security.lower() == "ssl":
                    remote_server = smtplib.SMTP_SSL(
                        self.smtp_server,
                        self.smtp_port,
                    )
                else:
                    # Standard SMTP transaction without security
                    remote_server = smtplib.SMTP(self.smtp_server, self.smtp_port)

                # Now go ahead and play the transaction
                if self.debug:
                    remote_server.set_debuglevel(True)
                remote_server.ehlo(self.hostname)
                if self.security == "tls":
                    remote_server.starttls()
                    remote_server.ehlo(self.hostname)
                if self.smtp_user is not None and self.smtp_password is not None:
                    remote_server.login(self.smtp_user, self.smtp_password)
                remote_server.sendmail(sender_mail, recipient_mail, text)

            # SMTPNotSupportedError = Server does not support STARTTLS
            # SMTPNotSupportedError does not exist in Python 2.x
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
                socket.error,  # Python 2 error on bad port
                SMTPNotSupportedError,  # Python 2 error when TLS is required
                ssl.SSLError,
            ) as exc:
                logger.error("Cannot send email: %s", exc, exc_info=True)
                return False
            return True

        if not isinstance(recipient_mails, list):
            # Make sure recipient mails is a list
            recipient_mails = re.split(r",|;| ", recipient_mails)

        # Strip extra chars around mail addresses
        recipient_mails = [mail.strip() for mail in recipient_mails]

        rfc822_addresses = [mail for mail in recipient_mails if is_mail_address(mail)]
        non_rfc822_addresses = [
            mail for mail in recipient_mails if mail not in rfc822_addresses
        ]

        result = True

        if split_mails:
            for recipient in rfc822_addresses:
                _result = _send_email(recipient)
                if not _result:
                    result = _result
        else:
            _result = _send_email(rfc822_addresses)
            if not _result:
                result = _result

        if not non_rfc822_addresses == []:
            logger.error("Refused non RFC 822 mails: %s", format(non_rfc822_addresses))
            result = False

        return result


def is_mail_address(
    string,  # type: bool
):
    # type: (...) -> bool
    """
    Check email address validity against simpler than RFC822 regex
    """
    if re.match(r"[^@\s]+@[^@\s]+\.[a-zA-Z0-9][a-zA-Z0-9]+$", string):
        return True
    return False


def send_email(
    source_mail=None,  # type: str
    destination_mails=None,  # type: Union[str, List[str]]
    split_mails=False,  # type: bool
    smtp_server="localhost",  # type: str
    smtp_port=25,  # type: int
    smtp_user=None,  # type: str
    smtp_password=None,  # type: str
    security=None,  # type: Optional[str]
    subject=None,  # type: str
    body=None,  # type: str
    attachment=None,  # type: str
    filename=None,  # type: str
    html_enabled=False,  # type: bool
    bcc_mails=None,  # type: str
    priority=False,  # type: bool
    debug=False,  # type: bool
):
    # type: (...) -> Union[bool, str]
    """
    Wrapper for compat with earlier ofunctions.mailer
    """

    mailer = Mailer(
        smtp_server=smtp_server,
        smtp_port=smtp_port,
        smtp_user=smtp_user,
        smtp_password=smtp_password,
        security=security,
        debug=debug,
    )

    result = mailer.send_email(
        sender_mail=source_mail,
        recipient_mails=destination_mails,
        split_mails=split_mails,
        subject=subject,
        body=body,
        attachment=attachment,
        filename=filename,
        html_enabled=html_enabled,
        bcc_mails=bcc_mails,
        priority=priority,
    )

    return result
