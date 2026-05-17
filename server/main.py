import asyncio
import uvicorn
from api import app, get_gateway_state
from mesh import scan_neighbors, advertise_as_gateway, route_traffic, Node
from ai import rank_gateways, detect_anomalies
from energy import has_surplus_bandwidth, read_harvested_power_mw, get_power_mode
from db import log_metric

node = Node()

async def mesh_loop():
    while True:
        neighbors = await scan_neighbors()
        best_gateway = await rank_gateways(neighbors)

        is_gw = get_gateway_state()

        if has_surplus_bandwidth() and is_gw:
            await advertise_as_gateway(node)

        await route_traffic(best_gateway)
        await detect_anomalies(neighbors)

        power_mw = read_harvested_power_mw()
        mode = get_power_mode(power_mw)

        # Log metrics every heartbeat
        log_metric(
            gb_shared=round(len(neighbors) * 0.4, 1),
            uptime_pct=100.0 if mode.value != "Sleep" else 0.0,
            is_gateway=is_gw
        )

        print(f"Heartbeat - Neighbors: {len(neighbors)}, Gateway: {best_gateway.id}, Power: {mode}, GW: {is_gw}")

        await asyncio.sleep(30)

async def main():
    print("Meshwork v0.1 - Booting...")
    config = uvicorn.Config(app, host="0.0.0.0", port=8080, log_level="info")
    server = uvicorn.Server(config)
    await asyncio.gather(
        server.serve(),
        mesh_loop(),
    )

if __name__ == "__main__":
    asyncio.run(main())