# Current master

## Features

### srtring handling
- Added filename_sanitize() function so a string becomes a windows/linux compatible filename

### file_utils
- file_utils.remove_files_on_timestamp_delta() and check_file_timestamp_delta() now accept optional alternative timestamp

### misc
- Added dict_update() function in order to update nested dictionaries with other nested dictionaries

### network
- probe_mtu and ping functions now allow to specify source
- added get_public_hostname() function

## Fixes

### file_utils
- Fixed remove_files_on_timestamp_delta() did not properly walk directories

## Generic
- Improved Python 2.7 unit tests for logger_utils and string_handling

# v2.3.0

See git history