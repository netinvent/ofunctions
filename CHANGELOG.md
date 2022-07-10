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