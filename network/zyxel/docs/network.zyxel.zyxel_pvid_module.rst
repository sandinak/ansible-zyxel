.. _network.zyxel.zyxel_pvid_module:

*************************
network.zyxel.zyxel_pvid
*************************

**Manage port VLAN ID (PVID) settings on Zyxel switches**

Synopsis
--------

- This module manages the Port VLAN ID (PVID) setting on Zyxel switch ports.
- PVID determines the default VLAN for untagged traffic on a port.

Parameters
----------

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Parameter
     - Type
     - Description
   * - port
     - string (required)
     - Port number or name to configure
   * - pvid
     - integer (required)
     - VLAN ID to set as the PVID for this port (1-4094)

Examples
--------

.. code-block:: yaml

   - name: Set PVID for port 1 to VLAN 100
     network.zyxel.zyxel_pvid:
       port: "1"
       pvid: 100

   - name: Configure multiple ports with different PVIDs
     network.zyxel.zyxel_pvid:
       port: "{{ item.port }}"
       pvid: "{{ item.pvid }}"
     loop:
       - { port: "1", pvid: 100 }
       - { port: "2", pvid: 200 }
       - { port: "3", pvid: 100 }

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

