#!/usr/bin/env python3
"""
NSO RESTCONF Configuration Pusher
Applies XML configuration files to NSO devices via RESTCONF API
"""

import argparse
import sys
from pathlib import Path
import requests
from typing import Optional


class ConfigPusher:
    """Handles NSO RESTCONF configuration operations"""
    
    def __init__(self, nso_url: str, username: str, password: str):
        self.nso_url = nso_url
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.auth = (username, password)
    
    def push_config(self, device_name: str, xml_payload: str) -> bool:
        """
        Push XML configuration to NSO device
        
        Args:
            device_name: Target device name in NSO
            xml_payload: XML configuration payload
            
        Returns:
            True if successful, False otherwise
        """
        url = f"{self.nso_url}/restconf/data/tailf-ncs:devices/device={device_name}/config"
        headers = {
            "Content-Type": "application/yang-data+xml",
            "Accept": "application/yang-data+json"
        }
        
        print(f"🚀 Pushing configuration to device: {device_name}")
        print(f"🔗 URL: {url}")
        print("📡 Sending PATCH request...\n")
        
        try:
            response = self.session.patch(
                url,
                headers=headers,
                data=xml_payload,
                timeout=30
            )
            
            return self._handle_response(response, device_name)
            
        except requests.exceptions.Timeout:
            print("⏱️  Request timeout - NSO took too long to respond")
            return False
        except requests.exceptions.ConnectionError:
            print(f"🔌 Connection error - Cannot reach NSO at {self.nso_url}")
            return False
        except Exception as e:
            print(f"💥 Unexpected error: {str(e)}")
            return False
    
    def _handle_response(self, response: requests.Response, device_name: str) -> bool:
        """Handle and display API response"""
        
        if response.status_code in [200, 201, 204]:
            print("=" * 60)
            print("✅ SUCCESS! Configuration applied successfully")
            print("=" * 60)
            print(f"📱 Device: {device_name}")
            print(f"📊 Status Code: {response.status_code}")
            print(f"⏰ Response Time: {response.elapsed.total_seconds():.2f}s")
            
            if response.text:
                print(f"\n📄 Response Body:\n{response.text}")
            
            print("\n🎉 Configuration is now active on the device!")
            return True
        else:
            print("=" * 60)
            print("❌ FAILED! Configuration could not be applied")
            print("=" * 60)
            print(f"📱 Device: {device_name}")
            print(f"📊 Status Code: {response.status_code}")
            print(f"⏰ Response Time: {response.elapsed.total_seconds():.2f}s")
            print(f"\n❗ Error Details:\n{response.text}")
            print("\n💡 Tip: Check device connectivity and XML syntax")
            return False


def load_xml_file(file_path: str) -> Optional[str]:
    """
    Load XML content from file
    
    Args:
        file_path: Path to XML file
        
    Returns:
        XML content as string, or None if failed
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            print(f"❌ File not found: {file_path}")
            return None
        
        if not path.is_file():
            print(f"❌ Not a file: {file_path}")
            return None
        
        if path.suffix.lower() not in ['.xml', '.txt']:
            print(f"⚠️  Warning: File doesn't have .xml extension: {file_path}")
        
        print(f"📂 Loading XML file: {file_path}")
        content = path.read_text(encoding='utf-8')
        print(f"📏 File size: {len(content)} characters")
        print("✅ File loaded successfully\n")
        
        return content
        
    except UnicodeDecodeError:
        print(f"❌ Cannot decode file - not valid UTF-8: {file_path}")
        return None
    except PermissionError:
        print(f"❌ Permission denied reading file: {file_path}")
        return None
    except Exception as e:
        print(f"❌ Error loading file: {str(e)}")
        return None


def extract_device_name(xml_content: str) -> Optional[str]:
    """
    Extract device name from XML payload
    
    Args:
        xml_content: XML configuration content
        
    Returns:
        Device name if found, None otherwise
    """
    import re
    
    # Try to find device name in XML
    match = re.search(r'<name>([^<]+)</name>', xml_content)
    if match:
        return match.group(1)
    return None


def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(
        description='🔧 NSO RESTCONF Configuration Pusher',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s config.xml
  %(prog)s config.xml -d dc1-fgt-fw01
  %(prog)s config.xml -u admin -p admin123 -n http://nso.example.com:8080
  %(prog)s config1.xml config2.xml config3.xml
        """
    )
    
    parser.add_argument(
        'xml_files',
        nargs='+',
        help='XML configuration file(s) to push'
    )
    
    parser.add_argument(
        '-d', '--device',
        help='Device name (overrides device name in XML)'
    )
    
    parser.add_argument(
        '-n', '--nso-url',
        default='http://localhost:8080',
        help='NSO URL (default: http://localhost:8080)'
    )
    
    parser.add_argument(
        '-u', '--username',
        default='admin',
        help='NSO username (default: admin)'
    )
    
    parser.add_argument(
        '-p', '--password',
        default='admin',
        help='NSO password (default: admin)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("🔧 NSO RESTCONF Configuration Pusher")
    print("=" * 60 + "\n")
    
    # Initialize pusher
    pusher = ConfigPusher(args.nso_url, args.username, args.password)
    
    # Track results
    total_files = len(args.xml_files)
    successful = 0
    failed = 0
    
    # Process each file
    for i, xml_file in enumerate(args.xml_files, 1):
        print(f"\n{'🔷' * 30}")
        print(f"📦 Processing file {i}/{total_files}: {xml_file}")
        print(f"{'🔷' * 30}\n")
        
        # Load XML content
        xml_content = load_xml_file(xml_file)
        if not xml_content:
            print(f"⏭️  Skipping file: {xml_file}\n")
            failed += 1
            continue
        
        # Determine device name
        device_name = args.device
        if not device_name:
            device_name = extract_device_name(xml_content)
            if not device_name:
                print("❌ No device name specified and couldn't extract from XML")
                print("💡 Use -d/--device option to specify device name\n")
                failed += 1
                continue
            print(f"🔍 Auto-detected device name: {device_name}\n")
        
        # Show XML preview if verbose
        if args.verbose:
            print("📝 XML Preview (first 500 chars):")
            print("-" * 60)
            print(xml_content[:500])
            if len(xml_content) > 500:
                print("...")
            print("-" * 60 + "\n")
        
        # Push configuration
        if pusher.push_config(device_name, xml_content):
            successful += 1
        else:
            failed += 1
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 FINAL SUMMARY")
    print("=" * 60)
    print(f"📁 Total files processed: {total_files}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎊 All configurations applied successfully!")
        print("=" * 60 + "\n")
        sys.exit(0)
    else:
        print("\n⚠️  Some configurations failed")
        print("=" * 60 + "\n")
        sys.exit(1)


if __name__ == '__main__':
    main()