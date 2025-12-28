# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Cliconf plugin for Zyxel switches."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = """
---
name: zyxel
short_description: Use zyxel cliconf to run commands on Zyxel switches
description:
  - This zyxel plugin provides low level abstraction APIs for sending and receiving CLI
    commands from Zyxel network devices.
version_added: "1.0.0"
author:
  - Ansible Network Team
"""

import re
import json

from ansible.errors import AnsibleConnectionFailure
from ansible.module_utils.common.text.converters import to_text
from ansible.plugins.cliconf import CliconfBase, enable_mode


class Cliconf(CliconfBase):
    """Cliconf plugin for Zyxel devices."""

    def get_device_info(self):
        """Get device information."""
        device_info = {}
        device_info['network_os'] = 'zyxel'
        
        # Try to get system information
        try:
            reply = self.get('show system-information')
            data = to_text(reply, errors='surrogate_or_strict').strip()
            
            # Parse system name
            match = re.search(r'System Name\s*:\s*(\S+)', data)
            if match:
                device_info['network_os_hostname'] = match.group(1)
            
            # Parse firmware version
            match = re.search(r'Firmware Version\s*:\s*(\S+)', data)
            if match:
                device_info['network_os_version'] = match.group(1)
            
            # Parse model
            match = re.search(r'Model\s*:\s*(\S+)', data)
            if match:
                device_info['network_os_model'] = match.group(1)
                
        except AnsibleConnectionFailure:
            # Fall back to simpler command
            pass
        
        return device_info

    def get_device_operations(self):
        """Return supported operations."""
        return {
            'supports_diff_replace': False,
            'supports_commit': False,
            'supports_rollback': False,
            'supports_defaults': False,
            'supports_onbox_diff': False,
            'supports_commit_comment': False,
            'supports_multiline_delimiter': False,
            'supports_diff_match': False,
            'supports_diff_ignore_lines': False,
            'supports_generate_diff': False,
            'supports_replace': False,
        }

    def get_option_values(self):
        """Return option values."""
        return {
            'format': ['text'],
            'diff_match': [],
            'diff_replace': [],
            'output': ['text'],
        }

    def get_capabilities(self):
        """Return device capabilities."""
        result = super(Cliconf, self).get_capabilities()
        result['rpc'] += ['run_commands', 'get_config', 'edit_config']
        result['device_operations'] = self.get_device_operations()
        result['network_api'] = 'cliconf'
        return json.dumps(result)

    @enable_mode
    def get_config(self, source='running', flags=None, format=None):
        """Get running configuration."""
        if source != 'running':
            raise AnsibleConnectionFailure("Zyxel devices only support 'running' configuration")
        
        cmd = 'show running-config'
        if flags:
            cmd += ' ' + ' '.join(flags)
        
        return self.send_command(cmd)

    @enable_mode
    def edit_config(self, candidate=None, commit=True, replace=None, comment=None):
        """Edit device configuration."""
        responses = []
        
        if not candidate:
            return {'request': [], 'response': []}
        
        for cmd in candidate:
            if isinstance(cmd, dict):
                command = cmd.get('command', '')
                prompt = cmd.get('prompt')
                answer = cmd.get('answer')
                newline = cmd.get('newline', True)
            else:
                command = cmd
                prompt = None
                answer = None
                newline = True
            
            if command:
                responses.append(self.send_command(
                    command=command,
                    prompt=prompt,
                    answer=answer,
                    newline=newline
                ))
        
        return {'request': candidate, 'response': responses}

    def get(self, command, prompt=None, answer=None, sendonly=False, newline=True, check_all=False):
        """Send a command to the device."""
        return self.send_command(
            command=command,
            prompt=prompt,
            answer=answer,
            sendonly=sendonly,
            newline=newline,
            check_all=check_all
        )

    def run_commands(self, commands, check_rc=True):
        """Run a list of commands on the device."""
        responses = []
        for cmd in commands:
            try:
                if isinstance(cmd, dict):
                    response = self.send_command(**cmd)
                else:
                    response = self.send_command(command=cmd)
                responses.append(response)
            except AnsibleConnectionFailure as e:
                if check_rc:
                    raise
                responses.append(to_text(e))
        return responses

