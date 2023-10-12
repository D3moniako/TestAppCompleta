import httpx

async def check_consul_service():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://consul:8500/v1/agent/services")
        services = response.json()
        if "fastapi-service" in services:
            print("FastAPI service is registered in Consul.")
        else:
            print("FastAPI service is NOT registered in Consul.")

if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(check_consul_service())
