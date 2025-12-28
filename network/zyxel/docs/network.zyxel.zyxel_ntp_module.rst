.. _network.zyxel.zyxel_ntp_module:

************************
network.zyxel.zyxel_ntp
************************

**Manage NTP settings on Zyxel switches**

Synopsis
--------

- This module manages NTP server configuration on Zyxel switches.
- Configure NTP servers and timezone settings.

Parameters
----------

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Parameter
     - Type
     - Description
   * - state
     - string
     - State of the NTP configuration. Choices: present, absent. Default: present
   * - server
     - string (required)
     - IP address or hostname of the NTP server
   * - prefer
     - boolean
     - Mark this server as preferred. Default: false
   * - timezone
     - string
     - Timezone offset from UTC (e.g., '+0', '-5', '+5:30')

Examples
--------

.. code-block:: yaml

   - name: Configure NTP server
     network.zyxel.zyxel_ntp:
       server: "pool.ntp.org"
       prefer: true

   - name: Configure NTP with timezone
     network.zyxel.zyxel_ntp:
       server: "192.168.1.1"
       timezone: "-5"

   - name: Remove NTP server
     network.zyxel.zyxel_ntp:
       server: "pool.ntp.org"
       state: absent

Return Values
-------------

commands
    The list of configuration commands sent to the device.
    
    Returned: always
    
    Type: list

changed
    Whether the configuration was changed.
    
    Returned: always
    
    Type: bool

Authors
-------

- Ansible Network Team

