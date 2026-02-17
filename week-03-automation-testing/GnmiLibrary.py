"""
Simple gNMI Library for Robot Framework
Provides keywords for connecting to network devices and retrieving interface information
"""

import json
import yaml
from pygnmi.client import gNMIclient
from robot.api import logger


class GnmiLibrary:
    """Robot Framework library for gNMI operations using pygnmi"""
    
    ROBOT_LIBRARY_SCOPE = 'SUITE'
    
    def __init__(self):
        self.devices_config = {}
        self.devices = {}
    
    def load_devices(self, devices_file):
        """
        Load device configurations from YAML file
        
        Args:
            devices_file: Path to devices.yaml file
        """
        logger.info(f"Loading devices from {devices_file}")
        with open(devices_file, 'r') as f:
            self.devices_config = yaml.safe_load(f)
        
        device_count = len(self.devices_config.get('devices', {}))
        logger.info(f"Devices loaded successfully: {device_count} devices")
        return True
    
    def get_all_device_names(self):
        """
        Get list of all device names from loaded configuration
        
        Returns:
            List of device names
        """
        if not self.devices_config:
            raise Exception("Devices not loaded. Call 'Load Devices' first.")
        
        device_names = list(self.devices_config.get('devices', {}).keys())
        logger.info(f"Device names: {device_names}")
        return device_names
    
    def connect_to_device(self, device_name):
        """
        Connect to a network device using gNMI
        
        Args:
            device_name: Name of the device in configuration
        """
        if not self.devices_config:
            raise Exception("Devices not loaded. Call 'Load Devices' first.")
        
        devices = self.devices_config.get('devices', {})
        if device_name not in devices:
            raise Exception(f"Device {device_name} not found in configuration")
        
        device_cfg = devices[device_name]
        logger.info(f"Connecting to device: {device_name}")
        
        try:
            connection = gNMIclient(
                target=(device_cfg['host'], device_cfg['port']),
                username=device_cfg['username'],
                password=device_cfg['password'],
                insecure=device_cfg.get('insecure', True),
                skip_verify=device_cfg.get('skip_verify', True)
            )
            connection.connect()
            self.devices[device_name] = connection
            logger.info(f"Successfully connected to {device_name}")
            return True
        except Exception as e:
            raise Exception(f"Failed to connect to {device_name}: {str(e)}")
    
    def connect_to_device_inline(self, device_name, host, port, username, password, insecure=True):
        """
        Connect to a network device using gNMI with inline parameters
        
        Args:
            device_name: Name/identifier for the device
            host: Device IP address or hostname
            port: gNMI port number
            username: Authentication username
            password: Authentication password
            insecure: Skip TLS verification (default: True)
        """
        logger.info(f"Connecting to device: {device_name} at {host}:{port}")
        
        try:
            # Convert port to integer
            port = int(port)
            
            connection = gNMIclient(
                target=(host, port),
                username=username,
                password=password,
                insecure=insecure,
                skip_verify=insecure
            )
            connection.connect()
            self.devices[device_name] = connection
            logger.info(f"Successfully connected to {device_name}")
            return True
        except Exception as e:
            raise Exception(f"Failed to connect to {device_name}: {str(e)}")
    
    def get_config_via_gnmi(self, device_name, path):
        """
        Retrieve configuration from device using gNMI with custom path
        
        Args:
            device_name: Name of the device
            path: gNMI path to query (e.g., '/interfaces' or '/network-instances')
            
        Returns:
            JSON string with configuration
        """
        if device_name not in self.devices:
            raise Exception(f"Device {device_name} not connected. Call 'Connect To Device' first.")
        
        connection = self.devices[device_name]
        logger.info(f"Retrieving config from {device_name} at path: {path}")
        
        try:
            response = connection.get(path=[path], encoding='json_ietf')
            
            # Parse response
            config_data = {}
            if response and 'notification' in response:
                for notification in response['notification']:
                    if 'update' in notification:
                        for update in notification['update']:
                            if 'val' in update:
                                config_data = update['val']
            
            logger.info(f"Retrieved config from {device_name}: {json.dumps(config_data, indent=2)}")
            return json.dumps(config_data)
        except Exception as e:
            raise Exception(f"Failed to get config from {device_name} at {path}: {str(e)}")
    
    def get_interfaces_via_gnmi(self, device_name):
        """
        Retrieve interface configuration from device using gNMI and OpenConfig
        
        Args:
            device_name: Name of the device
            
        Returns:
            JSON string with interface configuration
        """
        if device_name not in self.devices:
            raise Exception(f"Device {device_name} not connected. Call 'Connect To Device' first.")
        
        connection = self.devices[device_name]
        logger.info(f"Retrieving interface configuration from {device_name}")
        
        try:
            path = '/interfaces'
            response = connection.get(path=[path], encoding='json_ietf')
            
            # Parse response
            interfaces_data = {}
            if response and 'notification' in response:
                for notification in response['notification']:
                    if 'update' in notification:
                        for update in notification['update']:
                            if 'val' in update:
                                interfaces_data = update['val']
                                if interfaces_data:
                                    logger.info(f"✓ Successfully retrieved interfaces from {device_name}")
                                    logger.info(f"Response data: {json.dumps(interfaces_data, indent=2)[:500]}...")
                                    return json.dumps(interfaces_data)
            
            raise Exception(f"No interface data received from {device_name}")
        except Exception as e:
            error_msg = f"Failed to get interfaces from {device_name}: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def parse_interfaces_from_json(self, json_string):
        """
        Extract interface details from JSON response
        
        Args:
            json_string: JSON string containing interface data
            
        Returns:
            List of dictionaries with interface name, description, and status
        """
        try:
            data = json.loads(json_string)
            interfaces = []
            
            # OpenConfig interfaces structure
            interface_list = data.get('openconfig-interfaces:interface', data.get('interface', []))
            
            for intf in interface_list:
                # Get interface name
                name = intf.get('name', 'Unknown')
                
                # Get config and state
                config = intf.get('config', {})
                state = intf.get('state', {})
                
                # Get description
                description = config.get('description', state.get('description', ''))
                
                # Get admin and operational status
                admin_status = config.get('enabled', state.get('enabled', None))
                oper_status = state.get('oper-status', 'UNKNOWN')
                
                interface_info = {
                    'name': name,
                    'description': description,
                    'admin_status': 'UP' if admin_status else 'DOWN',
                    'oper_status': oper_status
                }
                
                interfaces.append(interface_info)
                logger.info(f"Parsed interface: {name} - {description} - Admin: {interface_info['admin_status']}, Oper: {oper_status}")
            
            logger.info(f"Total interfaces parsed: {len(interfaces)}")
            return interfaces
        except Exception as e:
            logger.error(f"Failed to parse interfaces: {str(e)}")
            logger.error(f"JSON data was: {json_string[:500]}...")  # Log first 500 chars
            raise Exception(f"Failed to parse interfaces: {str(e)}")
    
    def load_expected_interfaces(self, expected_file, device_name):
        """
        Load expected interfaces for a device from JSON file
        
        Args:
            expected_file: Path to expected_interfaces.json file
            device_name: Name of the device
            
        Returns:
            List of expected interface dictionaries
        """
        try:
            with open(expected_file, 'r') as f:
                expected_data = json.load(f)
            
            if device_name not in expected_data:
                raise Exception(f"Device {device_name} not found in expected interfaces file")
            
            expected_interfaces = expected_data[device_name]
            logger.info(f"Expected interfaces for {device_name}: {len(expected_interfaces)} interfaces")
            return expected_interfaces
        except Exception as e:
            raise Exception(f"Failed to load expected interfaces: {str(e)}")
    
    def verify_interface_exists(self, interface_name, actual_interfaces):
        """
        Verify if an interface exists in the actual interfaces list
        
        Args:
            interface_name: Name of the interface to find
            actual_interfaces: List of actual interface dictionaries
            
        Returns:
            Dictionary with interface details if found, None otherwise
        """
        for intf in actual_interfaces:
            if intf['name'] == interface_name:
                return intf
        return None
    
    def disconnect_from_device(self, device_name):
        """
        Disconnect from a network device
        
        Args:
            device_name: Name of the device
        """
        if device_name in self.devices:
            try:
                self.devices[device_name].close()
                logger.info(f"Disconnected from {device_name}")
                del self.devices[device_name]
            except Exception as e:
                logger.warn(f"Error disconnecting from {device_name}: {str(e)}")
    
    def disconnect_all(self):
        """Disconnect from all devices"""
        for device_name in list(self.devices.keys()):
            self.disconnect_from_device(device_name)
