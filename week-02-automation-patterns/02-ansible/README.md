# Ansible gNMI Interface Management with OpenConfig

A simple Ansible project for retrieving and configuring network interfaces using gNMI and OpenConfig models via **pygnmi**.

## 📋 What This Does

This project provides two main capabilities:
1. **Get Interfaces**: Retrieve current interface configurations from network devices
2. **Configure Interfaces**: Apply interface configurations to network devices

Both operations use **gNMI** (gRPC Network Management Interface) with **OpenConfig** data models via custom Ansible modules built on **pygnmi**.

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Ansible 2.9 or higher  
- Network device with gNMI support

### Installation

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   This installs Ansible, grpcio, protobuf, and **pygnmi**

2. **Create output directory** (if it doesn't exist):
   ```bash
   mkdir -p output
   ```

Note: No Ansible collections needed - this project uses custom modules!

## 📁 Project Structure

```
02-ansible/
├── ansible.cfg                    # Ansible configuration
├── inventory.yml                  # Device inventory  
├── requirements.txt               # Python dependencies (ansible, pygnmi)
├── get_interfaces.yml             # Playbook to retrieve interfaces
├── configure_interfaces.yml       # Playbook to configure interfaces
├── library/                       # Custom Ansible modules
│   ├── gnmi_get.py               # Custom module for gNMI Get (using pygnmi)
│   └── gnmi_set.py               # Custom module for gNMI Set (using pygnmi)
├── group_vars/
│   └── all.yml                   # Common variables (credentials)
├── host_vars/
│   └── devnet-sandbox-router-1.yml  # Device-specific configuration
└── output/                        # Retrieved interface data
```

## ⚙️ Configuration

### 1. Update Inventory

Edit [inventory.yml](inventory.yml) to add your devices:

```yaml
all:
  children:
    network_devices:
      hosts:
        router1:
          ansible_host: 192.168.1.10  # Device IP address
          ansible_port: 57400          # gNMI port
```

### 2. Configure Credentials

Edit [group_vars/all.yml](group_vars/all.yml):

```yaml
ansible_user: admin
ansible_password: your_password
```

### 3. Define Interface Configuration

Edit `host_vars/router1.yml` (create for each device):

```yaml
interfaces:
  - name: GigabitEthernet0/0/0/1
    description: "Uplink to Core"
    enabled: true
    mtu: 1500
    ipv4_address: 10.0.1.1
    ipv4_prefix_length: 24
```

## 🎯 Usage

**Important**: Use the Python environment where you installed the dependencies:

```bash
# If using a virtual environment (recommended):
/path/to/venv/bin/ansible-playbook get_interfaces.yml

# Or activate your venv first:
source /path/to/venv/bin/activate
ansible-playbook get_interfaces.yml
```

### Retrieve Interfaces

Get current interface information from all devices:

```bash
ansible-playbook get_interfaces.yml
```

Get interfaces from a specific device:

```bash
ansible-playbook get_interfaces.yml --limit router1
```

Results are saved in `output/<device>_interfaces.json`.

### Configure Interfaces

Apply interface configuration to all devices:

```bash
ansible-playbook configure_interfaces.yml
```

Configure a specific device:

```bash
ansible-playbook configure_interfaces.yml --limit router1
```

### Dry Run (Check Mode)

Test without making changes:

```bash
ansible-playbook configure_interfaces.yml --check
```

## 📝 Examples

### Example 1: Get Interfaces from Multiple Devices

```bash
# Run against all devices in inventory
ansible-playbook get_interfaces.yml

# Run against specific device
ansible-playbook get_interfaces.yml --limit devnet-sandbox-router-1
```

### Example 2: Configure Single Interface

Create `host_vars/router1.yml`:

```yaml
interfaces:
  - name: GigabitEthernet0/0/0/1
    description: "Management Interface"
    enabled: true
    mtu: 1500
```

Run:
```bash
ansible-playbook configure_interfaces.yml --limit router1
```

### Example 3: Configure Multiple Interfaces

Update `host_vars/router1.yml`:

```yaml
interfaces:
  - name: GigabitEthernet0/0/0/1
    description: "Uplink"
    enabled: true
    mtu: 9000
    ipv4_address: 10.0.1.1
    ipv4_prefix_length: 24
    
  - name: GigabitEthernet0/0/0/2
    description: "Downlink"
    enabled: true
    mtu: 1500
    ipv4_address: 10.0.2.1
    ipv4_prefix_length: 24
```

### Example 4: Configure Loopback Interfaces

Loopback interfaces are automatically detected and configured without MTU:

```yaml
interfaces:
  - name: Loopback23
    description: "Test Loopback"
    enabled: true
    ipv4_address: 192.0.2.31
    ipv4_prefix_length: 32
```

**Note**: The playbook automatically excludes MTU for loopback interfaces since they don't support this parameter on most platforms.

## 🔍 Interface Type Support

The playbooks automatically detect and assign the correct IANA interface type based on the interface name:

| Interface Type | Name Pattern | IANA Type | MTU Support |
|---------------|--------------|-----------|-------------|
| Loopback | `Loopback*` | `iana-if-type:softwareLoopback` | ❌ No |
| Tunnel | `Tunnel*` | `iana-if-type:tunnel` | ⚠️ Platform-dependent |
| VLAN | `Vlan*` | `iana-if-type:l3ipvlan` | ✅ Yes |
| Port-Channel | `Bundle-Ether*`, `Port-channel*` | `iana-if-type:ieee8023adLag` | ✅ Yes |
| Ethernet | `GigabitEthernet*`, `TenGigE*`, etc. | `iana-if-type:ethernetCsmacd` | ✅ Yes |
| Other | All others | `iana-if-type:other` | ⚠️ Platform-dependent |

**MTU Handling**: The configuration playbook automatically omits the MTU parameter for loopback interfaces. If you configure other interface types that don't support MTU, you may need to customize the playbook logic.

## 🔧 Troubleshooting

### Connection Issues

If you can't connect to the device:
- Verify the device IP and gNMI port in `inventory.yml`
- Check credentials in `group_vars/all.yml`
- Ensure gNMI is enabled on the device
- Verify network connectivity: `ping <device_ip>`

### Authentication Errors

- Double-check username and password in `group_vars/all.yml`
- Verify the user has proper permissions on the device

### Collection Not Found

**Solution**: No collections needed! This project uses custom modules.

### Module Not Found

**Solution**: Ensure `pygnmi` is installed:
```bash
pip install pygnmi
```

## 📚 Understanding the Components

### What is Ansible?
Ansible is agnmic?
gnmic is a command-line client for gNMI that makes it easy to interact with network devices. This project uses gnmic through Ansible's shell module.

### What is n automation tool that runs tasks on remote devices using "playbooks" (YAML files describing what to do).

### What is gNMI?
gNMI (gRPC Network Management Interface) is a modern protocol for managing network devices, using gRPC for efficiency.

### What is pygnmi?
pygnmi is a pure Python gNMI client library that provides a simple, Pythonic way to interact with network devices using the gNMI protocol. It's well-maintained and production-ready.

### What are the custom modules?
This project includes custom Ansible modules (`gnmi_get.py` and `gnmi_set.py`) that wrap pygnmi functionality, making it easy to use gNMI with OpenConfig in Ansible playbooks.

### What is OpenConfig?
OpenConfig provides vendor-neutral data models for network configuration, ensuring consistency across different device types.

### Playbook Structure

Each playbook has:
- **name**: Description of what the playbook does
- **hosts**: Which devices to run on (from inventory)
- **tasks**: List of actions to perform

## 🔐 Security Notes

For production use:
1. Use encrypted credentials (Ansible Vault):
   ```bash
   ansible-vault encrypt group_vars/all.yml
   ```

2. Enable secure connections:
   ```yaml
   gnmi_secure: true
   gnmi_validate_certs: true
   ```

3. Use certificate-based authentication when possible

## 📖 Additional Resources

- [Ansible Documentation](https://docs.ansible.com/)
- [pygnmi GitHub Repository](https://github.com/akarneliuk/pygnmi)
- [OpenConfig Models](https://www.openconfig.net/)
- [gNMI Specification](https://github.com/openconfig/gnmi)

## ❓ Common Questions

**Q: Do I need to install anything on the devices?**  
A: No, devices just need gNMI support enabled.

**Q: Can I use this with different vendors?**  
A: Yes! OpenConfig models work across vendors that support them.

**Q: How do I add more devices?**  
A: Add them to `inventory.yml` and create corresponding `host_vars/<device>.yml` files.

**Q: What happens if configuration fails?**  
A: Ansible will report the error and continue with other devices (use `--limit` to target specific devices).

## 📄 License

This project is provided as-is for educational and operational purposes.
