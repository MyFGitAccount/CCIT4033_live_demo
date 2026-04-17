#!/usr/bin/env python
# run_network_server.py - Start Django server accessible from any computer

import os
import sys
import socket
import subprocess
import webbrowser
from time import sleep

def get_local_ip():
    """Get the local IP address of this computer"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        print(f"Error getting IP: {e}")
        return "127.0.0.1"

def get_public_ip():
    """Try to get public IP (for internet access)"""
    try:
        import requests
        response = requests.get('https://api.ipify.org', timeout=5)
        return response.text
    except:
        return "Unable to determine public IP (no internet or behind NAT)"

def main():
    local_ip = get_local_ip()
    public_ip = get_public_ip()
    port = 8000
    
    print("=" * 60)
    print("🚀 UNIVERSITY DBMS NETWORK SERVER")
    print("=" * 60)
    print(f"\n📡 Server is starting...")
    print(f"\n📍 ACCESS YOUR APP FROM ANY DEVICE:")
    print(f"\n   On THIS computer:")
    print(f"   → http://localhost:{port}")
    print(f"   → http://127.0.0.1:{port}")
    print(f"\n   On OTHER computers on the SAME NETWORK (WiFi/LAN):")
    print(f"   → http://{local_ip}:{port}")
    print(f"\n   From the INTERNET (if port forwarded):")
    print(f"   → http://{public_ip}:{port}" if public_ip != "Unable to determine public IP" else "   → (Configure port forwarding on your router)")
    
    print(f"\n⚠️  IMPORTANT NOTES:")
    print(f"   • All devices must be on the same network")
    print(f"   • You may need to allow port {port} in your firewall")
    print(f"   • Keep this terminal window open")
    print(f"   • Press CTRL+C to stop the server")
    print("=" * 60)
    
    # Ask for confirmation
    response = input(f"\n🌐 Start server on http://{local_ip}:{port}? (y/n): ")
    if response.lower() != 'y':
        print("Server start cancelled.")
        return
    
    # Open browser automatically
    webbrowser.open(f'http://localhost:{port}')
    
    # Run Django server on all interfaces
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'university_dbms.settings')
    
    try:
        from django.core.management import execute_from_command_line
        # Run on 0.0.0.0 to accept connections from any device
        sys.argv = ['manage.py', 'runserver', f'0.0.0.0:{port}', '--insecure']
        execute_from_command_line(sys.argv)
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTry running: python manage.py runserver 0.0.0.0:8000")

if __name__ == '__main__':
    main()
