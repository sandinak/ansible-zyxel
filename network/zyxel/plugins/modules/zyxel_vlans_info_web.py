#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: zyxel_vlans_info_web
short_description: Gather VLAN information from Zyxel GS1915/GS1920 switches via web API
description:
  - This module gathers VLAN information from Zyxel GS1915/GS1920 series switches.
  - Uses the web interface HTTP API for fast configuration retrieval.
  - Read-only module for information gathering.
  - Much faster than CLI-based information gathering.
version_added: "1.2.0"
author:
  - Ansible Network Team
options:
  vlan_id:
    description:
      - Specific VLAN ID to get information for
      - If not specified, returns information for all VLANs
    required: false
    type: int
notes:
  - This module requires httpapi connection type
  - Configure ansible_connection=ansible.netcommon.httpapi
  - Configure ansible_network_os=network.zyxel.zyxel
  - The GS1915/GS1920 series does not support configuration changes via API
  - Use the web interface for configuration changes
'''

EXAMPLES = '''
# Get information for all VLANs
- name: Get all VLANs
  network.zyxel.zyxel_vlans_info_web:
  register: all_vlans

# Get information for specific VLAN
- name: Get VLAN 100 info
  network.zyxel.zyxel_vlans_info_web:
    vlan_id: 100
  register: vlan_100

# Display VLAN information
- name: Show VLAN info
  debug:
    msg: "VLAN {{ item.key }}: {{ item.value.name }}"
  loop: "{{ all_vlans.vlans | dict2items }}"
'''

RETURN = '''
vlans:
  description: Dictionary of VLAN information
  returned: always
  type: dict
  sample:
    "100":
      id: "100"
      name: "GUEST_NETWORK"
      config: "vlan 100\\n  name \\"GUEST_NETWORK\\"\\n  normal \\"\\"\\n  fixed \\"\\"\\n  forbidden 1-24\\n  untagged 1-24\\nexit"
    "200":
      id: "200"
      name: "SERVERS"
      config: "vlan 200\\n  name \\"SERVERS\\"\\n  normal 1-4\\n  fixed \\"\\"\\n  forbidden 5-24\\n  untagged 5-24\\nexit"
device_info:
  description: Device information
  returned: always
  type: dict
  sample:
    network_os: "zyxel"
    network_os_platform: "gs1915-24ep"
    network_os_version: "V4.70(ACDS.2)"
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import Connection


def main():
    """Main module execution."""
    argument_spec = dict(
        vlan_id=dict(type='int', required=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    vlan_id = module.params.get('vlan_id')

    try:
        connection = Connection(module._socket_path)

        # Get device info
        device_info = connection.get_device_info()

        # Get VLAN information
        if vlan_id:
            vlans = connection.get_vlan_info(vlan_id=vlan_id)
        else:
            vlans = connection.get_vlan_info()

        result = {
            'changed': False,
            'vlans': vlans,
            'device_info': device_info,
            'vlan_count': len(vlans)
        }

        module.exit_json(**result)

    except Exception as e:
        module.fail_json(msg=f'Failed to gather VLAN information: {str(e)}')


if __name__ == '__main__':
    main()

