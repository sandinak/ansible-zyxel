# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Ansible module for port mirroring configuration on Zyxel switches via HTTP API."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: zyxel_mirror
short_description: Configure port mirroring on Zyxel switches
description:
  - Configure port mirroring (SPAN) sessions for traffic analysis via HTTP API.
  - Note: HTTP API port mirroring is not yet fully implemented.
version_added: "1.0.0"
author:
  - Ansible Network Team
options:
  sessions:
    description:
      - List of mirror session configurations.
    type: list
    elements: dict
    required: true
notes:
  - HTTP API port mirroring is not yet fully implemented.
  - Tested against Zyxel GS1920 series switches.
extends_documentation_fragment:
  - network.zyxel.zyxel
'''

EXAMPLES = r'''
- name: Configure port mirroring session
  network.zyxel.zyxel_mirror:
    sessions:
      - session_id: 1
        destination_port: "24"
        source_ports:
          - port: "1"
            direction: both
'''

RETURN = r'''
changed:
  description: Whether any changes were made
  returned: always
  type: bool
  sample: false
'''

from ansible.module_utils.basic import AnsibleModule


def main():
    """Main module execution."""
    argument_spec = dict(
        sessions=dict(type='list', elements='dict', required=True),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    # HTTP API port mirroring not yet implemented
    module.fail_json(
        msg="Port mirroring via HTTP API is not yet implemented for GS1920 series. "
            "Please configure port mirroring through the web interface."
    )


if __name__ == '__main__':
    main()

