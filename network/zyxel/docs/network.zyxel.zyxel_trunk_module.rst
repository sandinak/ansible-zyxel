.. _network.zyxel.zyxel_trunk_module:

**************************
network.zyxel.zyxel_trunk
**************************

**Manage trunk (link aggregation) groups on Zyxel switches**

Synopsis
--------

- This module provides management of trunk groups (link aggregation) on Zyxel switches.
- Configure port channel/trunk groups with member ports and LACP settings.

Parameters
----------

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Parameter
     - Type
     - Description
   * - group
     - integer (required)
     - Trunk group number or identifier
   * - state
     - string
     - State of the trunk group. Choices: present, absent. Default: present
   * - members
     - list
     - List of ports to include in the trunk group
   * - mode
     - string
     - Trunk mode configuration. Choices: static, lacp. Default: static
   * - lacp_mode
     - string
     - LACP mode when mode is set to lacp. Choices: active, passive. Default: active

Examples
--------

.. code-block:: yaml

   - name: Create static trunk group with ports 1-4
     network.zyxel.zyxel_trunk:
       group: 1
       members:
         - "1"
         - "2"
         - "3"
         - "4"
       mode: static

   - name: Create LACP trunk group
     network.zyxel.zyxel_trunk:
       group: 2
       members:
         - "5"
         - "6"
       mode: lacp
       lacp_mode: active

   - name: Remove trunk group
     network.zyxel.zyxel_trunk:
       group: 1
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

