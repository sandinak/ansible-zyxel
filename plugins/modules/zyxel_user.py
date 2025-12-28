# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Module for managing Zyxel switch user accounts via HTTP API."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: zyxel_user
short_description: Manage user accounts on Zyxel switches
description:
  - This module manages user accounts on Zyxel switches via HTTP API.
  - Note: HTTP API user management is not yet fully implemented.
version_added: "1.0.0"
author:
  - Ansible Network Team
options:
  name:
    description:
      - Username to manage.
    type: str
    required: true
  state:
    description:
      - State of the user account.
    type: str
    choices: ['present', 'absent']
    default: 'present'
  password:
    description:
      - Password for the user account.
    type: str
    no_log: true
  privilege:
    description:
      - Privilege level for the user.
    type: str
    choices: ['admin', 'user', 'guest']
    default: 'user'
notes:
  - HTTP API user management is not yet fully implemented.
  - Tested against Zyxel GS1920 series switches.
extends_documentation_fragment:
  - network.zyxel.zyxel
'''

EXAMPLES = r'''
- name: Create admin user
  network.zyxel.zyxel_user:
    name: "netadmin"
    password: "SecurePass123!"
    privilege: admin
'''

RETURN = r'''
changed:
  description: Whether the configuration was changed.
  returned: always
  type: bool
  sample: false
msg:
  description: Status message.
  returned: always
  type: str
'''

from ansible.module_utils.basic import AnsibleModule


def main():
    """Main entry point for module execution."""
    argument_spec = dict(
        name=dict(type='str', required=True),
        state=dict(type='str', choices=['present', 'absent'], default='present'),
        password=dict(type='str', no_log=True),
        privilege=dict(type='str', choices=['admin', 'user', 'guest'], default='user'),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    # HTTP API user management not yet implemented
    module.fail_json(
        msg="User management via HTTP API is not yet implemented for GS1920 series. "
            "Please configure users through the web interface."
    )


if __name__ == '__main__':
    main()

