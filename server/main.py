import asyncio
import logging
import uvicorn
from api import app, get_gateway_state
from mesh import scan_neighbors, advertise_as_gateway, route_traffic, Node
from ai import rank_gateways, detect_anomalies
from energy import has_surplus_bandwidth, read_harvested_power_mw, get_power_mode
from db import log_metric
from serial_link import init_serial_link, get_link

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("meshwork.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

node = Node()

async def mesh_loop():
    logger.info("Starting mesh loop")
    while True:
        try:
            neighbors = await scan_neighbors()
            logger.debug(f"Scanned {len(neighbors)} neighbors")
            
            best_gateway = await rank_gateways(neighbors)
            logger.info(f"Best gateway: {best_gateway.id}")

            is_gw = get_gateway_state()

            if has_surplus_bandwidth() and is_gw:
                await advertise_as_gateway(node)
                logger.info("Advertised as gateway")

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

            logger.info(f"Heartbeat - Neighbors: {len(neighbors)}, Gateway: {best_gateway.id}, Power: {mode}, GW: {is_gw}")

            await asyncio.sleep(30)
        except Exception as e:
            logger.error(f"Mesh loop error: {e}", exc_info=True)
            await asyncio.sleep(30)

async def main():
    logger.info("Meshwork v0.1 - Booting...")

    # Initialize serial link to C++ firmware layer
    # In production: /dev/ttyUSB0 or /dev/ttyACM0
    # In development: simulation mode (no hardware needed)
    serial_port = None  # Set to "/dev/ttyUSB0" when firmware is connected
    try:
        init_serial_link(port=serial_port)
        logger.info(f"Serial link initialized (port: {serial_port or 'simulation'})")
    except Exception as e:
        logger.error(f"Failed to initialize serial link: {e}", exc_info=True)

    config = uvicorn.Config(app, host="0.0.0.0", port=8080, log_level="info")
    server = uvicorn.Server(config)
    await asyncio.gather(
        server.serve(),
        mesh_loop(),
    )

if __name__ == "__main__":
    asyncio.run(main())