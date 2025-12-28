.. _network.zyxel.zyxel_syslog_module:

***************************
network.zyxel.zyxel_syslog
***************************

**Manage syslog settings on Zyxel switches**

Synopsis
--------

- This module manages syslog server configuration on Zyxel switches.
- Configure remote syslog servers, facility, and severity levels.

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
     - State of the syslog configuration. Choices: present, absent. Default: present
   * - server
     - string (required)
     - IP address or hostname of the syslog server
   * - port
     - integer
     - UDP port for syslog server. Default: 514
   * - facility
     - string
     - Syslog facility. Choices: local0-local7. Default: local7
   * - severity
     - string
     - Minimum severity level. Choices: emergency, alert, critical, error, warning, notice, info, debug. Default: info

Examples
--------

.. code-block:: yaml

   - name: Configure syslog server
     network.zyxel.zyxel_syslog:
       server: "192.168.1.100"
       port: 514
       facility: local7
       severity: info

   - name: Configure syslog with warning level
     network.zyxel.zyxel_syslog:
       server: "syslog.example.com"
       severity: warning

   - name: Remove syslog server
     network.zyxel.zyxel_syslog:
       server: "192.168.1.100"
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

