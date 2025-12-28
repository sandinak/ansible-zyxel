# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Module for managing Zyxel switch trunk/LAG settings via HTTP API."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: zyxel_trunk
short_description: Manage trunk (link aggregation) groups on Zyxel switches
description:
  - This module provides management of trunk groups (link aggregation) on Zyxel switches.
  - Configure port channel/trunk groups with member ports via HTTP API.
  - Supports GS1900, GS1915, and GS1920 series switches.
version_added: "1.0.0"
author:
  - Ansible Network Team
options:
  group:
    description:
      - Trunk group identifier (e.g., "T1", "T2", etc. for GS1920).
    type: str
    required: true
  enabled:
    description:
      - Enable or disable the trunk group.
    type: bool
    default: true
  members:
    description:
      - List of ports to include in the trunk group.
    type: list
    elements: str
  criteria:
    description:
      - Load balancing criteria.
    type: str
    choices: ['src-mac', 'dst-mac', 'src-dst-mac', 'src-ip', 'dst-ip', 'src-dst-ip']
notes:
  - Uses HTTP API only - no SSH/CLI.
  - Tested against Zyxel GS1920 series switches.
extends_documentation_fragment:
  - network.zyxel.zyxel
'''

EXAMPLES = r'''
- name: Create trunk group with ports 1-4
  network.zyxel.zyxel_trunk:
    group: "T1"
    enabled: true
    members:
      - "1"
      - "2"
      - "3"
      - "4"

- name: Create trunk with load balancing criteria
  network.zyxel.zyxel_trunk:
    group: "T2"
    enabled: true
    members:
      - "5"
      - "6"
    criteria: src-dst-mac

- name: Disable trunk group
  network.zyxel.zyxel_trunk:
    group: "T1"
    enabled: false
'''

RETURN = r'''
changed:
  description: Whether the configuration was changed.
  returned: always
  type: bool
  sample: true
group:
  description: The trunk group that was configured.
  returned: always
  type: str
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.network.zyxel.plugins.module_utils.zyxel import (
    get_connection,
)


def main():
    """Main entry point for module execution."""
    argument_spec = dict(
        group=dict(type='str', required=True),
        enabled=dict(type='bool', default=True),
        members=dict(type='list', elements='str'),
        criteria=dict(type='str', choices=['src-mac', 'dst-mac', 'src-dst-mac',
                                            'src-ip', 'dst-ip', 'src-dst-ip']),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    result = {'changed': False, 'group': module.params['group']}

    config = {
        'enabled': module.params['enabled'],
        'members': module.params.get('members') or [],
    }
    if module.params.get('criteria'):
        config['criteria'] = module.params['criteria']

    if not module.check_mode:
        connection = get_connection(module)
        success, message = connection.configure_lag(module.params['group'], config)
        if success:
            result['changed'] = True
    else:
        result['changed'] = True

    module.exit_json(**result)


if __name__ == '__main__':
    main()
