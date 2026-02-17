# Week 2: Choose Your Love Language

**Part of the [Month of Smart Connections Lab](https://github.com/ponchotitlan/month-of-smart-connections-lab)**

Three distinct automation patterns for managing network interfaces using gNMI and OpenConfig. From raw Python scripting to declarative Ansible playbooks to fully automated CI/CD pipelines - pick the pattern that speaks your language, or master them all.

## The Many Faces of Network Automation

In network automation, there's no "one size fits all." The right approach depends on your team's skills, your operational maturity, and how much you value repeatability over flexibility. This week explores three patterns that represent an evolution in automation thinking:

- **🐍 Scripting:** Direct, imperative control. You write the exact steps. Perfect for one-off tasks, troubleshooting, or when you need to see exactly what's happening under the hood.

- **📜 Configuration Management (Ansible):** Declarative state management. You describe what you want, and let the tool figure out how to get there. Great for standardizing configurations across fleets of devices.

- **⚙️ CI/CD Pipelines:** Automated workflows triggered by events or schedules. The network configures itself based on code changes, pull requests, or manual triggers. This is where operations become truly programmable.

All three patterns in this repository use the same underlying technology - **gNMI (gRPC Network Management Interface)** with **OpenConfig** data models - but each wraps it differently to serve different needs.

## What's gNMI and OpenConfig?

Before diving into the patterns, let's briefly introduce the technologies that power all three approaches:

### gNMI (gRPC Network Management Interface)

gNMI is a modern network management protocol built on top of gRPC. Unlike traditional protocols (SNMP, NETCONF), gNMI offers:
- 🚀 **Streaming telemetry:** Real-time data delivery instead of polling
- 🔒 **Strong encryption:** Built on HTTP/2 and TLS
- 🎯 **Efficient and structured:** Protocol buffers for compact, strongly-typed data
- 🌐 **Vendor-neutral:** Supported by Cisco, Arista, Juniper, Nokia, and more

### OpenConfig

OpenConfig is a collaborative effort to define vendor-neutral, standards-based YANG models for network configuration and operational state. Instead of learning Cisco CLI, Juniper CLI, and Arista CLI separately, you work with a common data model.

Benefits:
- ✅ **Consistency:** Same data model across vendors
- ✅ **Predictability:** Strongly typed schemas reduce errors
- ✅ **Automation-friendly:** Designed for programmatic access from day one

Together, **gNMI + OpenConfig** provide a modern, programmable interface to network infrastructure, regardless of vendor.

### Helpful Resources

| Resource Type | Description |
|--------------|-------------|
| [📘 OpenConfig Models](https://github.com/openconfig/public) | Official OpenConfig YANG models repository |
| [📖 gNMI Specification](https://github.com/openconfig/reference/blob/master/rpc/gnmi/gnmi-specification.md) | Technical specification for gNMI protocol |
| [🐍 pygnmi Library](https://github.com/akarneliuk/pygnmi) | Python library for gNMI implementation (used in all projects) |
| [🧪 Cisco IOS XR Sandbox](https://devnetsandbox.cisco.com/RM/Diagram/Index/e83cfd31-ade3-4e15-91d6-3118b867a0dd?diagramType=Topology) | Free DevNet sandbox with gNMI/OpenConfig support |
| [📚 OpenConfig Documentation](https://www.openconfig.net/docs/) | Official documentation and tutorials |

## What's Included in this Repository

This repository contains three complete automation patterns, each progressively building on the previous one. All examples use the same OpenConfig interface model but implement it differently.

### Prerequisites

Before starting with any pattern, ensure you have:
- Python 3.8+ installed
- Access to a network device with gNMI enabled (or use [Cisco DevNet Sandbox](https://devnetsandbox.cisco.com))
- Basic understanding of network interfaces and IP addressing

### Pattern 1: Direct Scripting with Python

**📁 Location:** [01-scripting/](01-scripting/)

An interactive Python script that speaks gNMI directly. This is automation at its most transparent - you see every request and response, making it perfect for learning or debugging.

**What it does:**
- Connects to network devices via gNMI
- Retrieves interface information using OpenConfig models
- Configures interfaces interactively through a menu-driven CLI
- Displays formatted gNMI request/response payloads
- Automatically detects interface types (Ethernet, Loopback, VLAN, etc.)

**When to use this:**
- 🔍 Learning gNMI and OpenConfig fundamentals
- 🐛 Debugging network automation workflows
- 🛠 One-off configuration tasks
- 🎓 Training and demonstrations

**Setup:**

```bash
# Navigate to the scripting directory
cd week-02-automation-patterns/01-scripting

# Install dependencies
pip install -r requirements.txt
```

**Usage:**

```bash
# Connect to a device
python3 network_interface_manager.py \
    --host sandbox-iosxr-1.cisco.com \
    --username admin \
    --password C1sco12345 \
    --port 57777
```

**Interactive Menu:**

```
============================================================
🌐 OPENCONFIG gNMI INTERFACE MANAGER
============================================================
1. 📋 Retrieve Interface Information
2. ⚙️  Configure Interface
3. 🚪 Exit
============================================================

Enter your choice (1-3): 1

============================================================
📋 RETRIEVING INTERFACE INFORMATION
============================================================

📤 gNMI Get Request:
------------------------------------------------------------
{
  "path": [
    "openconfig-interfaces:interfaces/interface"
  ]
}
------------------------------------------------------------

Interface                      IP Address           Status       Description
════════════════════════════════════════════════════════════════════════════════════════════════════
GigabitEthernet0/0/0/0        10.10.20.48/24       ✓ up         to port6.sandbox-backend
GigabitEthernet0/0/0/1        172.16.255.1/24      ✓ up         to port7.sandbox-backend
Loopback100                   1.1.1.100/32         ✓ up         Test loopback
────────────────────────────────────────────────────────────────────────────────────────────────────

📊 Total interfaces: 3
```

**Example Configuration:**

```
============================================================
🌐 OPENCONFIG gNMI INTERFACE MANAGER
============================================================
1. 📋 Retrieve Interface Information
2. ⚙️  Configure Interface
3. 🚪 Exit
============================================================

Enter your choice (1-3): 2

------------------------------------------------------------
Enter interface name (e.g., GigabitEthernet0/0/0/0): Loopback200
Enter IP address: 192.0.2.200
Enter prefix length (e.g., 24): 32
Enter description (optional): Configured via gNMI Script
------------------------------------------------------------

============================================================
⚙️  CONFIGURING INTERFACE
============================================================

🔍 Detected interface type: iana-if-type:softwareLoopback

🔧 Applying OpenConfig configuration:
  Interface: Loopback200
  IP Address: 192.0.2.200/32
  Description: Configured via gNMI Script
  Status: enabled

📤 gNMI Set Request:
------------------------------------------------------------
{
  "openconfig-interfaces:interface": [
    {
      "name": "Loopback200",
      "config": {
        "name": "Loopback200",
        "type": "iana-if-type:softwareLoopback",
        "description": "Configured via gNMI Script",
        "enabled": true
      },
      "subinterfaces": {
        "subinterface": [
          {
            "index": 0,
            "openconfig-if-ip:ipv4": {
              "addresses": {
                "address": [
                  {
                    "ip": "192.0.2.200",
                    "config": {
                      "ip": "192.0.2.200",
                      "prefix-length": 32
                    }
                  }
                ]
              }
            }
          }
        ]
      }
    }
  ]
}
------------------------------------------------------------

✅ Configuration applied successfully.
```

### Pattern 2: Configuration Management with Ansible

**📁 Location:** [02-ansible/](02-ansible/)

Ansible playbooks with custom gNMI modules. This moves from imperative scripting to declarative configuration - you define the desired state, and Ansible ensures it's achieved.

**What it does:**
- Two playbooks: one for retrieving interfaces, one for configuring them
- Custom Ansible modules (`gnmi_get` and `gnmi_set`) wrap pygnmi
- Inventory-based management with host and group variables
- Idempotent operations (safe to run multiple times)
- Structured output saved to JSON files

**When to use this:**
- 🔁 Standardizing configurations across multiple devices
- 📋 Maintaining consistent state over time
- 👥 Teams already using Ansible for other infrastructure
- 📊 Audit trails and change tracking via version control

**Setup:**

```bash
# Navigate to the ansible directory
cd week-02-automation-patterns/02-ansible

# Install dependencies
pip install -r requirements.txt
```

**Project Structure:**

```
02-ansible/
├── ansible.cfg                 # Ansible configuration
├── inventory.yml               # Device inventory
├── get_interfaces.yml          # Playbook to retrieve interfaces
├── configure_interfaces.yml    # Playbook to configure interfaces
├── group_vars/
│   └── all.yml                 # Variables for all devices
├── host_vars/
│   └── devnet-sandbox-router-1.yml  # Device-specific configuration
├── library/
│   ├── gnmi_get.py             # Custom Ansible module for gNMI Get
│   └── gnmi_set.py             # Custom Ansible module for gNMI Set
└── output/
    └── devnet-sandbox-router-1_interfaces.json  # Retrieved data
```

**Configuration:**

Edit [inventory.yml](02-ansible/inventory.yml) to add your devices:

```yaml
---
all:
  children:
    network_devices:
      hosts:
        devnet-sandbox-router-1:
          ansible_host: sandbox-iosxr-1.cisco.com
          ansible_port: 57777
```

Edit [group_vars/all.yml](02-ansible/group_vars/all.yml) for credentials:

```yaml
---
# gNMI connection credentials
ansible_user: admin
ansible_password: C1sco12345
```

Define interfaces in [host_vars/devnet-sandbox-router-1.yml](02-ansible/host_vars/devnet-sandbox-router-1.yml):

```yaml
---
interfaces:
  - name: Loopback100
    description: "Configured by Ansible"
    enabled: true
    ipv4_address: 192.0.2.100
    ipv4_prefix_length: 32
    
  - name: Loopback101
    description: "Another test interface"
    enabled: true
    ipv4_address: 192.0.2.101
    ipv4_prefix_length: 32
```

**Usage:**

```bash
# Retrieve interface information
ansible-playbook get_interfaces.yml

# Configure interfaces based on host_vars
ansible-playbook configure_interfaces.yml

# Target specific hosts
ansible-playbook configure_interfaces.yml --limit devnet-sandbox-router-1

# Verbose output
ansible-playbook get_interfaces.yml -v
```

**Example Output:**

```
$ ansible-playbook get_interfaces.yml

PLAY [Retrieve Interface Information via gNMI] *********************************

TASK [Get all interfaces using OpenConfig] *************************************
ok: [devnet-sandbox-router-1]

TASK [Save interface data to file] *********************************************
changed: [devnet-sandbox-router-1]

TASK [Display summary] *********************************************************
ok: [devnet-sandbox-router-1] => 
  msg: |-
    ================================================
    Successfully retrieved interfaces from devnet-sandbox-router-1
    Data saved to: ./output/devnet-sandbox-router-1_interfaces.json
    ================================================

PLAY RECAP *********************************************************************
devnet-sandbox-router-1    : ok=3    changed=1    unreachable=0    failed=0
```

```
$ ansible-playbook configure_interfaces.yml

PLAY [Configure Interfaces via gNMI] *******************************************

TASK [Validate interface configuration exists] *********************************
ok: [devnet-sandbox-router-1] => 
  msg: Found 2 interface(s) to configure

TASK [Configure each interface using OpenConfig] *******************************
changed: [devnet-sandbox-router-1] => (item=Loopback100)
changed: [devnet-sandbox-router-1] => (item=Loopback101)

TASK [Display configuration summary] *******************************************
ok: [devnet-sandbox-router-1] => 
  msg: |-
    ================================================
    Successfully configured 2 interface(s) on devnet-sandbox-router-1
    ================================================

PLAY RECAP *********************************************************************
devnet-sandbox-router-1    : ok=3    changed=1    unreachable=0    failed=0
```

### Pattern 3: CI/CD Pipeline with GitHub Actions

**📁 Location:** [03-cicd/](03-cicd/) + [.github/workflows/ci.yml](../../.github/workflows/ci.yml)

A GitHub Actions workflow that runs the Ansible playbooks automatically. This is "infrastructure as code" in its final form - network changes driven by commits, pull requests, or scheduled triggers.

**What it does:**
- Workflow dispatch (manual trigger) with selectable actions
- Provisions Python virtual environment automatically
- Runs Ansible playbooks in isolated environment
- Uploads interface data as build artifacts
- Cleans up resources after completion
- Provides detailed workflow summaries

**When to use this:**
- 🔄 Automating routine network configuration tasks
- 🧪 Testing network changes in staging before production
- 📅 Scheduled configuration audits or backups
- 🚀 GitOps-style workflows where Git is the source of truth

**Setup:**

This workflow requires a [GitHub Actions self-hosted runner](https://docs.github.com/en/actions/hosting-your-own-runners/about-self-hosted-runners) configured in your repository. The runner needs:
- Python 3.8+ installed
- Network connectivity to target devices
- Proper credentials (stored as repository secrets or in checked-in vars)

**Workflow Configuration:**

The workflow is defined in [.github/workflows/ci.yml](../../.github/workflows/ci.yml) and supports three actions:

1. **get_interfaces** - Retrieves interface information
2. **configure_interfaces** - Applies interface configurations
3. **both** - Runs both operations in sequence

**Triggering the Workflow:**

1. Navigate to **Actions** tab in your GitHub repository
2. Select **🔧 Ansible Network Automation CI** workflow
3. Click **Run workflow** button
4. Select your desired action and optionally specify a target host
5. Click **Run workflow**

**Workflow Inputs:**

| Input | Description | Options |
|-------|-------------|---------|
| `action` | Action to perform | `get_interfaces`, `configure_interfaces`, `both` |
| `target_host` | Target host (optional) | Leave empty for all hosts or specify a host from inventory |

**Workflow Stages:**

```
🚀 Setup Environment
   └─> Creates Python venv
   └─> Installs Ansible + dependencies

📡 Get Network Interfaces (if selected)
   └─> Runs get_interfaces.yml playbook
   └─> Uploads output as artifact
   
⚙️ Configure Network Interfaces (if selected)
   └─> Runs configure_interfaces.yml playbook
   └─> Applies interface configurations

📊 Workflow Summary
   └─> Generates execution report

🧹 Cleanup Environment
   └─> Removes virtual environment
```

**Example Workflow Run:**

<div align="center">
<img src="../images/week2_githubactions.png"/></br>
</div>

Once triggered, you'll see output like:

```
🚀 Setup Environment
  📥 Checkout repository
  ✅ Repository checked out
  
  🐍 Create Python virtual environment
  ✅ Virtual environment created
  ✅ Dependencies installed

📡 Get Network Interfaces
  ▶️ Run Get Interfaces Playbook
  ✅ Playbook executed successfully
  
  📤 Upload Get Interfaces Output
  ✅ Artifact uploaded: get-interfaces-output-42

⚙️ Configure Network Interfaces
  ▶️ Run Configure Interfaces Playbook
  ✅ 2 interface(s) configured on devnet-sandbox-router-1

📊 Workflow Summary
  - Action: both
  - Target Host: all
  
  Job Results:
  - Setup: success
  - Get Interfaces: success
  - Configure Interfaces: success

🧹 Cleanup Environment
  ✅ Virtual environment removed
```

**Downloading Artifacts:**

After a successful run with the `get_interfaces` action, download the interface data:
1. Go to the workflow run summary
2. Scroll to **Artifacts** section
3. Download `get-interfaces-output-{run-number}.zip`
4. Extract to view JSON files with interface data

## Comparison: Which Pattern Should You Choose?

| Aspect | 🐍 Scripting | 📜 Ansible | ⚙️ CI/CD |
|--------|-------------|-----------|---------|
| **Learning Curve** | Low | Medium | High |
| **Flexibility** | Very High | Medium | Low |
| **Repeatability** | Low | High | Very High |
| **Idempotency** | Manual | Built-in | Built-in |
| **Version Control** | Code only | Code + State | Code + State + History |
| **Team Collaboration** | Difficult | Good | Excellent |
| **Best For** | Exploration, debugging | Standardization | Full automation |
| **Execution** | On-demand | On-demand | Event-driven |

**Recommendation:**
- Start with **scripting** to understand gNMI and OpenConfig
- Graduate to **Ansible** when managing multiple devices
- Implement **CI/CD** when you need auditability and automation at scale


## Additional Resources

| Resource | Description |
|----------|-------------|
| [🎓 gNMI/OpenConfig Tutorial](https://github.com/openconfig/gnmi) | Official gNMI getting started guide |
| [📖 Ansible Network Automation](https://docs.ansible.com/ansible/latest/network/index.html) | Ansible's network automation documentation |
| [⚙️ GitHub Actions Documentation](https://docs.github.com/en/actions) | Complete GitHub Actions reference |
| [🐍 pygnmi Examples](https://github.com/akarneliuk/pygnmi/tree/master/examples) | More pygnmi code examples |
| [🏗 Network CI/CD Best Practices](https://www.ciscolive.com/c/dam/r/ciscolive/emea/docs/2020/pdf/DEVNET-2594.pdf) | Cisco Live presentation on network CI/CD |

---
**⬅️ Previous Week:** [Week 1 - Loving All Vendors](../week-01-automation-multivendor/)</br>
**➡️ Next Week:** [Week 3 - Trust Issues](../week-03-automation-testing/)</br>
**📚 Main Repository:** [Month of Smart Connections Lab](https://github.com/ponchotitlan/month-of-smart-connections-lab)