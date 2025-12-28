# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Module for managing Zyxel switch port PVID settings via HTTP API."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: zyxel_pvid
short_description: Manage port VLAN ID (PVID) settings on Zyxel switches
description:
  - This module manages the Port VLAN ID (PVID) and related VLAN port settings via HTTP API.
  - PVID determines the default VLAN for untagged traffic on a port.
  - Also configures VLAN trunking, ingress filtering, and acceptable frame type.
  - Supports GS1900, GS1915, and GS1920 series switches.
version_added: "1.0.0"
author:
  - Ansible Network Team
options:
  port:
    description:
      - Port number to configure.
    type: str
    required: true
  pvid:
    description:
      - VLAN ID to set as the PVID for this port.
    type: int
    required: true
  vlan_trunking:
    description:
      - Enable or disable VLAN trunking on this port.
      - When enabled, the port will pass all VLANs.
    type: bool
  ingress_filtering:
    description:
      - Enable or disable ingress filtering on this port.
    type: bool
  acceptable_frame_type:
    description:
      - Type of frames the port will accept.
    type: str
    choices: ['all', 'tagged', 'untagged']
notes:
  - Uses HTTP API only - no SSH/CLI.
  - Tested against Zyxel GS1920 series switches.
extends_documentation_fragment:
  - network.zyxel.zyxel
'''

EXAMPLES = r'''
- name: Set PVID for port 1 to VLAN 100
  network.zyxel.zyxel_pvid:
    port: "1"
    pvid: 100

- name: Set PVID with VLAN trunking enabled
  network.zyxel.zyxel_pvid:
    port: "1"
    pvid: 100
    vlan_trunking: true

- name: Configure port with all VLAN settings
  network.zyxel.zyxel_pvid:
    port: "24"
    pvid: 1
    vlan_trunking: true
    ingress_filtering: false
    acceptable_frame_type: all

- name: Configure multiple ports with different PVIDs
  network.zyxel.zyxel_pvid:
    port: "{{ item.port }}"
    pvid: "{{ item.pvid }}"
    vlan_trunking: "{{ item.trunking | default(omit) }}"
  loop:
    - { port: "1", pvid: 100, trunking: true }
    - { port: "2", pvid: 200, trunking: true }
    - { port: "3", pvid: 100 }
'''

RETURN = r'''
changed:
  description: Whether the configuration was changed.
  returned: always
  type: bool
  sample: true
port:
  description: The port that was configured.
  returned: always
  type: str
pvid:
  description: The PVID that was set.
  returned: always
  type: int
vlan_trunking:
  description: VLAN trunking setting if specified.
  returned: when specified
  type: bool
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.network.zyxel.plugins.module_utils.zyxel import (
    get_connection,
)


def main():
    """Main entry point for module execution."""
    argument_spec = dict(
        port=dict(type='str', required=True),
        pvid=dict(type='int', required=True),
        vlan_trunking=dict(type='bool'),
        ingress_filtering=dict(type='bool'),
        acceptable_frame_type=dict(type='str', choices=['all', 'tagged', 'untagged']),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    result = {'changed': False, 'port': module.params['port'], 'pvid': module.params['pvid']}

    port = module.params['port']
    pvid = module.params['pvid']
    vlan_trunking = module.params.get('vlan_trunking')
    ingress_filtering = module.params.get('ingress_filtering')
    acceptable_frame_type = module.params.get('acceptable_frame_type')

    # Validate PVID range
    if pvid < 1 or pvid > 4094:
        module.fail_json(msg='PVID must be between 1 and 4094')

    if not module.check_mode:
        connection = get_connection(module)
        success, message = connection.set_port_pvid(
            port, pvid,
            vlan_trunking=vlan_trunking,
            ingress_filtering=ingress_filtering,
            acceptable_frame_type=acceptable_frame_type
        )
        if success:
            result['changed'] = True
            result['message'] = message
            if vlan_trunking is not None:
                result['vlan_trunking'] = vlan_trunking
        else:
            module.fail_json(msg=message)
    else:
        result['changed'] = True

    module.exit_json(**result)


if __name__ == '__main__':
    main()

