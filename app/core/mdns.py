import socket
from zeroconf import Zeroconf, ServiceInfo

def register_mdns_service() -> Zeroconf:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]

    zeroconf_instance = Zeroconf()
    service_info = ServiceInfo(
        type_='_manara._tcp.local.',
        name='Manara Backend._manara._tcp.local.',
        port=8000,
        addresses=[socket.inet_aton(local_ip)],
        properties={},
    )
    zeroconf_instance.register_service(service_info)

    return zeroconf_instance
