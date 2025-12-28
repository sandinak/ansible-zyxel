# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Terminal plugin for Zyxel switches."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = """
---
name: zyxel
short_description: Zyxel switch terminal plugin
description:
  - This is the terminal plugin for Zyxel network devices.
version_added: "1.0.0"
author:
  - Ansible Network Team
"""

import re

from ansible.errors import AnsibleConnectionFailure
from ansible.plugins.terminal import TerminalBase


class TerminalModule(TerminalBase):
    """Terminal plugin for Zyxel devices."""

    # Regex patterns for terminal prompts
    # Updated to handle Zyxel prompts with ANSI escape sequences (\x1b7 = ESC 7)
    terminal_stdout_re = [
        re.compile(rb'[\r\n]?[\w\-]+[>#]\s*(?:\x1b7)?$'),
        re.compile(rb'[\r\n]?[\w\-]+\([\w\-]+\)[>#]\s*(?:\x1b7)?$'),
    ]

    # Regex patterns for error messages
    terminal_stderr_re = [
        re.compile(rb"% Invalid input detected", re.I),
        re.compile(rb"% Ambiguous command", re.I),
        re.compile(rb"% Incomplete command", re.I),
        re.compile(rb"% Unknown command", re.I),
        re.compile(rb"% Error", re.I),
        re.compile(rb"command not found", re.I),
        re.compile(rb"invalid parameter", re.I),
    ]

    # Regex patterns for initial prompts (login, password)
    terminal_initial_prompt = [
        re.compile(rb'[Uu]sername:', re.I),
        re.compile(rb'[Pp]assword:', re.I),
    ]

    # Answers to initial prompts
    terminal_initial_answer = None

    # Regex patterns for paging prompts
    terminal_inital_prompt_newline = True

    def on_open_shell(self):
        """Handle initial shell setup after connection."""
        # Many Zyxel switches don't support paging disable commands
        # or don't require them for CLI operations
        # Skip paging configuration to avoid connection timeouts
        pass

    def on_become(self, passwd=None):
        """Handle privilege escalation."""
        if self._get_prompt().endswith(b'#'):
            return

        cmd = {'command': 'enable'}
        if passwd:
            cmd['prompt'] = to_bytes(
                r"[\r\n]?[Pp]assword:",
                errors='surrogate_or_strict'
            )
            cmd['answer'] = passwd

        try:
            self._exec_cli_command(cmd['command'])
        except AnsibleConnectionFailure as e:
            prompt = self._get_prompt()
            if prompt is not None and prompt.endswith(b'#'):
                return
            raise AnsibleConnectionFailure(
                'unable to elevate privilege to enable mode, at prompt [%s] with error: %s'
                % (prompt, e.message if hasattr(e, 'message') else str(e))
            )

    def on_unbecome(self):
        """Handle privilege de-escalation."""
        prompt = self._get_prompt()
        if prompt is None:
            return

        if b'(config' in prompt:
            self._exec_cli_command(b'end')
            self._exec_cli_command(b'disable')
        elif prompt.endswith(b'#'):
            self._exec_cli_command(b'disable')

