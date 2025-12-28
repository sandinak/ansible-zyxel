# -*- coding: utf-8 -*-
# Copyright: (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Unit tests for Zyxel httpapi plugin parsing methods for GS1900/GS1915/GS1920."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import pytest
from unittest.mock import MagicMock, patch

from ansible_collections.network.zyxel.plugins.httpapi.zyxel import (
    HttpApi,
    encode_gs1900_password,
)


# Sample HTML data for GS1900
# GS1900 VLAN list pattern: VID, Name, Type (Default/Static)
GS1900_VLAN_HTML = '''
<td class="font-4" ><div align=center>1</div></td>
<td class="font-4" ><div align=center>default</div></td>
<td class="font-4" ><div align=center>Default</div></td>
<td class="font-4" ><div align=center>100</div></td>
<td class="font-4" ><div align=center>Management</div></td>
<td class="font-4" ><div align=center>Static</div></td>
'''

# GS1900 port settings pattern: checkbox, port num, PVID, AcceptFrame, IngressCheck, VLANTrunk
GS1900_VLAN_PORT_HTML = '''
<input type="checkbox" name="port" value="1">
<td class="font-4" ><div align=center>1</div></td>
<td class="font-4" ><div align=center>100</div></td>
<td class="font-4" ><div align=center>ALL</div></td>
<td class="font-4" ><div align=center>Disable</div></td>
<td class="font-4" ><div align=center>Enable</div></td>
<input type="checkbox" name="port" value="2">
<td class="font-4" ><div align=center>2</div></td>
<td class="font-4" ><div align=center>1</div></td>
<td class="font-4" ><div align=center>TagOnly</div></td>
<td class="font-4" ><div align=center>Enable</div></td>
<td class="font-4" ><div align=center>Disable</div></td>
'''

GS1900_PORT_HTML = '''
<input type="checkbox" name="port" value="1">
<td class="font-4" ><div align=center>1</div></td>
<td class="font-4" ><div align=center>Port1</div></td>
<td class="font-4" ><div align=center>Enable</div></td>
<td class="font-4" ><div align=center>Up</div></td>
<td class="font-4" ><div align=center>Auto</div></td>
<td class="font-4" ><div align=center>Auto</div></td>
<td class="font-4" ><div align=center>Disable</div></td>

<input type="checkbox" name="port" value="2">
<td class="font-4" ><div align=center>2</div></td>
<td class="font-4" ><div align=center>Uplink</div></td>
<td class="font-4" ><div align=center>Disable</div></td>
<td class="font-4" ><div align=center>Down</div></td>
<td class="font-4" ><div align=center>1000M</div></td>
<td class="font-4" ><div align=center>Full</div></td>
<td class="font-4" ><div align=center>Enable</div></td>
'''

# Sample HTML data for GS1915 - uses rpvlanstatusStatistics.html format
# Pattern: <a href='US/{VID}/rpvlanstatusStatisticsDetail.html'>index</a> VID Name Untagged Tagged
GS1915_VLAN_HTML = '''
<a href='US/1/rpvlanstatusStatisticsDetail.html'>1</a>
<div align=center>1</div>
<div align=center>default</div>
<div align=center>1-4</div>
<div align=center></div>
<a href='US/100/rpvlanstatusStatisticsDetail.html'>2</a>
<div align=center>100</div>
<div align=center>Management</div>
<div align=center>5-6</div>
<div align=center>7-8</div>
'''

# Sample HTML data for GS1920 (uses same patterns as GS1915)
GS1920_VLAN_HTML = '''
<a href='US/1/rpvlanstatusStatisticsDetail.html'>1</a>
<div align=center>1</div>
<div align=center>default</div>
<div align=center>1-4</div>
<div align=center></div>
<a href='US/200/rpvlanstatusStatisticsDetail.html'>2</a>
<div align=center>200</div>
<div align=center>Servers</div>
<div align=center>5-8</div>
<div align=center>9-12</div>
'''

# GS1920 port HTML - uses rpPort_Ipt_PortName and rpPort_Chk_PortActive patterns
GS1920_PORT_HTML = '''
<input type="checkbox" name="rpPort_Chk_PortActive" value="?1" checked>
<input type="text" name="rpPort_Ipt_PortName?1" VALUE="Database" maxlength="12">
<select name="rpPort_Slt_Speed?1"><OPTION VALUE=5 SELECTED>Auto</option></select>
<input type="checkbox" name="rpPort_Chk_PortActive" value="?2">
<input type="text" name="rpPort_Ipt_PortName?2" VALUE="Gateway" maxlength="12">
<select name="rpPort_Slt_Speed?2"><OPTION VALUE=4 SELECTED>100M</option></select>
'''

# GS1920 VLAN port settings - uses rpVlanport_Ipt_PVID pattern
GS1920_VLAN_PORT_HTML = '''
<input type="text" name="rpVlanport_Ipt_PVID?1" VALUE="200" maxlength="4">
<input type="checkbox" name="rpVlanport_Chk_Ingress" VALUE="?1">
<input type="checkbox" name="rpVlanport_Chk_VLANTrunking" VALUE="?1" CHECKED>
<input type="text" name="rpVlanport_Ipt_PVID?2" VALUE="1" maxlength="4">
<input type="checkbox" name="rpVlanport_Chk_Ingress" VALUE="?2" CHECKED>
<input type="checkbox" name="rpVlanport_Chk_VLANTrunking" VALUE="?2">
'''

GS1915_PORT_HTML = '''
<input type="checkbox" name="rpport_ChkPortActive" VALUE="?1" checked>
<input type="text" name="rpport_IptPortName?1" VALUE="Server1" maxlength="12">
<select name="rpport_OptSpeed?1"><option value="5" selected>Auto</option></select>
<input type="checkbox" name="rpport_ChkPortActive" VALUE="?2">
<input type="text" name="rpport_IptPortName?2" VALUE="Uplink" maxlength="12">
<select name="rpport_OptSpeed?2"><option value="3" selected>1000M</option></select>
'''

# GS1915 VLAN port settings - uses rpvlanport_IptPVID pattern
GS1915_VLAN_PORT_HTML = '''
<input type="text" name="rpvlanport_IptPVID?1" VALUE="100" maxlength="4">
<input type="checkbox" name="rpvlanport_ChkIngress" VALUE="?1" CHECKED>
<input type="checkbox" name="rpvlanport_ChkVLANTrunking" VALUE="?1" CHECKED>
<input type="text" name="rpvlanport_IptPVID?2" VALUE="1" maxlength="4">
<input type="checkbox" name="rpvlanport_ChkIngress" VALUE="?2">
<input type="checkbox" name="rpvlanport_ChkVLANTrunking" VALUE="?2">
'''


class TestEncodeGs1900Password:
    """Tests for the GS1900 password encoding function."""

    def test_short_password(self):
        """Test encoding a short password."""
        result = encode_gs1900_password("test")
        assert len(result) == 321
        # Verify length encoding positions
        assert result[122] == '0'  # tens digit of length (0 for 4)
        assert result[288] == '4'  # ones digit of length

    def test_long_password(self):
        """Test encoding a longer password."""
        result = encode_gs1900_password("mypassword123")
        assert len(result) == 321
        assert result[122] == '1'  # tens digit (13 -> 1)
        assert result[288] == '3'  # ones digit (13 -> 3)

    def test_password_chars_embedded(self):
        """Test that password characters are embedded correctly."""
        password = "abc"
        result = encode_gs1900_password(password)
        # Password chars should be at positions 5, 10, 15 (reversed: c, b, a)
        assert result[4] == 'c'   # position 5 (0-indexed = 4)
        assert result[9] == 'b'   # position 10 (0-indexed = 9)
        assert result[14] == 'a'  # position 15 (0-indexed = 14)


class TestHttpApiParsing:
    """Tests for HttpApi parsing methods."""

    @pytest.fixture
    def mock_httpapi(self):
        """Create a mock HttpApi instance."""
        mock_connection = MagicMock()
        mock_connection.get_option.return_value = None
        with patch.object(HttpApi, '__init__', lambda x, y: None):
            httpapi = HttpApi(mock_connection)
            httpapi.connection = mock_connection
            httpapi._model = None
            httpapi._logged_in = False
            httpapi._auth_id = None
            httpapi._firmware_version = None
        return httpapi

    # GS1900 VLAN parsing tests
    def test_parse_vlans_gs1900(self, mock_httpapi):
        """Test parsing VLANs from GS1900 HTML.

        Note: GS1900 VLAN list only returns VID, name, and type.
        Port membership is retrieved separately.
        """
        result = mock_httpapi._parse_vlans_info_gs1900(GS1900_VLAN_HTML)
        assert '1' in result
        assert result['1']['name'] == 'default'
        assert result['1']['active'] is True
        # GS1900 VLAN list doesn't include port membership - that's a separate call
        assert result['1']['untagged_ports'] == []
        assert result['1']['tagged_ports'] == []
        assert '100' in result
        assert result['100']['name'] == 'Management'

    # GS1900 VLAN port parsing tests
    def test_parse_vlan_ports_gs1900(self, mock_httpapi):
        """Test parsing VLAN port settings from GS1900 HTML."""
        result = mock_httpapi._parse_port_settings_gs1900(GS1900_VLAN_PORT_HTML)
        assert '1' in result
        assert result['1']['pvid'] == 100
        assert result['1']['vlan_trunking'] is True
        assert result['1']['ingress_filtering'] is False
        assert '2' in result
        assert result['2']['pvid'] == 1
        assert result['2']['ingress_filtering'] is True

    # GS1900 Port parsing tests
    def test_parse_ports_gs1900(self, mock_httpapi):
        """Test parsing port info from GS1900 HTML."""
        result = mock_httpapi._parse_ports_info(GS1900_PORT_HTML, 'gs1900')
        assert '1' in result
        assert result['1']['name'] == 'Port1'
        assert result['1']['enabled'] is True
        assert result['1']['link_status'] == 'up'
        assert '2' in result
        assert result['2']['name'] == 'Uplink'
        assert result['2']['enabled'] is False

    # GS1915 VLAN parsing tests
    def test_parse_vlans_gs1915(self, mock_httpapi):
        """Test parsing VLANs from GS1915 HTML."""
        result = mock_httpapi._parse_vlans_info_gs1915(GS1915_VLAN_HTML)
        assert '1' in result
        assert result['1']['name'] == 'default'
        assert '100' in result
        assert result['100']['name'] == 'Management'

    # GS1915 Port parsing tests
    def test_parse_ports_gs1915(self, mock_httpapi):
        """Test parsing port info from GS1915 HTML."""
        result = mock_httpapi._parse_ports_info(GS1915_PORT_HTML, 'gs1915')
        assert '1' in result
        assert result['1']['name'] == 'Server1'
        assert result['1']['enabled'] is True
        assert '2' in result
        assert result['2']['name'] == 'Uplink'
        assert result['2']['enabled'] is False

    # GS1915 VLAN port parsing tests
    def test_parse_vlan_ports_gs1915(self, mock_httpapi):
        """Test parsing VLAN port settings from GS1915 HTML."""
        result = mock_httpapi._parse_vlan_port_settings(GS1915_VLAN_PORT_HTML)
        assert '1' in result
        assert result['1']['pvid'] == 100
        assert result['1']['ingress_filtering'] is True
        assert result['1']['vlan_trunking'] is True
        assert '2' in result
        assert result['2']['pvid'] == 1

    # GS1920 VLAN parsing tests (uses same parser as GS1915)
    def test_parse_vlans_gs1920(self, mock_httpapi):
        """Test parsing VLANs from GS1920 HTML."""
        result = mock_httpapi._parse_vlans_info_gs1915(GS1920_VLAN_HTML)
        assert '1' in result
        assert result['1']['name'] == 'default'
        assert '200' in result
        assert result['200']['name'] == 'Servers'

    # GS1920 Port parsing tests
    def test_parse_ports_gs1920(self, mock_httpapi):
        """Test parsing port info from GS1920 HTML."""
        result = mock_httpapi._parse_ports_info(GS1920_PORT_HTML, 'gs1920')
        assert '1' in result
        assert result['1']['name'] == 'Database'
        assert result['1']['enabled'] is True
        assert '2' in result
        assert result['2']['name'] == 'Gateway'
        assert result['2']['enabled'] is False

    # GS1920 VLAN port parsing tests
    def test_parse_vlan_ports_gs1920(self, mock_httpapi):
        """Test parsing VLAN port settings from GS1920 HTML."""
        result = mock_httpapi._parse_vlan_port_settings(GS1920_VLAN_PORT_HTML)
        assert '1' in result
        assert result['1']['pvid'] == 200
        assert result['1']['vlan_trunking'] is True
        assert '2' in result
        assert result['2']['pvid'] == 1


class TestModelDetection:
    """Tests for model detection."""

    @pytest.fixture
    def mock_httpapi(self):
        """Create a mock HttpApi instance."""
        mock_connection = MagicMock()
        mock_connection.get_option.return_value = None
        with patch.object(HttpApi, '__init__', lambda x, y: None):
            httpapi = HttpApi(mock_connection)
            httpapi.connection = mock_connection
            httpapi._model = None
            httpapi._logged_in = False
            httpapi._auth_id = None
            httpapi._firmware_version = None
            httpapi.get_option = MagicMock(return_value=None)
        return httpapi

    def test_detect_model_from_option(self, mock_httpapi):
        """Test model detection from option."""
        mock_httpapi.get_option = MagicMock(return_value='gs1915')
        result = mock_httpapi.detect_model()
        assert result == 'gs1915'

    def test_model_caching(self, mock_httpapi):
        """Test that model is cached after first detection."""
        mock_httpapi._model = 'gs1900'
        result = mock_httpapi.detect_model()
        assert result == 'gs1900'
        # get_option should not be called since model is cached
        mock_httpapi.get_option.assert_not_called()

