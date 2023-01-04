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
- network: various tools like ping, internet check, MTU probing, public IP discovery, network interface IO counters
- platform: nothing special here, just check what arch we are running on
- process: simple kill-them-all function to terminate subprocesses
- random: basic random string & password generator
- service_control: control Windows / Linux service start / stop / status
- string_handling: remove accents / special chars from strings
- threading: threading decorator for functions, also contains a function call anti-flood system

ofunctions is compatible with Python 2.7 and 3.5+ and is tested on both Linux and Windows.
There are still two subpackages that will only work with Python 3.5+
- delayed_keyboardinterrupt (signal handling is different in Python 2.7)
- threading (we don't have concurrent_futures in python 2.7, so the @threaded decorator will indeed work, but can't return a result)


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

ofunctions.logger_utils is an easy implementation of logger which promises to always work, regardless of encoding issues.
Easy usage:
```
from ofunctions.logger_utils import logger_get_logger

logger = logger_get_logger(log_file='/path/to/log/file')
```

logger_utils will automatically try to open a temp log file if given log_file is not writable.
You can also disable console output with `console=False`, enable debug_mode with `debug=True` (or later with `logger.setLevel(logging.DEBUG)`).
Also allows to inject more LOGGER formatter objects, eg:
```
logger = logger_get_logger(formatter_insert="%(processName)s")
```

logger_utils also allows to know what was the worst loglevel that has been called in your program:

```
from ofunctions.logger_utils import logger_get_logger, get_worst_logger_level

logger = logger_get_logger()
logger.error("Oh no !")

print("worst log level was :", get_worst_logger_level())  # 10-50, 10 = debug, 50 = critical
```


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

## misc Usage

Misc is a collection of somehow useful functions.

Example: BytesConverter

BytesConverter is that little tool that you want when handling bits and byte units.
Internally, BytesConverter always represents data an int number of bytes.
BytesConverter will return a float or a str if human output is requested.

Example:

```
from ofunctions.misc import BytesConverter

print(BytesConverter(1234))
print(BytesConverter(1234).bits)
print(BytesConverter(1234).kbytes)
print(BytesConverter(1234).human)
print(BytesConverter(65535).kbytes)
print(BytesConverter(9000000).mbytes)
print(BytesConverter("4MB"))
print(BytesConverter("9600 Kb").mbytes)

```

Output will be:
```
1234
9872
1.2
1.2 KB
64
8.6
4194304
1.2
```

Arithmetics:
```
print(BytesConverter("50 MB") + BytesConverter("8192 Kb"))
print(BytesConverter(BytesConverter("50 MB") + BytesConverter("8192 Kb")).human)
```

Output
```
53477376
51.0 MB
```

## network Usage

ofunctions.network is a collection of various tools making network diag / mapping easier.

Setup:
```commandline
pip install ofunctions.network
```

### IOCounters

IOCounters is a class that will log instant sent/received bytes as well as total sent/received bytes.
Once an instance is created, logging begins as a thread.
You may specify which interfaces to track at which resolution.
If none is given, all interfaces are tracked every second.

Example of IO counters for network interfaces:
```python
counter = IOCounters()
while True:
    print(counter.interfaces['eth0'].recv_bytes, counter.interfaces['eth0'].recv_bytes_total)
    time.sleep(1)
```

```python
counter = IOCounters(['Ethernet Connection 2', 'Wi-Fi'], resolution=2)
while True:
    print(counter.interfaces['Ethernet Connection 2'].sent_bytes)
    time.sleep(1)
```

## platform Usage

## process Usage

## random Usage

## service_control Usage

## string_handling Usage

## threading Usage

### @threaded

threading comes with a couple of decorators that allow to modify functions.
In order to thread a function, you can simply apply the `@threaded` decorator like below.

Once you call the function, it will automatically be threaded, and you get to keep your execution flow.
You can then execute whatever you want, or wait for it's result:

```
@threaded
def my_nice_function():
   # Do some nice stuff
   return result
   
def main():
   # Some stuff
   thread = my_nice_function()
   # Some other stuff being executed while my_nice_function runs in a thread
   # now let's wait for my function result
   result = thread.result()
```

Remember that Python 2.7 can't give you a result, so the function will be threaded, but without any possible return codes.

### @no_flood

There are situations where some code can call multiple times the same function (on a trigger for example), but you don't want that function to run multiple times.
That's a situation where we should handle function call antiflooding.

Example:
```
# Adding @no_flood(5) only allows one execution of my_function per 5 seconds

@no_flood(5)
def my_function():
    print("Hey, it's me !")
  
# Will run my_function() only once
for _ in range(0, 20):
    my_function()
```

Multiple executions of a functions are permitted as long as they're called with different arguments.
The `@no_flood` decorator can be setup to prevent **any** multiple function execution in a given timespan, regarless of it's arguments:

```
@no_flood(5, multiple_instances_diff_args=False)
@def my_function(var):
    print("Hey, it's me: {}".format(var))

# Will run my_function() only once
for i in range(0, 20):
    my_function(i)
```
