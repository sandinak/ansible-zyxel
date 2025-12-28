# Ansible Zyxel Collection

Ansible collection and roles for managing Zyxel switches via HTTP API.

## Overview

This repository contains:
- **`network.zyxel`** - An Ansible Galaxy collection for Zyxel switch management
- **Roles** - Reusable Ansible roles for common switch configurations

## Supported Switch Models

| Model | Status | Connection |
|-------|--------|------------|
| GS1920 Series | ✅ Tested | HTTPS API |
| GS1915 Series | ✅ Tested | HTTPS API |
| GS1900 Series | ✅ Tested | HTTPS API |

## Requirements

- Ansible 2.14+
- Python 3.9+
- `ansible.netcommon` collection

## Quick Start

### 1. Install the Collection

```bash
# Install from this repository
cd network/zyxel
ansible-galaxy collection build
ansible-galaxy collection install network-zyxel-*.tar.gz

# Install dependencies
ansible-galaxy collection install ansible.netcommon
```

### 2. Configure Inventory

Edit `inventory/hosts.yml` with your switch details:

```yaml
all:
  children:
    zyxel_switches:
      hosts:
        my-switch:
          ansible_host: 192.168.1.10
          zyxel_model: gs1920
      vars:
        ansible_connection: ansible.netcommon.httpapi
        ansible_network_os: network.zyxel.zyxel
        ansible_httpapi_use_ssl: true
        ansible_httpapi_validate_certs: false
        ansible_user: "{{ vault_zyxel_user }}"
        ansible_password: "{{ vault_zyxel_password }}"
```

### 3. Set Credentials

Edit `inventory/group_vars/all/vault.yml` and encrypt with ansible-vault:

```bash
ansible-vault encrypt inventory/group_vars/all/vault.yml
```

### 4. Run Playbook

```bash
ansible-playbook -i inventory/hosts.yml playbooks/zyxel.yml --ask-vault-pass
```

## Collection Modules

| Module | Description |
|--------|-------------|
| `zyxel_system` | System settings (hostname, location, contact, timezone) |
| `zyxel_port` | Individual port configuration |
| `zyxel_ports` | Bulk port configuration |
| `zyxel_ports_info` | Gather port information |
| `zyxel_vlan` | Individual VLAN configuration |
| `zyxel_vlans` | Bulk VLAN configuration |
| `zyxel_vlans_info` | Gather VLAN information |
| `zyxel_management` | Management services (SNMP, syslog, NTP, SSH, HTTPS) |
| `zyxel_aaa` | RADIUS and TACACS+ configuration |
| `zyxel_security` | Port security, 802.1X, DHCP snooping |
| `zyxel_spanning_tree` | Spanning tree configuration |
| `zyxel_lag` | Link aggregation groups |
| `zyxel_mirror` | Port mirroring |
| `zyxel_mac_address_table_info` | MAC address table information |

## Roles

| Role | Description |
|------|-------------|
| `zyxel_base` | Base system configuration |
| `zyxel_ports` | Port configuration role |
| `zyxel_vlans` | VLAN configuration role |
| `zyxel_security` | Security configuration role |

## Development

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run tests
cd network/zyxel
python -m pytest tests/unit/ -v

# Build collection
ansible-galaxy collection build --force
```

## License

MIT

## Author

Disconet

