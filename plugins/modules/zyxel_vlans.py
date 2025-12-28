# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Ansible module for bulk VLAN configuration on Zyxel switches via HTTP API."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: zyxel_vlans
short_description: Bulk configure VLANs on Zyxel switches
description:
  - Configure multiple VLANs at once using a dictionary of VLAN configurations via HTTP API.
  - Each VLAN can specify name, tagged ports, and untagged ports.
  - Supports GS1900, GS1915, and GS1920 series switches.
version_added: "1.0.0"
author:
  - Ansible Network Team
options:
  vlans:
    description:
      - Dictionary of VLAN configurations keyed by VLAN ID.
      - Each VLAN configuration can include name, tagged_ports, untagged_ports, state.
    type: dict
    required: true
notes:
  - Uses HTTP API only - no SSH/CLI.
  - Tested against Zyxel GS1920 series switches.
extends_documentation_fragment:
  - network.zyxel.zyxel
'''

EXAMPLES = r'''
- name: Configure multiple VLANs
  network.zyxel.zyxel_vlans:
    vlans:
      "10":
        name: "Management"
        tagged_ports: ["24"]
        untagged_ports: ["1", "2"]
      "20":
        name: "Servers"
        tagged_ports: ["24"]
        untagged_ports: ["3", "4", "5"]
      "30":
        name: "Users"
        tagged_ports: ["24"]
        untagged_ports: ["6", "7", "8", "9", "10"]

- name: Remove specific VLANs
  network.zyxel.zyxel_vlans:
    vlans:
      "99":
        state: absent
'''

RETURN = r'''
changed:
  description: Whether any changes were made
  returned: always
  type: bool
vlans_configured:
  description: List of VLAN IDs that were configured
  returned: always
  type: list
  sample: ["10", "20", "30"]
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.network.zyxel.plugins.module_utils.zyxel import (
    get_connection,
)


def main():
    """Main module execution."""
    argument_spec = dict(
        vlans=dict(type='dict', required=True),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    result = {'changed': False, 'vlans_configured': []}
    vlans = module.params['vlans']

    if not module.check_mode:
        connection = get_connection(module)

        for vlan_id, config in vlans.items():
            if config:
                state = config.get('state', 'present')
                if state == 'absent':
                    success, message = connection.delete_vlan(vlan_id)
                else:
                    success, message = connection.create_vlan(
                        vlan_id,
                        name=config.get('name'),
                        tagged_ports=config.get('tagged_ports'),
                        untagged_ports=config.get('untagged_ports')
                    )
                if success:
                    result['changed'] = True
                    result['vlans_configured'].append(vlan_id)
    else:
        result['changed'] = True
        result['vlans_configured'] = list(vlans.keys())

    module.exit_json(**result)


if __name__ == '__main__':
    main()

