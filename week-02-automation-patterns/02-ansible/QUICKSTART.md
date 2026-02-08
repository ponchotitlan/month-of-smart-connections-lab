# 🚀 Quick Start Guide - For Ansible Beginners

This is a step-by-step guide to get you started with this project, even if you've never used Ansible before.

## What You'll Do

1. Install Ansible and pygnmi
2. Configure your device details
3. Get interface information from your device
4. Configure interfaces on your device

## Step-by-Step Instructions

### Step 1: Install Python Dependencies

Open your terminal and run:

```bash
pip install -r requirements.txt
```

This installs:
- Ansible (automation framework)
- pygnmi (gNMI Python client library)
- grpcio and protobuf (required by pygnmi)

Wait for it to complete. You should see success messages.

### Step 2: Verify Installation

Check that everything is installed:

```bash
python -c "import pygnmi; print('pygnmi version:', pygnmi.__version__)"
ansible --version
```

You should see version information for both.

### Step 3: Configure Your Device

1. Open `inventory.yml`
2. Replace the device details with your device's information:
   - `ansible_host`: Your device IP or hostname
   - `ansible_port`: Your device's gNMI port (often 57400 or 57777)
3. Save the file

Example:
```yaml
devnet-sandbox-router-1:
  ansible_host: 10.20.30.40      # ← Your device IP here
  ansible_port: 57777             # ← Your gNMI port here
```

### Step 4: Set Credentials

1. Open `group_vars/all.yml`
2. Update username and password:

```yaml
ansible_user: your_username      # ← Your username
ansible_password: your_password  # ← Your password
```

3. Save the file

### Step 5: Get Interfaces (Read from Device)

Run this command:

```bash
ansible-playbook get_interfaces.yml
```

**What happens:**
- Connects to your device
- Retrieves all interface information
- Saves it to `output/router1_interfaces.json`
- Shows the data on screen

### Step 6: Configure Interfaces (Write to Device)

First, define what you want to configure:

1. Open `host_vars/router1.yml` (or the file for your device)
2. Edit the interface names and settings for YOUR device:

```yaml
interfaces:
  - name: GigabitEthernet0/0/0/1    # ← Use YOUR interface name
    description: "My Test Interface"
    enabled: true
    mtu: 1500
    ipv4_address: 192.168.10.1      # ← Your desired IP
    ipv4_prefix_length: 24
```

**For loopback interfaces**, you can add them without MTU (it's auto-excluded):
```yaml
interfaces:
  - name: Loopback23
    description: "My Test Loopback"
    enabled: true
    ipv4_address: 192.0.2.31
    ipv4_prefix_length: 32
    # No MTU needed - automatically handled!
```

3. Save the file

4. Run the configuration command:

```bash
ansible-playbook configure_interfaces.yml
```

**What happens:**
- Connects to your device
- Applies the configuration you defined
- Shows success or error messages

## Understanding the Output

### Success looks like:
```
TASK [Configure each interface] **********************
ok: [router1] => (item=GigabitEthernet0/0/0/1)

PLAY RECAP *******************************************
router1: ok=3    changed=1    unreachable=0    failed=0
```

- `ok`: Number of successful tasks
- `changed`: Configuration was applied
- `failed=0`: No errors!

### Error looks like:
```
fatal: [router1]: FAILED!
```

Check the error message below it for details.

## Common Issues & Solutions

### "pygnmi module not found" error
**Solution**: Install pygnmi:
```bash
pip install pygnmi
```

### "Module gnmi_get not found" error
**Solution**: 
- Make sure you're running the playbook from the 02-ansible folder
- The custom modules are in the `library/` folder

### "Connection refused" error
**Solution**: 
- Check device IP in `inventory.yml`
- Verify gNMI is enabled on device
- Check gNMI port number

### "Authentication failed" error
**Solution**: 
- Verify username/password in `group_vars/all.yml`
- Check user permissions on device

### "Host not found" error
**Solution**:
- Check the limit matches inventory name
- Use `--limit router1` (must match inventory.yml)

## Useful Commands

### Run on specific device only:
```bash
ansible-playbook get_interfaces.yml --limit router1
```

### See what would change (without applying):
```bash
ansible-playbook configure_interfaces.yml --check
```

### See detailed output:
```bash
ansible-playbook get_interfaces.yml -v
# or even more detail:
ansible-playbook get_interfaces.yml -vvv
```

### List all devices in inventory:
```bash
ansible-inventory --list
```

## Next Steps

Once comfortable with the basics:

1. **Add more devices**: Copy the router1 section in `inventory.yml` and create matching `host_vars` files
2. **Organize by groups**: Group devices by role (core, distribution, access)
3. **Use tags**: Add tags to tasks to run only specific parts
4. **Encrypt secrets**: Use `ansible-vault` to encrypt `group_vars/all.yml`

## Getting Help

- Read the full [README.md](README.md) for more details
- Check [Ansible documentation](https://docs.ansible.com/)
- Look at the playbook comments for explanations

## Terminology Quick Reference
gnmic**: CLI tool that performs gNMI operations
- **gNMI**: Protocol for network management
- **Playbook**: A file containing automation tasks (like a recipe)
- **Inventory**: List of devices to manage
- **Host**: A device in your inventory
- **Task**: A single action (like "get interfaces")
- **Module**: Code that performs an action (like `gnmi_get`)
- **Variable**: A value that can change (like device IP)
- **Host vars**: Variables specific to one device
- **Group vars**: Variables shared by multiple devices

---

**Remember**: Start simple! Get interfaces first, then try configuration.
