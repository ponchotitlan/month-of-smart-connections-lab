# Custom Ansible gNMI Modules

This directory contains custom Ansible modules for gNMI communication using **pygnmi**.

## Modules

### gnmi_get.py
Retrieve configuration and state data from network devices using gNMI with OpenConfig.

**Example:**
```yaml
- name: Get all interfaces
  gnmi_get:
    host: "{{ ansible_host }}"
    port: 57400
    username: admin
    password: secret
    path: "openconfig-interfaces:interfaces/interface"
```

### gnmi_set.py
Configure network devices using gNMI Set operations with OpenConfig.

**Example:**
```yaml
- name: Configure interface
  gnmi_set:
    host: "{{ ansible_host }}"
    port: 57400
    username: admin
    password: secret
    update:
      - path: "openconfig-interfaces:interfaces/interface"
        value:
          name: "GigabitEthernet0/0/0/1"
          config:
            description: "Updated via Ansible"
            enabled: true
```

## Why Custom Modules?

The official `ansible.netcommon.grpc_*` modules don't support OpenConfig paths natively - they're designed for vendor-specific YANG models (like Cisco IOS-XR native models).

These custom modules wrap **pygnmi**, a mature Python gNMI client library, giving you:
- ✅ **Native OpenConfig support** - Works with standard OpenConfig paths
- ✅ **Production-ready** - Built on well-tested pygnmi library  
- ✅ **Simple** - Clean Pythonic interface
- ✅ **Vendor-agnostic** - Works with any gNMI-enabled device

## Requirements

```bash
pip install pygnmi
```

The modules automatically import pygnmi and will fail gracefully with a helpful error if it's not installed.
