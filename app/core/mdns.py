import socket
from zeroconf import ServiceInfo
from zeroconf.asyncio import AsyncZeroconf

async def register_mdns_service() -> AsyncZeroconf:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]

    async_zeroconf = AsyncZeroconf()
    service_info = ServiceInfo(
        type_='_manara._tcp.local.',
        name='Manara Backend._manara._tcp.local.',
        port=8000,
        addresses=[socket.inet_aton(local_ip)],
        properties={},
    )
    await async_zeroconf.async_register_service(service_info)

    return async_zeroconf
