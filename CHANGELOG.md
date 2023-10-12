# Current master

### network

- Added IPv4 / IPv6 preference selector function (set_ip_version()
  - Make Nuitka compiler and pylint happy about the way we call into urllib

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