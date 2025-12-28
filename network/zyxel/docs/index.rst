.. _network.zyxel_docsite:

**********************
Network.Zyxel Collection
**********************

The ``network.zyxel`` collection provides Ansible modules for managing Zyxel network switches.

.. toctree::
   :maxdepth: 1
   :caption: Modules

   network.zyxel.zyxel_port_module
   network.zyxel.zyxel_trunk_module
   network.zyxel.zyxel_vlan_module
   network.zyxel.zyxel_pvid_module
   network.zyxel.zyxel_syslog_module
   network.zyxel.zyxel_ntp_module
   network.zyxel.zyxel_user_module

Description
===========

This collection enables automation of Zyxel switch configuration including:

* Port management (speed, duplex, flow control, descriptions)
* VLAN management (create, update, delete VLANs)
* Trunk/LAG configuration (static and LACP)
* PVID (Port VLAN ID) configuration
* System management (syslog, NTP, users)

Requirements
============

* Ansible >= 2.14.0
* Python >= 3.9
* ansible.netcommon >= 2.0.0

Installation
============

Install from Ansible Galaxy::

    ansible-galaxy collection install network.zyxel

Or install from source::

    cd network/zyxel
    ansible-galaxy collection build
    ansible-galaxy collection install network-zyxel-1.0.0.tar.gz

Supported Devices
=================

* Zyxel GS2220 Series
* Zyxel GS1920 Series
* Zyxel XGS Series
* Other Zyxel managed switches with CLI access

Connection Configuration
========================

Configure your inventory to use the network_cli connection::

    all:
      hosts:
        zyxel_switch:
          ansible_host: 192.168.1.1
          ansible_user: admin
          ansible_password: password
          ansible_connection: ansible.netcommon.network_cli
          ansible_network_os: network.zyxel.zyxel

License
=======

GNU General Public License v3.0+

Authors
=======

* Ansible Network Team

