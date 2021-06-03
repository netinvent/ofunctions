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
- mailer: send emails regardless of ssl/tls protocols, in batch or as single mail, with attachments
- network: various tools like ping, internet check, MTU probing and public IP discovery
- platform: nothing special here, just check what arch we are running on
- process: simple kill-them-all function to terminate subprocesses
- random: basic random string & password generator
- service_control: control Windows / Linux service start / stop / status
- string_handling: remove accents / special chars from strings
- threading: threading decorator for functions

It is compatible with Python 3.5+ and is tested on both Linux and Windows.

## Setup

```
pip install ofunctions.<subpackage>

```
