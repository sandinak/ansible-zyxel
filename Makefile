# Disconet Ansible Infrastructure Makefile
SHELL := /bin/bash
VENV_DIR := .venv
PYTHON := python3
PIP := $(VENV_DIR)/bin/pip
ANSIBLE := $(VENV_DIR)/bin/ansible
ANSIBLE_PLAYBOOK := $(VENV_DIR)/bin/ansible-playbook
ANSIBLE_GALAXY := $(VENV_DIR)/bin/ansible-galaxy
ANSIBLE_LINT := $(VENV_DIR)/bin/ansible-lint

.PHONY: all venv deps collections lint test clean check help ping

# Default target
all: venv deps collections

# Create virtual environment
$(VENV_DIR)/bin/activate:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV_DIR)
	$(PIP) install --upgrade pip

venv: $(VENV_DIR)/bin/activate

# Install Python dependencies
deps: venv
	@echo "Installing Python dependencies..."
	$(PIP) install -r requirements.txt
	@touch $(VENV_DIR)/.deps_installed

# Install Ansible collections
collections: deps
	@echo "Installing Ansible collections..."
	$(ANSIBLE_GALAXY) collection install -r requirements.yml --force
	@touch $(VENV_DIR)/.collections_installed

# Lint playbooks and roles
lint: deps
	@echo "Linting Ansible code..."
	$(ANSIBLE_LINT) playbooks/ roles/

# Syntax check all playbooks
check: deps
	@echo "Checking playbook syntax..."
	$(ANSIBLE_PLAYBOOK) --syntax-check playbooks/*.yml

# Test connectivity to all hosts
ping: deps
	@echo "Testing connectivity..."
	$(ANSIBLE) all -m ping

# Run specific playbook
play: deps collections
ifdef PLAYBOOK
	$(ANSIBLE_PLAYBOOK) playbooks/$(PLAYBOOK)
else
	@echo "Usage: make play PLAYBOOK=<playbook.yml>"
endif

# Deploy to specific device type
pfsense: deps collections
	$(ANSIBLE_PLAYBOOK) playbooks/pfsense.yml

zyxel: deps collections
	$(ANSIBLE_PLAYBOOK) playbooks/zyxel.yml

proxmox: deps collections
	$(ANSIBLE_PLAYBOOK) playbooks/proxmox.yml

# Deploy everything
site: deps collections
	$(ANSIBLE_PLAYBOOK) playbooks/site.yml

# Clean up
clean:
	@echo "Cleaning up..."
	rm -rf $(VENV_DIR)
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.retry" -delete

# Help
help:
	@echo "Disconet Ansible Infrastructure"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Setup targets:"
	@echo "  all          - Setup venv, deps, and collections (default)"
	@echo "  venv         - Create Python virtual environment"
	@echo "  deps         - Install Python dependencies"
	@echo "  collections  - Install Ansible collections"
	@echo ""
	@echo "Validation targets:"
	@echo "  lint         - Lint playbooks and roles"
	@echo "  check        - Syntax check all playbooks"
	@echo "  ping         - Test connectivity to all hosts"
	@echo ""
	@echo "Deployment targets:"
	@echo "  site         - Deploy full site configuration"
	@echo "  pfsense      - Deploy pfSense configuration"
	@echo "  zyxel        - Deploy Zyxel switch configuration"
	@echo "  proxmox      - Deploy Proxmox VM configuration"
	@echo "  play         - Run specific playbook (PLAYBOOK=name.yml)"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean        - Remove venv and temp files"
	@echo "  help         - Show this help"
