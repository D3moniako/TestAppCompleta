import requests

def register_service(service_id, service_name, service_address, service_port):
    consul_url = "http://consul:8500/v1/agent/service/register"
    data = {
        "ID": service_id,
        "Name": service_name,
        "Address": service_address,
        "Port": service_port,
    }
    response = requests.put(consul_url, json=data)
    response.raise_for_status()

def get_services():
    consul_url = "http://consul:8500/v1/agent/services"
    response = requests.get(consul_url)
    response.raise_for_status()
    return response.json()
