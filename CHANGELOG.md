# v2.8.0

### logger_utils 

- Monkeypatch `get_worst_logger_level()` into logger object returned by `logger_get_logger()` in order to easily retrieve worst called log level

### misc

- Created a function called `replace_in_iterable()` that recursively walks a dict structure and replaces data depending on key / value names. Replacement can be the result of a function call.
- Added `fn_name()` function which returns current or parent function name depending on the requested level
- Fixed `BytesConverter` class to allow interpreting `0`

### network

- BREAKING CHANGE: `test_http_internet()` has been renamed to `check_http_internet()` to avoid pytest complaints
- `get_public_ip()` can now properly enforce timeouts, which didn't work on host resolution because of OS
- `get_public_ip()` is now way faster since it tries to concurrently fetch IP addresses


### platform

- Remove `get_distro()`
- Added `get_os_identifier()`

### process

- Refactor `kill_childs()` to allow grace period before asking nicely to quit, then grace period before being a merciless process killer

### requestor

- Requestor now has `ignore_errors` getter/setter, which will transform all log levels above info into info

### threading

- @threaded decorator now takes optional `__no_thread` bool which allows to bypass threading will keeping the decorator syntax (the `__no_thread` argument is given to the original function and is intercepted by the decorator)
- New wait_for_thread_completion() function which accepts threads or lists of threads, and returns results or lists of results

# v2.7.0

## Features

### network

- Added IPv4 / IPv6 preference selector function set_ip_version()
  - Make Nuitka compiler and pylint happy about the way we call into urllib

### Misc

- New replace_in_iterable() function which can iter over a composite dict/list struct and replace values
  - Retains original struct type
  - Can also run a callable to replace values
- New DotDict() object which is basically a dict that can be accessed with dot notation, ie dict.my.value

### Platform

- Improve os_arch() function to work with various arm platforms

### Random

- Add new password_gen() function which allows to select alpha/numeric/special_chars & non ambiguous chars

## Others

- Removed Python 2.7 from the test matrix since Github doesn't support it anymore
- Linters are now using Python 3.11

# v2.6.0

## Features

### requestor
- Initial upload of REST API class

### platform
- os_arch() and python_arch() now also check for arm & arm64 platforms

# v2.5.2

## Features

### platform
- Added os_arch() function which returns current OS arch regardless of python arch

### process
- Make kill_childs() function verbose by default

# v2.5.1

## Fixes

### misc
- Fixed BytesConverter class conversion failures for null values

# v2.5.0

## Features

### misc
- Improved BytesConverter class in order to deal with human and IEC notations
- Added convert_time_to_seconds() function allowing converting HHH:MM:SS to seconds

## Others

- Remove Python 3.5 and 3.6 from linux test matrix since Github actions don't propose them anymore
- Update github actions to v3
# v2.4.0

## Features

### checksums
- Added sha256sum_data() function

### srtring handling
- Added filename_sanitize() function so a string becomes a windows/linux compatible filename

### file_utils
- file_utils.remove_files_on_timestamp_delta() and check_file_timestamp_delta() now accept optional alternative timestamp

### misc
- Added deep_dict_update() function in order to update nested dictionaries with other nested dictionaries
- Added BytesConverter class which handles conversion between bytes/bits and their binary prefixes

### network
- New IOCounters class that returns periodic network interface statistics
- probe_mtu and ping functions now allow to specify source
- added get_public_hostname() function

### platform
- Added get_distro() function which returns distro flavor and version (only works on RHEL so far, help welcome)

### string_handling
- Added sanitize_filename() function to clean filenames in order to work on most filesystems (win/linux/macos)

### threading
- Added a simple threaded decorator for Python 2.7

## Fixes

### file_utils
- Fixed remove_files_on_timestamp_delta() did not properly walk directories

## Generic
- Improved Python 2.7 unit tests for logger_utils and string_handling

# v2.3.0

See git history