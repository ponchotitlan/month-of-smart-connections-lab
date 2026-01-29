#!/usr/bin/env python3
"""
Cisco NSO RESTCONF Multi-Vendor Interface Query Tool
=====================================================
Query network devices through Cisco NSO via RESTCONF API
and display results in beautiful ASCII tables.
"""

import argparse
import json
import sys
from typing import Dict, List, Optional, Any

import requests
import urllib3
from requests.auth import HTTPBasicAuth
from tabulate import tabulate


# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ============================================================================
# CONFIGURATION
# ============================================================================

RESTCONF_URLS = {
    'test_connectivity': '/restconf/data/ietf-yang-library:yang-library',
    'get_devices': '/restconf/data/tailf-ncs:devices/device?fields=name',
    'get_platform': '/restconf/data/tailf-ncs:devices/device={device}/device-type/{connection_type}/ned-id',
    'get_interfaces_asa': '/restconf/data/tailf-ncs:devices/device={device}/config/tailf-ned-cisco-asa:interface',
    'get_interfaces_iosxr': '/restconf/data/tailf-ncs:devices/device={device}/config/tailf-ned-cisco-ios-xr:interface',
    'get_interfaces_juniper': '/restconf/data/tailf-ncs:devices/device={device}/config/junos:configuration/interfaces/interface',
    'get_interfaces_fortinet': '/restconf/data/tailf-ncs:devices/device={device}/config/tailf-ned-fortinet-fortios:global/system/interface'
}

VENDOR_ICONS = {
    'cisco': '🔷',
    'juniper': '🟢',
    'fortinet': '🔴',
    'default': '🖥️'
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_header(title: str) -> None:
    """Print a formatted section header."""
    width = 80
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width)


def print_banner() -> None:
    """Print the application banner."""
    banner = """
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║        🌐  Cisco NSO RESTCONF Multi-Vendor Interface Query Tool  🌐       ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def get_vendor_icon(platform: str) -> str:
    """Get emoji icon for vendor based on platform name."""
    platform_lower = platform.lower()
    
    if 'cisco' in platform_lower or 'asa' in platform_lower or 'iosxr' in platform_lower:
        return VENDOR_ICONS['cisco']
    elif 'juniper' in platform_lower or 'junos' in platform_lower:
        return VENDOR_ICONS['juniper']
    elif 'fortinet' in platform_lower or 'fortios' in platform_lower:
        return VENDOR_ICONS['fortinet']
    else:
        return VENDOR_ICONS['default']


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Query Cisco NSO via RESTCONF API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --url nso.example.com --port 443 --username admin --password secret
  %(prog)s --url 192.168.1.100
        """
    )
    
    parser.add_argument(
        '--url',
        default='localhost',
        help='NSO server URL (default: localhost)'
    )
    parser.add_argument(
        '--port',
        default='8080',
        help='NSO RESTCONF port (default: 8080)'
    )
    parser.add_argument(
        '--username',
        default='admin',
        help='Username (default: admin)'
    )
    parser.add_argument(
        '--password',
        default='admin',
        help='Password (default: admin)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    return parser.parse_args()


# ============================================================================
# API FUNCTIONS
# ============================================================================

def test_connectivity(base_url: str, auth: HTTPBasicAuth) -> bool:
    """Test RESTCONF connectivity to NSO."""
    url = f"{base_url}{RESTCONF_URLS['test_connectivity']}"
    
    try:
        response = requests.get(
            url,
            auth=auth,
            verify=False,
            headers={'Accept': 'application/yang-data+json'},
            timeout=10
        )
        response.raise_for_status()
        print("✅ RESTCONF connectivity successful")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ RESTCONF connectivity failed: {e}")
        return False


def get_devices(base_url: str, auth: HTTPBasicAuth) -> Optional[List[str]]:
    """Get all devices from NSO."""
    url = f"{base_url}{RESTCONF_URLS['get_devices']}"
    
    try:
        response = requests.get(
            url,
            auth=auth,
            verify=False,
            headers={'Accept': 'application/yang-data+json'},
            timeout=10
        )
        response.raise_for_status()
        devices = response.json()
        device_list = [device['name'] for device in devices.get('tailf-ncs:device', [])]
        
        print(f"📋 Found {len(device_list)} device(s)")
        return device_list
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting devices: {e}")
        return None


def get_platform(base_url: str, auth: HTTPBasicAuth, device: str, connection_type: str) -> str:
    """Get platform version for a specific device from NSO."""
    url = f"{base_url}{RESTCONF_URLS['get_platform'].format(device=device, connection_type=connection_type)}"
    
    try:
        response = requests.get(
            url,
            auth=auth,
            verify=False,
            headers={'Accept': 'application/yang-data+json'},
            timeout=10
        )
        response.raise_for_status()
        return response.json()['tailf-ncs:ned-id']
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error getting platform for device {device} via {connection_type}: {e}")


def get_interfaces(base_url: str, auth: HTTPBasicAuth, device: str, platform: str) -> Optional[Dict]:
    """Get interfaces for a specific device from NSO."""
    platform_lower = platform.lower()
    
    # Determine the correct URL based on platform
    if 'asa' in platform_lower:
        url = f"{base_url}{RESTCONF_URLS['get_interfaces_asa'].format(device=device)}"
    elif 'iosxr' in platform_lower or 'ios-xr' in platform_lower:
        url = f"{base_url}{RESTCONF_URLS['get_interfaces_iosxr'].format(device=device)}"
    elif 'juniper' in platform_lower or 'junos' in platform_lower:
        url = f"{base_url}{RESTCONF_URLS['get_interfaces_juniper'].format(device=device)}"
    elif 'fortinet' in platform_lower or 'fortios' in platform_lower:
        url = f"{base_url}{RESTCONF_URLS['get_interfaces_fortinet'].format(device=device)}"
    else:
        raise ValueError(f"⚠️  Unsupported device type: {platform}")
    
    try:
        response = requests.get(
            url,
            auth=auth,
            verify=False,
            headers={'Accept': 'application/yang-data+json'},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting interfaces for device {device}: {e}")
        return None


# ============================================================================
# DATA PROCESSING FUNCTIONS
# ============================================================================

def parse_interfaces(interface_data: Dict, platform: str, device: str) -> List[Dict[str, str]]:
    """Parse interface data into a standardized format with IP address extraction."""
    interfaces = []
    platform_lower = platform.lower()
    
    try:
        if 'asa' in platform_lower:
            # Parse Cisco ASA interfaces
            for int_type, int_list in interface_data.get('tailf-ned-cisco-asa:interface', {}).items():
                if isinstance(int_list, list):
                    for interface in int_list:
                        # Extract IP address for ASA
                        ip_address = ''
                        if 'ip' in interface and 'address' in interface['ip']:
                            addr_data = interface['ip']['address']
                            if 'ip' in addr_data and 'host-ip' in addr_data['ip']:
                                host_ip = addr_data['ip']['host-ip']
                                # Check for subnet mask
                                if 'mask' in addr_data.get('ip', {}):
                                    mask = addr_data['ip']['mask']
                                    ip_address = f"{host_ip} {mask}"
                                else:
                                    ip_address = host_ip
                        
                        # Build interface name
                        interface_name = interface.get('name', interface.get('id', 'N/A'))
                        if interface_name != 'N/A' and int_type:
                            full_name = f"{int_type}{interface_name}"
                        else:
                            full_name = interface_name
                        
                        interfaces.append({
                            'name': full_name,
                            'type': int_type,
                            'ip_address': ip_address,
                            'status': 'Configured',
                            'description': interface.get('description', '')
                        })
                        
        elif 'iosxr' in platform_lower or 'ios-xr' in platform_lower:
            # Parse Cisco IOS-XR interfaces
            for int_type, int_list in interface_data.get('tailf-ned-cisco-ios-xr:interface', {}).items():
                if isinstance(int_list, list):
                    for interface in int_list:
                        # Extract IP address for IOS-XR
                        ip_address = ''
                        if 'ipv4' in interface and 'address' in interface['ipv4']:
                            addr_data = interface['ipv4']['address']
                            ip = addr_data.get('ip', '')
                            mask = addr_data.get('mask', '')
                            if ip:
                                ip_address = f"{ip} {mask}" if mask else ip
                        
                        # Build interface name
                        interface_id = interface.get('id', 'N/A')
                        if interface_id != 'N/A' and int_type:
                            full_name = f"{int_type}{interface_id}"
                        else:
                            full_name = interface_id
                        
                        interfaces.append({
                            'name': full_name,
                            'type': int_type,
                            'ip_address': ip_address,
                            'status': 'Configured',
                            'description': interface.get('description', '')
                        })
                        
        elif 'juniper' in platform_lower or 'junos' in platform_lower:
            # Parse Juniper interfaces
            for interface in interface_data.get('junos:interface', []):
                # Extract IP addresses from units
                ip_addresses = []
                if 'unit' in interface:
                    for unit in interface['unit']:
                        if 'family' in unit and 'inet' in unit['family']:
                            inet_family = unit['family']['inet']
                            if 'address' in inet_family:
                                for addr in inet_family['address']:
                                    if 'name' in addr:
                                        ip_addresses.append(addr['name'])
                
                ip_address = ', '.join(ip_addresses) if ip_addresses else ''
                
                interfaces.append({
                    'name': interface.get('name', 'N/A'),
                    'type': 'Physical',
                    'ip_address': ip_address,
                    'status': 'Configured',
                    'description': interface.get('description', '')
                })
                
        elif 'fortinet' in platform_lower or 'fortios' in platform_lower:
            # Parse Fortinet interfaces
            fortinet_data = interface_data.get('tailf-ned-fortinet-fortios:interface', {})
            
            # Handle nested interface-list structure
            if isinstance(fortinet_data, dict) and 'interface-list' in fortinet_data:
                interface_list = fortinet_data['interface-list']
            elif isinstance(fortinet_data, list):
                interface_list = fortinet_data
            else:
                interface_list = []
            
            for interface in interface_list:
                # Extract IP address for Fortinet
                ip_address = ''
                if 'ip' in interface and 'ip-mask' in interface['ip']:
                    ip_mask = interface['ip']['ip-mask']
                    class_ip = ip_mask.get('class_ip', '')
                    net_mask = ip_mask.get('net_mask', '')
                    if class_ip and net_mask:
                        ip_address = f"{class_ip} {net_mask}"
                    elif class_ip:
                        ip_address = class_ip
                
                # Extract access information for description
                access_info = ''
                if 'allowaccess' in interface:
                    access_list = interface['allowaccess']
                    if isinstance(access_list, list):
                        access_info = ', '.join(access_list)
                    else:
                        access_info = str(access_list)
                
                # Build description from available info
                description_parts = []
                if access_info:
                    description_parts.append(f"Access: {access_info}")
                if 'vdom' in interface:
                    description_parts.append(f"VDOM: {interface['vdom']}")
                if interface.get('description'):
                    description_parts.append(interface['description'])
                
                description = ' | '.join(description_parts) if description_parts else ''
                
                interfaces.append({
                    'name': interface.get('name', 'N/A'),
                    'type': interface.get('type', 'N/A'),
                    'ip_address': ip_address,
                    'status': interface.get('status', 'unknown'),
                    'description': description
                })
                
    except Exception as e:
        print(f"⚠️  Warning: Error parsing interfaces for {device}: {e}")
    
    return interfaces


def display_device_summary(devices_info: List[Dict[str, Any]]) -> None:
    """Display a summary table of all devices."""
    print_header("📊 DEVICE SUMMARY")
    
    table_data = []
    for device_info in devices_info:
        icon = get_vendor_icon(device_info['platform'])
        table_data.append([
            f"{icon} {device_info['name']}",
            device_info['platform'],
            device_info['interface_count'],
            device_info['status']
        ])
    
    headers = ['Device', 'Platform', 'Interfaces', 'Status']
    print(tabulate(table_data, headers=headers, tablefmt='fancy_grid'))


def display_device_interfaces(device: str, platform: str, interfaces: List[Dict[str, str]]) -> None:
    """Display interfaces for a specific device in an ASCII table."""
    icon = get_vendor_icon(platform)
    print_header(f"{icon} {device} - {platform}")
    
    if not interfaces:
        print("⚠️  No interfaces found or unable to retrieve interface data.\n")
        return
    
    # Prepare table data
    table_data = []
    for idx, interface in enumerate(interfaces, 1):
        # Truncate long descriptions and IP addresses intelligently
        description = interface.get('description', '')
        max_desc_length = 40
        if len(description) > max_desc_length:
            description = description[:max_desc_length-3] + '...'
        
        ip_address = interface.get('ip_address', '')
        max_ip_length = 30
        if len(ip_address) > max_ip_length:
            ip_address = ip_address[:max_ip_length-3] + '...'
        
        table_data.append([
            idx,
            interface.get('name', 'N/A'),
            interface.get('type', 'N/A'),
            ip_address if ip_address else '-',
            interface.get('status', 'N/A'),
            description
        ])
    
    headers = ['#', 'Interface Name', 'Type', 'IP Address', 'Status', 'Description']
    print(tabulate(table_data, headers=headers, tablefmt='fancy_grid'))
    print(f"\n💡 Total interfaces: {len(interfaces)}\n")


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main() -> int:
    """Main execution function."""
    args = parse_arguments()
    
    # Print banner
    print_banner()
    
    # Build base URL
    base_url = f"http://{args.url}:{args.port}"
    auth = HTTPBasicAuth(args.username, args.password)
    
    print(f"🔗 Connecting to NSO at {base_url}")
    print(f"👤 Username: {args.username}")
    
    # Test connectivity
    print_header("🔌 CONNECTIVITY TEST")
    if not test_connectivity(base_url, auth):
        print("\n❌ Failed to connect to NSO. Please check your credentials and URL.\n")
        return 1
    
    # Get devices
    print_header("📡 RETRIEVING DEVICES")
    device_list = get_devices(base_url, auth)
    
    if not device_list:
        print("\n⚠️  No devices found or unable to retrieve device list.\n")
        return 1
    
    # Process each device
    devices_info = []
    
    for device_name in device_list:
        print(f"\n🔍 Processing device: {device_name}")
        
        # Get platform type
        platform = None
        for connection_type in ['cli', 'netconf']:
            try:
                platform = get_platform(base_url, auth, device_name, connection_type)
                print(f"   ✓ Platform detected: {platform} (via {connection_type})")
                break
            except Exception:
                continue
        
        if not platform:
            print(f"   ⚠️  Unable to determine platform for {device_name}")
            devices_info.append({
                'name': device_name,
                'platform': 'Unknown',
                'interface_count': 0,
                'status': '❌ Failed',
                'interfaces': []
            })
            continue
        
        # Get interfaces
        try:
            interface_data = get_interfaces(base_url, auth, device_name, platform)
            
            if interface_data:
                interfaces = parse_interfaces(interface_data, platform, device_name)
                print(f"   ✓ Retrieved {len(interfaces)} interface(s)")
                
                devices_info.append({
                    'name': device_name,
                    'platform': platform,
                    'interface_count': len(interfaces),
                    'status': '✅ Success',
                    'interfaces': interfaces
                })
            else:
                devices_info.append({
                    'name': device_name,
                    'platform': platform,
                    'interface_count': 0,
                    'status': '⚠️  No Data',
                    'interfaces': []
                })
                
        except ValueError as ve:
            print(f"   ⚠️  {ve}")
            devices_info.append({
                'name': device_name,
                'platform': platform,
                'interface_count': 0,
                'status': '⚠️  Unsupported',
                'interfaces': []
            })
    
    # Display results
    print("\n")
    display_device_summary(devices_info)
    
    print_header("🔍 DETAILED INTERFACE INFORMATION")
    for device_info in devices_info:
        if device_info['interfaces']:
            display_device_interfaces(
                device_info['name'],
                device_info['platform'],
                device_info['interfaces']
            )
    
    # Final summary
    print_header("✨ QUERY COMPLETE")
    total_interfaces = sum(d['interface_count'] for d in devices_info)
    successful_devices = sum(1 for d in devices_info if '✅' in d['status'])
    
    print(f"""
    📊 Summary Statistics:
       • Total Devices Queried: {len(devices_info)}
       • Successful Queries: {successful_devices}
       • Total Interfaces Found: {total_interfaces}
    
    🎉 Query completed successfully!
    """)
    
    return 0


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user.\n")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        sys.exit(1)