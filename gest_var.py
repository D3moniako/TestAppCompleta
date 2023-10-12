import os

consul_http_addr = os.environ.get("CONSUL_HTTP_ADDR")
service_name = os.environ.get("SERVICE_NAME")
service_port = os.environ.get("SERVICE_PORT")
print(str(consul_http_addr)+str(service_name)+str(service_port))