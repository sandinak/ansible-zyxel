# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Unit tests for zyxel management modules (syslog, ntp, user) - HTTP API version.

Note: These modules are currently stubbed as HTTP API support is not yet implemented.
These tests verify the modules can be imported and have the expected structure.
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import pytest


class TestSyslogModule:
    """Tests for zyxel_syslog module."""

    def test_module_import(self):
        """Test that the module can be imported."""
        from ansible_collections.network.zyxel.plugins.modules import zyxel_syslog
        assert hasattr(zyxel_syslog, 'main')


class TestNtpModule:
    """Tests for zyxel_ntp module."""

    def test_module_import(self):
        """Test that the module can be imported."""
        from ansible_collections.network.zyxel.plugins.modules import zyxel_ntp
        assert hasattr(zyxel_ntp, 'main')


class TestUserModule:
    """Tests for zyxel_user module."""

    def test_module_import(self):
        """Test that the module can be imported."""
        from ansible_collections.network.zyxel.plugins.modules import zyxel_user
        assert hasattr(zyxel_user, 'main')

