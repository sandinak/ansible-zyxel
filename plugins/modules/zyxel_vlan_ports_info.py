# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Ansible module for gathering VLAN port settings (PVID) from Zyxel switches."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: zyxel_vlan_ports_info
short_description: Gather VLAN port settings including PVID from Zyxel switches
description:
  - Retrieves VLAN port configuration including PVID, ingress filtering, VLAN trunking.
  - Supports GS1915 and GS1920 series switches.
version_added: "1.0.0"
author:
  - Ansible Network Team
options: {}
extends_documentation_fragment:
  - network.zyxel.zyxel
'''

EXAMPLES = r'''
- name: Get VLAN port settings
  network.zyxel.zyxel_vlan_ports_info:
  register: vlan_ports

- name: Display PVID for each port
  debug:
    msg: "Port {{ item.key }} has PVID {{ item.value.pvid }}"
  loop: "{{ vlan_ports.ports | dict2items }}"
'''

RETURN = r'''
ports:
  description: Dictionary of port VLAN settings keyed by port number
  returned: always
  type: dict
  sample:
    "1":
      pvid: 100
      ingress_filtering: false
      vlan_trunking: true
      acceptable_frame_type: "all"
    "2":
      pvid: 200
      ingress_filtering: true
      vlan_trunking: false
      acceptable_frame_type: "tagged_only"
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.network.zyxel.plugins.module_utils.zyxel import (
    get_connection,
)


def main():
    """Main module execution."""
    argument_spec = dict()

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    result = {'ports': {}}

    connection = get_connection(module)
    result['ports'] = connection.get_vlan_port_settings()

    module.exit_json(**result)


if __name__ == '__main__':
    main()

