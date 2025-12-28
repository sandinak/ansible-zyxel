# Ansible Collection - network.zyxel

This collection provides Ansible modules for managing Zyxel network switches.

## Description

The `network.zyxel` collection enables automation of Zyxel switch configuration including:
- Port management (speed, duplex, flow control, descriptions)
- VLAN management (create, update, delete VLANs)
- Trunk/LAG configuration (static and LACP)
- PVID (Port VLAN ID) configuration
- System management (syslog, NTP, users)

## Requirements

- Ansible >= 2.14.0
- Python >= 3.9
- ansible.netcommon >= 2.0.0

## Installation

```bash
ansible-galaxy collection install network.zyxel
```

Or install from source:

```bash
cd network/zyxel
ansible-galaxy collection build
ansible-galaxy collection install network-zyxel-1.0.0.tar.gz
```

## Supported Devices

- Zyxel GS2220 Series
- Zyxel GS1920 Series
- Zyxel XGS Series
- Other Zyxel managed switches with CLI access

## Modules

### Bulk Configuration Modules

| Module | Description |
|--------|-------------|
| `zyxel_ports` | Bulk configure multiple ports using a dictionary |
| `zyxel_vlans` | Bulk configure multiple VLANs using a dictionary |
| `zyxel_ports_info` | Gather port information as a dictionary |
| `zyxel_vlans_info` | Gather VLAN information as a dictionary |

### Individual Configuration Modules

| Module | Description |
|--------|-------------|
| `zyxel_port` | Manage individual port settings (speed, duplex, flow control) |
| `zyxel_trunk` | Manage trunk/LAG groups |
| `zyxel_vlan` | Manage individual VLANs |
| `zyxel_pvid` | Manage port VLAN IDs |
| `zyxel_lag` | Advanced LAG configuration with LACP support |

### System & Management Modules

| Module | Description |
|--------|-------------|
| `zyxel_system` | Configure system settings (hostname, location, contact) |
| `zyxel_management` | Consolidated management (SNMP, syslog, NTP, SSH, HTTPS) |
| `zyxel_syslog` | Configure syslog servers |
| `zyxel_ntp` | Configure NTP servers |
| `zyxel_user` | Manage user accounts |

### Security & AAA Modules

| Module | Description |
|--------|-------------|
| `zyxel_aaa` | Configure RADIUS and TACACS+ authentication |
| `zyxel_security` | Port security, 802.1X, DHCP snooping, ARP inspection |

### Advanced Networking Modules

| Module | Description |
|--------|-------------|
| `zyxel_spanning_tree` | Configure STP/RSTP/MSTP settings |
| `zyxel_mirror` | Configure port mirroring (SPAN) sessions |
| `zyxel_mac_address_table_info` | Gather MAC address table information |

## Usage Examples

### Inventory Configuration

```yaml
# inventory.yml
all:
  hosts:
    zyxel_switch:
      ansible_host: 192.168.1.1
      ansible_user: admin
      ansible_password: password
      ansible_connection: ansible.netcommon.network_cli
      ansible_network_os: network.zyxel.zyxel
```

### Port Configuration

```yaml
- name: Configure switch port
  network.zyxel.zyxel_port:
    name: "1"
    state: enabled
    speed: "1000"
    duplex: full
    flow_control: true
    description: "Uplink to Core"
```

### VLAN Management

```yaml
- name: Create VLAN
  network.zyxel.zyxel_vlan:
    vlan_id: 100
    name: "Management"
    tagged_ports:
      - "24"
    untagged_ports:
      - "1"
      - "2"
      - "3"
```

### Trunk Configuration

```yaml
- name: Create LACP trunk
  network.zyxel.zyxel_trunk:
    group: 1
    members:
      - "1"
      - "2"
    mode: lacp
    lacp_mode: active
```

## Testing

### Unit Tests

```bash
cd network/zyxel
pytest tests/unit/ -v
```

### Integration Tests

```bash
# Copy and configure the integration config
cp tests/integration/integration_config.yml.template tests/integration/integration_config.yml
# Edit with your device details

# Run integration tests
ansible-test integration --local
```

## License

GNU General Public License v3.0+

## Author

Ansible Network Team

## Links

- [Ansible Documentation](https://docs.ansible.com/)
- [Zyxel Support](https://www.zyxel.com/support/)
