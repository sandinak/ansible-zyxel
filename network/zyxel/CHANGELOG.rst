================================
Network.Zyxel Release Notes
================================

.. contents:: Topics

v1.2.0
======

Release Summary
---------------

Major architecture change: Migrated from CLI-based to HTTP API-based configuration.
Zyxel switches require web-based management and do not support SSH configuration.

Breaking Changes
----------------

- All modules now use HTTP API (httpapi) connection instead of CLI
- Requires ``ansible_connection: ansible.netcommon.httpapi``
- Requires ``ansible_network_os: network.zyxel.zyxel``

New Features
------------

Multi-Model Support
~~~~~~~~~~~~~~~~~~~

- Full support for GS1900 series (CGI-based API with token authentication)
- Full support for GS1915 series (form-based API with lowercase page names)
- Full support for GS1920 series (form-based API with mixed-case page names)

HTTP API Plugin
~~~~~~~~~~~~~~~

- New ``httpapi`` plugin with automatic model detection
- Secure password encoding for GS1900 series
- Session-based authentication for GS1915/GS1920 series

Tested Switches
~~~~~~~~~~~~~~~

- GS1920-24HP - PASS
- GS1915-24EP - PASS
- GS1900-8HP - PASS

v1.1.0
======

Release Summary
---------------

Major feature release adding bulk configuration, system management, and advanced networking modules.

New Modules
-----------

Bulk Configuration
~~~~~~~~~~~~~~~~~~

- ``network.zyxel.zyxel_ports`` - Bulk configure multiple ports using a dictionary
- ``network.zyxel.zyxel_vlans`` - Bulk configure multiple VLANs using a dictionary
- ``network.zyxel.zyxel_ports_info`` - Gather port information as a dictionary
- ``network.zyxel.zyxel_vlans_info`` - Gather VLAN information as a dictionary

System & Management
~~~~~~~~~~~~~~~~~~~

- ``network.zyxel.zyxel_system`` - Configure system settings (hostname, location, contact, timezone)
- ``network.zyxel.zyxel_management`` - Consolidated management services (SNMP, syslog, NTP, SSH, HTTPS, Telnet)

Security & AAA
~~~~~~~~~~~~~~

- ``network.zyxel.zyxel_aaa`` - Configure RADIUS and TACACS+ authentication
- ``network.zyxel.zyxel_security`` - Configure port security, 802.1X, DHCP snooping, ARP inspection

Advanced Networking
~~~~~~~~~~~~~~~~~~~

- ``network.zyxel.zyxel_mac_address_table_info`` - Gather MAC address table information
- ``network.zyxel.zyxel_spanning_tree`` - Configure STP/RSTP/MSTP settings
- ``network.zyxel.zyxel_mirror`` - Configure port mirroring (SPAN) sessions
- ``network.zyxel.zyxel_lag`` - Configure Link Aggregation Groups

v1.0.0
======

Release Summary
---------------

Initial release of the network.zyxel collection for managing Zyxel switches.

New Modules
-----------

- ``network.zyxel.zyxel_port`` - Manage port settings on Zyxel switches
- ``network.zyxel.zyxel_trunk`` - Manage trunk (link aggregation) groups
- ``network.zyxel.zyxel_vlan`` - Manage VLANs on Zyxel switches
- ``network.zyxel.zyxel_pvid`` - Manage port VLAN ID (PVID) settings
- ``network.zyxel.zyxel_syslog`` - Manage syslog settings
- ``network.zyxel.zyxel_ntp`` - Manage NTP settings
- ``network.zyxel.zyxel_user`` - Manage user accounts

New Plugins
-----------

Cliconf
~~~~~~~

- ``network.zyxel.zyxel`` - CLI configuration plugin for Zyxel switches

Terminal
~~~~~~~~

- ``network.zyxel.zyxel`` - Terminal plugin for Zyxel switches

Features
--------

Port Management
~~~~~~~~~~~~~~~

- Configure port state (enabled/disabled)
- Set port speed and duplex mode
- Enable/disable flow control
- Set port descriptions

VLAN Management
~~~~~~~~~~~~~~~

- Create, update, and delete VLANs
- Assign tagged and untagged ports to VLANs
- Configure port VLAN IDs (PVID)

Trunk/LAG Management
~~~~~~~~~~~~~~~~~~~~

- Create static trunk groups
- Configure LACP trunk groups with active/passive modes
- Manage trunk group membership

System Management
~~~~~~~~~~~~~~~~~

- Configure syslog servers with facility and severity settings
- Configure NTP servers with timezone support
- Manage user accounts with privilege levels

Known Issues
------------

- This is the initial release; please report any issues on the project repository.

Deprecations
------------

- None

Bugfixes
--------

- None (initial release)

