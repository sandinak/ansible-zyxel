# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Ansible module for LAG configuration on Zyxel switches via HTTP API."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: zyxel_lag
short_description: Configure Link Aggregation Groups on Zyxel switches
description:
  - Configure LAG (Link Aggregation Group) / trunk settings via HTTP API.
  - Supports enabling/disabling LAG groups and assigning member ports.
  - Supports GS1900, GS1915, and GS1920 series switches.
version_added: "1.0.0"
author:
  - Ansible Network Team
options:
  groups:
    description:
      - Dictionary of LAG group configurations keyed by group ID (T1-T8).
    type: dict
    required: true
notes:
  - Uses HTTP API only - no SSH/CLI.
  - Tested against Zyxel GS1920 series switches.
  - Group IDs on GS1920 are T1 through T8.
extends_documentation_fragment:
  - network.zyxel.zyxel
'''

EXAMPLES = r'''
- name: Configure LAG groups
  network.zyxel.zyxel_lag:
    groups:
      "T1":
        enabled: true
        members: ["1", "2"]
        criteria: "src-dst-mac"
      "T2":
        enabled: true
        members: ["3", "4"]

- name: Disable LAG group
  network.zyxel.zyxel_lag:
    groups:
      "T1":
        enabled: false

- name: Configure LAG with specific port assignments
  network.zyxel.zyxel_lag:
    groups:
      "T1":
        enabled: true
        members: ["21", "22", "23", "24"]
'''

RETURN = r'''
changed:
  description: Whether any changes were made
  returned: always
  type: bool
groups_configured:
  description: List of LAG group IDs that were configured
  returned: always
  type: list
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.network.zyxel.plugins.module_utils.zyxel import (
    get_connection,
)


def main():
    """Main module execution."""
    argument_spec = dict(
        groups=dict(type='dict', required=True),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    result = {'changed': False, 'groups_configured': []}

    if not module.check_mode:
        connection = get_connection(module)

        for group_id, config in module.params['groups'].items():
            lag_config = {
                'enabled': config.get('enabled', True),
                'members': config.get('members', []),
            }
            if config.get('criteria'):
                lag_config['criteria'] = config['criteria']

            success, message = connection.configure_lag(group_id, lag_config)
            if success:
                result['changed'] = True
                result['groups_configured'].append(group_id)
    else:
        result['changed'] = True
        result['groups_configured'] = list(module.params['groups'].keys())

    module.exit_json(**result)


if __name__ == '__main__':
    main()

