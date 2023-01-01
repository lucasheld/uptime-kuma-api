## Changelog

### Release 0.7.1

#### Bugfix
- remove unsupported type hints on old python versions

### Release 0.7.0

#### Feature
- add support for uptime kuma 1.19.2

#### Bugfix
- skip condition check for None values

### Release 0.6.0

#### Feature
- add parameter `wait_timeout` to adjust connection timeout

### Release 0.5.2

#### Bugfix
- add type to notification provider options

### Release 0.5.1

#### Bugfix
- remove required notification provider args check

### Release 0.5.0

#### Feature
- support for uptime kuma 1.18.3

### Release 0.4.0

#### Feature
- support for uptime kuma 1.18.1 / 1.18.2

#### Bugfix
- update event list data after changes

### Release 0.3.0

#### Feature
- support autoLogin for enabled disableAuth

#### Bugfix
- set_settings password is only required if disableAuth is enabled
- increase event wait time to receive the slow statusPageList event

### Release 0.2.2

#### Bugfix
- remove `tags` from monitor input
- convert monitor notificationIDList only once

### Release 0.2.1

#### Bugfix
- generate pushToken on push monitor save
- convert monitor notificationIDList return value

### Release 0.2.0

#### Feature
- support for uptime kuma 1.18.0

#### Bugfix
- convert values on monitor edit

### Release 0.1.1

#### Bugfix
- implement 2FA login
- allow to add monitors to status pages
- do not block certain methods

### Release 0.1.0

- initial release
