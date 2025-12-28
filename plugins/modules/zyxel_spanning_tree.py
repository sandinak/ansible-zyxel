# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Ansible module for spanning tree configuration on Zyxel switches via HTTP API."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: zyxel_spanning_tree
short_description: Configure spanning tree on Zyxel switches
description:
  - Configure Spanning Tree Protocol (STP/RSTP/MSTP) settings via HTTP API.
  - Note: HTTP API spanning tree configuration is not yet fully implemented.
version_added: "1.0.0"
author:
  - Ansible Network Team
options:
  enabled:
    description:
      - Enable or disable spanning tree globally.
    type: bool
  mode:
    description:
      - Spanning tree mode.
    type: str
    choices: ['stp', 'rstp', 'mstp']
notes:
  - HTTP API spanning tree configuration is not yet fully implemented.
  - Tested against Zyxel GS1920 series switches.
extends_documentation_fragment:
  - network.zyxel.zyxel
'''

EXAMPLES = r'''
- name: Enable RSTP globally
  network.zyxel.zyxel_spanning_tree:
    enabled: true
    mode: rstp
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
        enabled=dict(type='bool'),
        mode=dict(type='str', choices=['stp', 'rstp', 'mstp']),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    # HTTP API spanning tree not yet implemented
    module.fail_json(
        msg="Spanning tree configuration via HTTP API is not yet implemented for GS1920 series. "
            "Please configure spanning tree through the web interface."
    )


if __name__ == '__main__':
    main()

