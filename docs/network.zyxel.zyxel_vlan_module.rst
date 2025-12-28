.. _network.zyxel.zyxel_vlan_module:

*************************
network.zyxel.zyxel_vlan
*************************

**Manage VLANs on Zyxel switches**

Synopsis
--------

- This module provides management of VLANs on Zyxel switches.
- Create, modify, and delete VLANs with associated settings.

Parameters
----------

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Parameter
     - Type
     - Description
   * - vlan_id
     - integer (required)
     - VLAN ID to manage (1-4094)
   * - name
     - string
     - Name of the VLAN
   * - state
     - string
     - State of the VLAN. Choices: present, absent. Default: present
   * - tagged_ports
     - list
     - List of ports that should be tagged members of this VLAN
   * - untagged_ports
     - list
     - List of ports that should be untagged members of this VLAN

Examples
--------

.. code-block:: yaml

   - name: Create VLAN 100
     network.zyxel.zyxel_vlan:
       vlan_id: 100
       name: "Management"
       state: present

   - name: Create VLAN with port assignments
     network.zyxel.zyxel_vlan:
       vlan_id: 200
       name: "Data"
       tagged_ports:
         - "24"
         - "25"
       untagged_ports:
         - "1"
         - "2"
         - "3"

   - name: Delete VLAN
     network.zyxel.zyxel_vlan:
       vlan_id: 100
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

