.. _network.zyxel.zyxel_user_module:

*************************
network.zyxel.zyxel_user
*************************

**Manage user accounts on Zyxel switches**

Synopsis
--------

- This module manages user accounts on Zyxel switches.
- Create, modify, and delete user accounts with associated privileges.

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
     - Username to manage
   * - state
     - string
     - State of the user account. Choices: present, absent. Default: present
   * - password
     - string
     - Password for the user account. Required when creating a new user.
   * - privilege
     - string
     - Privilege level. Choices: admin, user, guest. Default: user
   * - update_password
     - string
     - When to update the password. Choices: always, on_create. Default: always

Examples
--------

.. code-block:: yaml

   - name: Create admin user
     network.zyxel.zyxel_user:
       name: "netadmin"
       password: "SecurePass123!"
       privilege: admin

   - name: Create read-only user
     network.zyxel.zyxel_user:
       name: "monitor"
       password: "MonitorPass!"
       privilege: guest

   - name: Remove user
     network.zyxel.zyxel_user:
       name: "olduser"
       state: absent

Return Values
-------------

commands
    The list of configuration commands sent to the device (passwords masked).
    
    Returned: always
    
    Type: list

changed
    Whether the configuration was changed.
    
    Returned: always
    
    Type: bool

Authors
-------

- Ansible Network Team

