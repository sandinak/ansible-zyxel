# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Unit tests for advanced modules (mirror, LAG, MAC table) - HTTP API version.

Note: These modules are currently stubbed as HTTP API support is not yet implemented.
These tests verify the modules can be imported and have the expected structure.
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import pytest


class TestMirrorModule:
    """Tests for zyxel_mirror module."""

    def test_module_import(self):
        """Test that the module can be imported."""
        from ansible_collections.network.zyxel.plugins.modules import zyxel_mirror
        assert hasattr(zyxel_mirror, 'main')


class TestLagModule:
    """Tests for zyxel_lag module."""

    def test_module_import(self):
        """Test that the module can be imported."""
        from ansible_collections.network.zyxel.plugins.modules import zyxel_lag
        assert hasattr(zyxel_lag, 'main')


class TestMacTableModule:
    """Tests for zyxel_mac_address_table_info module."""

    def test_module_import(self):
        """Test that the module can be imported."""
        from ansible_collections.network.zyxel.plugins.modules import zyxel_mac_address_table_info
        assert hasattr(zyxel_mac_address_table_info, 'main')

