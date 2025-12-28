.. _network.zyxel.zyxel_port_module:

*************************
network.zyxel.zyxel_port
*************************

**Manage port settings on Zyxel switches**

Synopsis
--------

- This module provides management of port settings on Zyxel switches.
- Configure port state, speed, duplex, flow control, and descriptions.

Parameters
----------

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Parameter
     - Type
     - Description
   * - name
     - string (required)
     - Port number or name to configure
   * - state
     - string
     - Administrative state of the port. Choices: enabled, disabled
   * - speed
     - string
     - Port speed setting. Choices: auto, 10, 100, 1000
   * - duplex
     - string
     - Duplex mode. Choices: auto, half, full
   * - flow_control
     - boolean
     - Enable or disable flow control
   * - description
     - string
     - Port description

Examples
--------

.. code-block:: yaml

   - name: Enable port 1
     network.zyxel.zyxel_port:
       name: "1"
       state: enabled

   - name: Configure port speed and duplex
     network.zyxel.zyxel_port:
       name: "1"
       speed: "1000"
       duplex: full

   - name: Enable flow control
     network.zyxel.zyxel_port:
       name: "1"
       flow_control: true

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

