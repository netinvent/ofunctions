# ofunctions
## Collection of useful python functions

[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Percentage of issues still open](http://isitmaintained.com/badge/open/netinvent/ofunctions.svg)](http://isitmaintained.com/project/netinvent/ofunctions "Percentage of issues still open")
[![Maintainability](https://api.codeclimate.com/v1/badges/d82ea82db47d8a91c5b6/maintainability)](https://codeclimate.com/github/netinvent/ofunctions/maintainability)
[![codecov](https://codecov.io/gh/netinvent/ofunctions/branch/master/graph/badge.svg?token=WKQQHGHTO8)](https://codecov.io/gh/netinvent/ofunctions)
[![linux-tests](https://github.com/netinvent/ofunctions/actions/workflows/linux.yaml/badge.svg)](https://github.com/netinvent/ofunctions/actions/workflows/linux.yaml)
[![windows-tests](https://github.com/netinvent/ofunctions/actions/workflows/windows.yaml/badge.svg)](https://github.com/netinvent/ofunctions/actions/workflows/windows.yaml)
[![GitHub Release](https://img.shields.io/github/release/netinvent/ofunctions.svg?label=Latest)](https://github.com/netinvent/ofunctions/releases/latest)

ofunctions is a set of various recurrent functions amongst

- bisection: bisection algorithm for *any* function with *any* number of arguments, works LtoR and RtoL
- checksums: various SHA256 tools for checking and creating checksum files
- csv: CSV file reader with various enhancements over generic reader
- delayed_keyboardinterrupt: just a nifty tool to catch CTRL+C signals
- file_utils: file handling functions of which
  - get_paths_recursive: Walks a path for directories / files, can deal with permission errors, has include / exclude lists with wildcard support...
  - check_path_access: Checks whether a path is writable, with fallback for read test, and splits path until it finds which part denies permissions
  - check_file_timestamp_delta: Check a time delta (seconds, minutes, hours...) against file ctime, mtime or atime
  - hide_file: Hides/unhides files under windows & linux
  - get_writable_temp_dir: Returns a temporary dir in which we are allowed to write
  - get_writable_random_file: Returns a filename of a not-yet existing file we can write into
- json_sanitize: make sure json does not contain unsupported chars, yes I look at you Windows eventlog
- logger_utils: basic no brain console + file log creation
- mailer: A class to deal with email sending, regardless of ssl/tls protocols, in batch or as single mail, with attachments
- network: various tools like ping, internet check, MTU probing and public IP discovery
- platform: nothing special here, just check what arch we are running on
- process: simple kill-them-all function to terminate subprocesses
- random: basic random string & password generator
- service_control: control Windows / Linux service start / stop / status
- string_handling: remove accents / special chars from strings
- threading: threading decorator for functions

ofunctions is compatible with Python 2.7 and 3.5+ and is tested on both Linux and Windows.
There are still two subpackages that will only work with Python 3.5+
- delayed_keyboardinterrupt (signal handling is different in Python 2.7)
- threading (we don't have concurrent_futures in python 2.7)


## Setup

```
pip install ofunctions.<subpackage>

```

## bisection Usage

ofunctions.bisection is a dichotomy algorithm that can be used for all kind of bisections, mathematical operations, kernel bisections...
Let's imagine we have a function foo that takes argument x.
x might be between 0 and 999, and for a given value of x above 712, foo(x) returns "gotcha".
In order to find at which x value foo(x) becomes "gotcha", we could run foo(x) for every possible value of x until the result becomes what we expect.
The above solution works, but takes time (up to 1000 foo(x) runs).
We can achieve the same result in max 10 steps by checking foo(x) where x will be the middle of all possible values.
Looking at the result from that middle value, we'll know if the expected result should be a lower or higher value of x. We can repeat this action until we'll get the precise result.

Now let's code the above example in less abstract:
```
def foo(x):
	# We'll need to find value 712 te quickest way possible
	if x >= 712:
		return "gotcha"
	return False

from ofunctions.bisection import bisect

value = bisect(foo, range(0, 1000), expected_result="gotcha")
print('Value is %s' % value)
```

The above concept can be adapted in order to compute ethernet MTU values or whatever other values need to be calculated.
See ofunctions.network code for MTU probing example.


## checksums Usage

## csv Usage

## delayed_keyboardinterrupt Usage

The DelayedKeyboardInterrupt class allows to intercept a CTRL+C call in order to finish atomic operations without interruption.
Easy to use, we use a pythonic syntax as follows:

Setup:
```
pip install ofunctions.mailer
```

Usage:
```
with DelayedKeyboardInterrupt():
	<your code that should not be interrupted>
```
## file_utils Usage

ofuntions.file_utils is a collection of tools to handle:
- listing of paths

Setup
```
pip install ofunctions.file_utils
```

## json_sanitize Usage

json_sanitize will remove any control characters from json content (0x00-0x1F and 0x7F-0x9F) of which some are usually non printable and non visible.
This is especially useful when dealing with various log files (ex: windows event logs) that need to be passed as json.
It will also remove dots from value names, since those are prohibited in json standard.

Setup:
```
pip install ofunctions.json_sanitize
```

Usage:
```
my_json = {'some.name': 'some\tvalue'}
my_santized_json = json_sanitize(my_json)
```
my_santized_json will contain `{'somename': 'somevalue'}`

## logger_utils Usage

## mailer Usage

ofunctions.mailer is a simple mailing class and a rfc822 email validation function.

Setup:
```
pip install ofunctions.mailer
```

Quick usage:
```
from ofunctions.mailer import Mailer

mailer = Mailer()  # Uses localhost:25
mailer.send_email(subject='test', sender_mail='me@example.com', recipient_mails='them@example.com', body='some body just told me')
```

SmartRelay usage:
```
from ofunctions.mailer import Mailer

mailer = Mailer(smtp_server='mail.example.com', smtp_port=587, security='tls', smtp_user='me', smtp_password='secure_p@$$w0rd_lol')
mailer.send_email(subject='test', sender_mail='me@example.com', recipient_mails='them@example.com ; another_recipient@example.com', body='some body just told me')
```

Bulk mailer usage:
```
from ofunctions.mailer import Mailer

recipients = ['me@example.com', 'them@example.com', 'anyone@example.com', 'malformed_address_at_example.com']

mailer = Mailer(smtp_server='mail.example.com', smtp_port=465, security='ssl', debug=True, verify_certificates=False)

# split_mails=True will send one email per recipient
# split_mails=False will send one email for all recipients, which will be limited to the number of recipients the destination SMTP server allows
mailer.send_email(subject='test', sender_mail='me@example.com', recipient_mails=recipients, body='some body just told me', split_mails=True)
```

Attachment usage:
```
from ofunctions.mailer import Mailer

mailer = Mailer()  # Uses localhost:25

# attachment can be a binary blob or a file path
# filename is optional, and will rename a binary blob to something more meaningful
mailer.send_email(subject='test', sender_mail='me@example.com', recipient_mails='them@example.com', body='some body just told me', attachment=attachment, filename='My Attachment File.txt')
```

## network Usage

## platform Usage

## process Usage

## random Usage

## service_control Usage

## string_handling Usage

## threading Usage