# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Unit tests for bulk port and VLAN modules - HTTP API version.

Note: These modules are currently stubbed as HTTP API support is not yet implemented.
These tests verify the modules can be imported and have the expected structure.
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import pytest


class TestPortsModule:
    """Tests for zyxel_ports module."""

    def test_module_import(self):
        """Test that the module can be imported."""
        from ansible_collections.network.zyxel.plugins.modules import zyxel_ports
        assert hasattr(zyxel_ports, 'main')


class TestVlansModule:
    """Tests for zyxel_vlans module."""

    def test_module_import(self):
        """Test that the module can be imported."""
        from ansible_collections.network.zyxel.plugins.modules import zyxel_vlans
        assert hasattr(zyxel_vlans, 'main')

