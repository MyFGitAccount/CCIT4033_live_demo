# Add to university_app/views.py
def connection_info(request):
    """Display connection information for clients"""
    import socket
    import requests

    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    context = {
        'local_ip': get_local_ip(),
        'port': 8000,
    }

    try:
        response = requests.get('https://api.ipify.org', timeout=3)
        context['public_ip'] = response.text
    except:
        context['public_ip'] = 'Not available (behind NAT)'

    return render(request, 'connection_info.html', context)
