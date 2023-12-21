
from consul.aio import Consul

async def register_service(service_name, service_port):
    print(f"Registering service {service_name}...")

    try:
        consul = Consul(host='consul', port=8500)
        await consul.agent.service.register(service_name, port=service_port)
        print(f"Service {service_name} registered successfully!")
    except Exception as e:
        print(f"Failed to register service {service_name}: {e}")

