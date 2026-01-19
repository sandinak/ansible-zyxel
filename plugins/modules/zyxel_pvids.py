# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Module for bulk managing Zyxel switch port PVID settings via HTTP API."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: zyxel_pvids
short_description: Bulk configure port VLAN ID (PVID) settings on Zyxel switches
description:
  - This module manages the Port VLAN ID (PVID) and related VLAN port settings
    for multiple ports in a single API call.
  - Much more efficient than calling zyxel_pvid in a loop.
  - Supports GS1900, GS1915, and GS1920 series switches.
version_added: "1.0.0"
author:
  - Ansible Network Team
options:
  port_settings:
    description:
      - Dictionary of port VLAN settings keyed by port number (as string).
      - Each port can have pvid, vlan_trunking, ingress_filtering, acceptable_frame_type.
    type: dict
    required: true
  num_ports:
    description:
      - Total number of ports on the switch.
    type: int
    default: 28
notes:
  - Uses HTTP API only - no SSH/CLI.
  - Configures all specified ports in a single HTTP request for efficiency.
extends_documentation_fragment:
  - network.zyxel.zyxel
'''

EXAMPLES = r'''
- name: Configure all port PVIDs in one call
  network.zyxel.zyxel_pvids:
    port_settings:
      "1":
        pvid: 1
        vlan_trunking: true
      "2":
        pvid: 100
        vlan_trunking: true
      "3":
        pvid: 200
        vlan_trunking: false

- name: Apply golden config port settings
  network.zyxel.zyxel_pvids:
    port_settings: "{{ core_switch_template.port_vlan_settings }}"
    num_ports: 24
'''

RETURN = r'''
changed:
  description: Whether the configuration was changed.
  returned: always
  type: bool
  sample: true
ports_configured:
  description: Number of ports configured.
  returned: always
  type: int
  sample: 24
message:
  description: Status message.
  returned: always
  type: str
  sample: "Configured 24 ports"
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.network.zyxel.plugins.module_utils.zyxel import (
    get_connection,
)


def main():
    """Main entry point for module execution."""
    argument_spec = dict(
        port_settings=dict(type='dict', required=True),
        num_ports=dict(type='int', default=28),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    result = {
        'changed': False,
        'ports_configured': 0,
        'message': ''
    }

    port_settings = module.params['port_settings']
    num_ports = module.params['num_ports']

    if not port_settings:
        result['message'] = 'No port settings provided'
        module.exit_json(**result)

    # Validate PVID ranges
    for port_str, settings in port_settings.items():
        pvid = settings.get('pvid')
        if pvid is not None and (pvid < 1 or pvid > 4094):
            module.fail_json(msg='PVID for port %s must be between 1 and 4094' % port_str)

    if not module.check_mode:
        connection = get_connection(module)
        success, message = connection.set_all_port_pvids(port_settings, num_ports)
        if success:
            result['changed'] = True
            result['ports_configured'] = len(port_settings)
            result['message'] = message
        else:
            module.fail_json(msg=message)
    else:
        result['changed'] = True
        result['ports_configured'] = len(port_settings)
        result['message'] = 'Would configure %d ports (check mode)' % len(port_settings)

    module.exit_json(**result)


if __name__ == '__main__':
    main()

