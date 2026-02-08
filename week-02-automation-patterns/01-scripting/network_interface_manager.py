#!/usr/bin/env python3
"""
Month of Smart Connections
Episode 2: Choose your Love language
Network Interface Manager - A gNMI/OpenConfig-based script for managing network interfaces.
"""

import argparse
import sys
import json
from pygnmi.client import gNMIclient


def create_device_connection(host, username, password, port=57400):
    """
    Create a gNMI connection to the network device.
    
    Args:
        host: Device IP address or hostname
        username: gNMI username
        password: gNMI password
        port: gNMI port (default: 57400)
    
    Returns:
        gNMIclient object or None if connection fails
    """
    try:
        connection = gNMIclient(
            target=(host, port),
            username=username,
            password=password,
            insecure=True
        )
        connection.connect()
        return connection
    except Exception as e:
        print(f"❌ ERROR: Failed to connect to {host}: {str(e)}")
        return None


def retrieve_interfaces(connection):
    """
    Retrieve and display interface information using OpenConfig models.
    
    Args:
        connection: Active gNMIclient object
    """
    print("\n" + "="*60)
    print("📋 RETRIEVING INTERFACE INFORMATION")
    print("="*60 + "\n")
    
    # OpenConfig interfaces path
    path = ["openconfig-interfaces:interfaces/interface"]
    
    print("📤 gNMI Get Request:")
    print("-" * 60)
    print(json.dumps({"path": path}, indent=2))
    print("-" * 60 + "\n")
    
    try:
        # Send gNMI Get request
        response = connection.get(path=path, encoding='json_ietf')
        
        print("📥 gNMI Get Reply:")
        print("-" * 60)
        print(json.dumps(response, indent=2))
        print("-" * 60 + "\n")
        
        # Parse and display the response
        if response and 'notification' in response:
            print(f"{'Interface':<30} {'IP Address':<20} {'Status':<12} {'Description'}")
            print("═" * 100)
            
            interface_count = 0
            for notification in response['notification']:
                if 'update' in notification:
                    for update in notification['update']:
                        if 'val' in update:
                            # Each update contains one interface directly in val
                            interface = update['val']
                            
                            # Get interface name
                            name = interface.get('name', 'N/A')
                            
                            # Get state information (gNMI uses 'state' for operational data)
                            state = interface.get('state', {})
                            config = interface.get('config', {})
                            
                            # Try state first, then config for description and enabled
                            description = state.get('description', '') or config.get('description', '')
                            enabled = state.get('enabled', config.get('enabled', False))
                            status = '✓ up' if enabled else '✗ down'
                            
                            # Get IP address information from subinterfaces
                            ip_text = 'N/A'
                            subinterfaces = interface.get('subinterfaces', {}).get('subinterface', [])
                            for subif in subinterfaces:
                                ipv4 = subif.get('openconfig-if-ip:ipv4', {}) or subif.get('ipv4', {})
                                addresses = ipv4.get('addresses', {}).get('address', [])
                                if addresses:
                                    addr = addresses[0]
                                    ip = addr.get('ip', '')
                                    # Try state first, then config for IP details
                                    addr_state = addr.get('state', {})
                                    addr_config = addr.get('config', {})
                                    prefix_len = addr_state.get('prefix-length', '') or addr_config.get('prefix-length', '')
                                    if ip and prefix_len:
                                        ip_text = f"{ip}/{prefix_len}"
                                    break
                            
                            print(f"{name:<30} {ip_text:<20} {status:<12} {description}")
                            interface_count += 1
            
            print("─" * 100)
            print(f"\n📊 Total interfaces: {interface_count}\n")
            
            if interface_count == 0:
                print("ℹ️  No interfaces found.")
        else:
            print("ℹ️  No interfaces found.")
            
    except Exception as e:
        print(f"❌ Error retrieving interfaces: {e}")


def configure_interface(connection, interface_name, ip_address, prefix_length, description=''):
    """
    Configure an interface using OpenConfig models.
    
    Args:
        connection: Active gNMIclient object
        interface_name: Interface name (e.g., 'GigabitEthernet0/0/0/0')
        ip_address: IP address to assign
        prefix_length: Prefix length (e.g., 24 for /24)
        description: Optional interface description
    """
    print("\n" + "="*60)
    print("⚙️  CONFIGURING INTERFACE")
    print("="*60 + "\n")
    
    # Detect interface type based on name
    interface_name_lower = interface_name.lower()
    if 'loopback' in interface_name_lower:
        if_type = 'iana-if-type:softwareLoopback'
    elif 'tunnel' in interface_name_lower:
        if_type = 'iana-if-type:tunnel'
    elif any(x in interface_name_lower for x in ['gigabit', 'ethernet', 'eth', 'ge', 'te', 'fortygige', 'hundredgige']):
        if_type = 'iana-if-type:ethernetCsmacd'
    elif 'vlan' in interface_name_lower:
        if_type = 'iana-if-type:l3ipvlan'
    elif 'bundle' in interface_name_lower or 'port-channel' in interface_name_lower:
        if_type = 'iana-if-type:ieee8023adLag'
    else:
        if_type = 'iana-if-type:other'
    
    print(f"🔍 Detected interface type: {if_type}\n")
    
    # Build OpenConfig configuration in JSON format
    config_data = {
        "openconfig-interfaces:interface": [
            {
                "name": interface_name,
                "config": {
                    "name": interface_name,
                    "type": if_type,
                    "description": description,
                    "enabled": True
                },
                "subinterfaces": {
                    "subinterface": [
                        {
                            "index": 0,
                            "openconfig-if-ip:ipv4": {
                                "addresses": {
                                    "address": [
                                        {
                                            "ip": ip_address,
                                            "config": {
                                                "ip": ip_address,
                                                "prefix-length": int(prefix_length)
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
    
    print(f"🔧 Applying OpenConfig configuration:")
    print(f"  Interface: {interface_name}")
    print(f"  IP Address: {ip_address}/{prefix_length}")
    if description:
        print(f"  Description: {description}")
    print(f"  Status: enabled\n")
    
    # Build update list for gNMI Set request
    update = [
        (
            "openconfig-interfaces:interfaces/interface",
            config_data['openconfig-interfaces:interface'][0]
        )
    ]
    
    print("📤 gNMI Set Request:")
    print("-" * 60)
    print(json.dumps(config_data, indent=2))
    print("-" * 60 + "\n")
    
    try:
        # Send gNMI Set request
        response = connection.set(update=update, encoding='json_ietf')
        
        print("📥 gNMI Set Reply:")
        print("-" * 60)
        print(json.dumps(response, indent=2))
        print("-" * 60 + "\n")
        
        if response:
            print("✅ Configuration applied successfully.")
        else:
            print("❌ Failed to apply configuration.")
            
    except Exception as e:
        print(f"❌ Error configuring interface: {e}")


def display_menu():
    """Display the main menu."""
    print("\n" + "="*60)
    print("🌐 OPENCONFIG gNMI INTERFACE MANAGER")
    print("="*60)
    print("1. 📋 Retrieve Interface Information")
    print("2. ⚙️  Configure Interface")
    print("3. 🚪 Exit")
    print("="*60)


def main():
    """Main function to handle menu and user interaction."""
    parser = argparse.ArgumentParser(
        description='Network Interface Manager - Manage network device interfaces',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --host 192.168.1.1 --username admin --password secret
  %(prog)s -H 10.0.0.1 -u admin -p pass123 -P 830
        """
    )
    
    parser.add_argument('-H', '--host', required=True,
                        help='Device IP address or hostname')
    parser.add_argument('-u', '--username', required=True,
                        help='gNMI username')
    parser.add_argument('-p', '--password', required=True,
                        help='gNMI password')
    parser.add_argument('-P', '--port', type=int, default=57400,
                        help='gNMI port (default: 57400)')
    
    args = parser.parse_args()
    
    # Connect to device
    print(f"\n🔌 Connecting to {args.host}...")
    connection = create_device_connection(
        args.host,
        args.username,
        args.password,
        args.port
    )
    
    if not connection:
        sys.exit(1)
    
    print(f"✅ Successfully connected to {args.host}\n")
    
    # Main menu loop
    try:
        while True:
            display_menu()
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == '1':
                retrieve_interfaces(connection)
                
            elif choice == '2':
                print("\n" + "-"*60)
                interface_name = input("Enter interface name (e.g., GigabitEthernet0/0/0/0): ").strip()
                ip_address = input("Enter IP address: ").strip()
                prefix_length = input("Enter prefix length (e.g., 24): ").strip()
                description = input("Enter description (optional): ").strip()
                print("-"*60)
                
                configure_interface(
                    connection,
                    interface_name,
                    ip_address,
                    prefix_length,
                    description
                )
                
            elif choice == '3':
                print("\n👋 Exiting... Goodbye!")
                break
                
            else:
                print("\n⚠️  Invalid choice. Please select 1, 2, or 3.")
            
            input("\nPress Enter to continue...")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user.")
    
    finally:
        # Disconnect from device
        if connection:
            connection.close()
            print(f"🔌 Disconnected from {args.host}")


if __name__ == '__main__':
    main()
