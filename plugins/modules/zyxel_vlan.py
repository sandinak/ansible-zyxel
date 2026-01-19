# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Module for managing Zyxel switch VLANs."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: zyxel_vlan
short_description: Manage VLANs on Zyxel switches
description:
  - This module provides management of VLANs on Zyxel switches.
  - Create, modify, and delete VLANs with associated settings.
version_added: "1.0.0"
author:
  - Ansible Network Team
options:
  vlan_id:
    description:
      - VLAN ID to manage.
    type: int
    required: true
  name:
    description:
      - Name of the VLAN.
    type: str
  state:
    description:
      - State of the VLAN.
    type: str
    choices: ['present', 'absent']
    default: 'present'
  tagged_ports:
    description:
      - List of ports that should be tagged members of this VLAN (fixed, TX tagged).
      - These are typically trunk ports that carry multiple VLANs.
    type: list
    elements: str
  untagged_ports:
    description:
      - List of ports that should be untagged members of this VLAN (fixed, TX untagged).
      - These are typically access ports for this VLAN.
    type: list
    elements: str
  forbidden_ports:
    description:
      - List of ports that should be excluded from this VLAN.
      - Traffic for this VLAN will not be forwarded on these ports.
    type: list
    elements: str
notes:
  - Tested against Zyxel GS2220 series switches.
extends_documentation_fragment:
  - network.zyxel.zyxel
'''

EXAMPLES = r'''
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
'''

RETURN = r'''
commands:
  description: The list of configuration commands sent to the device.
  returned: always
  type: list
  sample: ['vlan 100', 'name Management', 'tagged 24,25', 'untagged 1,2,3']
changed:
  description: Whether the configuration was changed.
  returned: always
  type: bool
  sample: true
'''

import re
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.network.zyxel.plugins.module_utils.zyxel import (
    get_connection,
)


def get_vlan_config(module, vlan_id):
    """Get current VLAN configuration from the switch."""
    connection = get_connection(module)
    try:
        vlans = connection.get_vlans_info()
        vlan_str = str(vlan_id)
        if vlan_str in vlans:
            vlan_info = vlans[vlan_str]
            return {
                'exists': True,
                'name': vlan_info.get('name', ''),
                'tagged_ports': vlan_info.get('tagged_ports', []),
                'untagged_ports': vlan_info.get('untagged_ports', []),
            }
    except Exception:
        pass
    return {
        'exists': False,
        'name': '',
        'tagged_ports': [],
        'untagged_ports': [],
    }


def needs_update(current, params):
    """Check if VLAN configuration needs to be updated."""
    name = params.get('name', '')
    tagged = params.get('tagged_ports') or []
    untagged = params.get('untagged_ports') or []

    if not current.get('exists'):
        return True
    if name and name != current.get('name', ''):
        return True
    if sorted(str(p) for p in tagged) != sorted(current.get('tagged_ports', [])):
        return True
    if sorted(str(p) for p in untagged) != sorted(current.get('untagged_ports', [])):
        return True
    return False


def main():
    """Main entry point for module execution."""
    argument_spec = dict(
        vlan_id=dict(type='int', required=True),
        name=dict(type='str'),
        state=dict(type='str', choices=['present', 'absent'], default='present'),
        tagged_ports=dict(type='list', elements='str'),
        untagged_ports=dict(type='list', elements='str'),
        forbidden_ports=dict(type='list', elements='str'),
        num_ports=dict(type='int', default=28),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    result = {'changed': False, 'commands': [], 'msg': ''}

    vlan_id = module.params['vlan_id']
    state = module.params['state']
    name = module.params.get('name')
    tagged_ports = module.params.get('tagged_ports') or []
    untagged_ports = module.params.get('untagged_ports') or []
    forbidden_ports = module.params.get('forbidden_ports') or []
    num_ports = module.params.get('num_ports', 28)

    # Get connection to device
    connection = get_connection(module)

    # Get current configuration
    current = get_vlan_config(module, vlan_id)

    if state == 'absent':
        if current.get('exists'):
            result['changed'] = True
            result['commands'] = ['no vlan %s' % vlan_id]
            if not module.check_mode:
                success, msg = connection.delete_vlan(vlan_id)
                if not success:
                    module.fail_json(msg=msg)
                result['msg'] = msg
        else:
            result['msg'] = 'VLAN %s does not exist' % vlan_id
    else:  # state == 'present'
        # Check if ports are specified - this is critical for safe VLAN operations
        ports_specified = bool(tagged_ports or untagged_ports or forbidden_ports)
        vlan_exists = current.get('exists', False)

        # SAFETY: If VLAN exists and no ports specified, skip create_vlan entirely
        # The GS1920 web form clears port membership when submitted without port settings,
        # which breaks management connectivity if applied to VLAN 1 (management VLAN)
        if vlan_exists and not ports_specified:
            result['changed'] = False
            result['msg'] = 'VLAN %s exists (skipping update - no port changes specified)' % vlan_id
        elif needs_update(current, module.params):
            result['changed'] = True
            result['commands'] = ['vlan %s' % vlan_id]
            if name:
                result['commands'].append('name %s' % name)
            if tagged_ports:
                result['commands'].append('tagged %s' % ','.join(str(p) for p in tagged_ports))
            if untagged_ports:
                result['commands'].append('untagged %s' % ','.join(str(p) for p in untagged_ports))
            if forbidden_ports:
                result['commands'].append('forbidden %s' % ','.join(str(p) for p in forbidden_ports))

            if not module.check_mode:
                # Pass config as a dict to avoid RPC issues with 'name' parameter
                # Ensure lists are actual lists (not tuples) for JSON serialization
                vlan_config = {
                    'vlan_id': int(vlan_id),
                    'vlan_name': str(name) if name else '',
                    'tagged_ports': list(tagged_ports) if tagged_ports else [],
                    'untagged_ports': list(untagged_ports) if untagged_ports else [],
                    'forbidden_ports': list(forbidden_ports) if forbidden_ports else [],
                    'num_ports': int(num_ports),
                }
                response = connection.create_vlan(vlan_config)
                if isinstance(response, dict):
                    success = response.get('success', False)
                    msg = response.get('msg', 'Unknown result')
                else:
                    success, msg = response[0], response[1]
                if not success:
                    module.fail_json(msg=msg)
                result['msg'] = msg
        else:
            result['msg'] = 'VLAN %s already configured' % vlan_id

    module.exit_json(**result)


if __name__ == '__main__':
    main()
