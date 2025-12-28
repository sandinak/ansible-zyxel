# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Ansible module for gathering VLAN information from Zyxel switches via HTTP API."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: zyxel_vlans_info
short_description: Gather VLAN information from Zyxel switches
description:
  - Retrieves current VLAN configuration via web interface.
  - Supports GS1900, GS1915, and GS1920 series switches.
version_added: "1.0.0"
author:
  - Ansible Network Team
options:
  vlan_ids:
    description:
      - List of specific VLAN IDs to gather info for.
      - If not specified, returns info for all VLANs.
    type: list
    elements: str
    required: false
extends_documentation_fragment:
  - network.zyxel.zyxel
'''

EXAMPLES = r'''
- name: Get all VLAN information
  network.zyxel.zyxel_vlans_info:
  register: vlans_info

- name: Get specific VLANs information
  network.zyxel.zyxel_vlans_info:
    vlan_ids:
      - "10"
      - "20"
      - "30"
  register: vlans_info

- name: Display VLAN info
  debug:
    var: vlans_info.vlans
'''

RETURN = r'''
vlans:
  description: Dictionary of VLAN configurations keyed by VLAN ID
  returned: always
  type: dict
  sample:
    "1":
      name: "default"
      tagged_ports: []
      untagged_ports: ["1", "2", "3"]
    "10":
      name: "Management"
      tagged_ports: ["24"]
      untagged_ports: ["1", "2"]
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.network.zyxel.plugins.module_utils.zyxel import (
    get_connection,
)


def main():
    """Main module execution."""
    argument_spec = dict(
        vlan_ids=dict(type='list', elements='str', required=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    result = {'vlans': {}}
    requested_vlans = module.params.get('vlan_ids')

    connection = get_connection(module)
    all_vlans = connection.get_vlans_info()

    if requested_vlans:
        for vlan_id in requested_vlans:
            if vlan_id in all_vlans:
                result['vlans'][vlan_id] = all_vlans[vlan_id]
    else:
        result['vlans'] = all_vlans

    module.exit_json(**result)


if __name__ == '__main__':
    main()

