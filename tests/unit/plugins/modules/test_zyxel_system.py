# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Unit tests for system and management modules - HTTP API version.

Note: These modules are currently stubbed as HTTP API support is not yet implemented.
These tests verify the modules can be imported and have the expected structure.
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import pytest


class TestManagementModule:
    """Tests for zyxel_management module."""

    def test_module_import(self):
        """Test that the module can be imported."""
        from ansible_collections.network.zyxel.plugins.modules import zyxel_management
        assert hasattr(zyxel_management, 'main')


class TestAaaModule:
    """Tests for zyxel_aaa module."""

    def test_module_import(self):
        """Test that the module can be imported."""
        from ansible_collections.network.zyxel.plugins.modules import zyxel_aaa
        assert hasattr(zyxel_aaa, 'main')

