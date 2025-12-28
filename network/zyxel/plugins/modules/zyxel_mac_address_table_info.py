# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Ansible module for gathering MAC address table from Zyxel switches via HTTP API."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: zyxel_mac_address_table_info
short_description: Gather MAC address table from Zyxel switches
description:
  - Retrieves the MAC address table from the switch via HTTP API.
  - Note: HTTP API MAC address table retrieval is not yet fully implemented.
version_added: "1.0.0"
author:
  - Ansible Network Team
options:
  vlan_id:
    description:
      - Filter MAC addresses by VLAN ID.
    type: int
  port:
    description:
      - Filter MAC addresses by port.
    type: str
  mac_address:
    description:
      - Look up a specific MAC address.
    type: str
  address_type:
    description:
      - Filter by address type.
    type: str
    choices: ['dynamic', 'static', 'all']
    default: 'all'
notes:
  - HTTP API MAC address table retrieval is not yet fully implemented.
  - Tested against Zyxel GS1920 series switches.
extends_documentation_fragment:
  - network.zyxel.zyxel
'''

EXAMPLES = r'''
- name: Get all MAC addresses
  network.zyxel.zyxel_mac_address_table_info:
  register: mac_table
'''

RETURN = r'''
mac_table:
  description: List of MAC address entries
  returned: always
  type: list
  elements: dict
total_count:
  description: Total number of MAC addresses returned
  returned: always
  type: int
'''

from ansible.module_utils.basic import AnsibleModule


def main():
    """Main module execution."""
    argument_spec = dict(
        vlan_id=dict(type='int'),
        port=dict(type='str'),
        mac_address=dict(type='str'),
        address_type=dict(type='str', choices=['dynamic', 'static', 'all'], default='all'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    # HTTP API MAC address table retrieval not yet implemented
    module.fail_json(
        msg="MAC address table retrieval via HTTP API is not yet implemented for GS1920 series. "
            "Please view MAC address table through the web interface."
    )


if __name__ == '__main__':
    main()

