# ofunctions
## Collection of useful python functions

[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Percentage of issues still open](http://isitmaintained.com/badge/open/netinvent/ofunctions.svg)](http://isitmaintained.com/project/netinvent/ofunctions "Percentage of issues still open")
![Linux Build Status](https://github.com/netinvent/ofunctions/workflows/ofunctions-linux-tests/badge.svg)
[![GitHub Release](https://img.shields.io/github/release/netinvent/ofunctions.svg?label=Latest)](https://github.com/netinvent/ofunctions/releases/latest)

ofunctions is a set of various recurrent functions amongst

- bisection: bisection algorithm for *any* function with *any* number of arguments, works LtoR and RtoL
- checksums: various SHA256 tools for checking and creating checksum files
- delayed_keyboardinterrupt: Just a nifty tool to catch CTRL+C signals
- file_utils:
- json_sanitize: make sure json does not contain unsupported chars, yes I look at you Windows eventlog
- logger_utils: basic no brain console + file log creation
- mailer: send emails regardless of ssl/tls protocols, in batch or as single mail, with attachments
- network: various tools like ping, internet check, MTU probing and public IP discovery
- platform: nothing special here, just check what arch we are running on
- process: simple kill-them-all function to terminate subprocesses
- pw_gen: basic password generator
- service_control: control Windows / Linux service start / stop / status
- string_handling: Remove accents / special chars from strings

## Setup

```
pip install ofunctions.<subpackage>

```