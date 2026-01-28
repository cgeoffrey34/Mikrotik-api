import asyncio
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from .database import async_session
from .models import Router, RouterStats
from .services import MikrotikService
from .config import get_settings

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def poll_all_routers():
    """Poll all routers for status and stats."""
    logger.info("Starting scheduled router polling...")

    try:
        async with async_session() as db:
            try:
                result = await db.execute(select(Router))
                routers = result.scalars().all()

                if not routers:
                    logger.info("No routers configured, skipping poll")
                    return

                logger.info(f"Polling {len(routers)} router(s)...")

                online_count = 0
                offline_count = 0

                for router_obj in routers:
                    try:
                        service = MikrotikService(
                            host=router_obj.ip_address,
                            username=router_obj.username,
                            password=router_obj.password,
                            port=router_obj.api_port,
                            use_ssl=router_obj.use_ssl
                        )

                        test_result = service.test_connection()

                        router_obj.is_online = test_result["success"]

                        if test_result["success"]:
                            online_count += 1
                            router_obj.last_seen = datetime.utcnow()

                            # Populate missing routerboard info (model, serial, firmware)
                            if not router_obj.model or not router_obj.serial_number or not router_obj.firmware_version:
                                try:
                                    rb_info = service.get_routerboard_info()
                                    if rb_info:
                                        if not router_obj.model and rb_info.get("model"):
                                            router_obj.model = rb_info["model"]
                                        if not router_obj.serial_number and rb_info.get("serial_number"):
                                            router_obj.serial_number = rb_info["serial_number"]
                                        if not router_obj.firmware_version and rb_info.get("firmware"):
                                            router_obj.firmware_version = rb_info["firmware"]
                                        logger.info(f"Updated routerboard info for '{router_obj.name}': model={router_obj.model}, serial={router_obj.serial_number}")
                                except Exception as e:
                                    logger.warning(f"Failed to get routerboard info for '{router_obj.name}': {e}")

                            # Collect stats for online routers
                            try:
                                resource = service.get_system_resource()
                                if resource:
                                    wifi_clients = service.get_wifi_clients()
                                    dhcp_leases = service.get_dhcp_leases()
                                    connections = service.get_active_connections()

                                    stats = RouterStats(
                                        router_id=router_obj.id,
                                        cpu_load=resource.get("cpu_load"),
                                        memory_used=resource.get("memory_used"),
                                        memory_total=resource.get("memory_total"),
                                        disk_used=resource.get("disk_used"),
                                        disk_total=resource.get("disk_total"),
                                        uptime=resource.get("uptime"),
                                        wifi_clients=len(wifi_clients),
                                        dhcp_leases=len([l for l in dhcp_leases if l.get("status") == "bound"]),
                                        active_connections=connections
                                    )
                                    db.add(stats)

                                    router_obj.ros_version = resource.get("version")

                                    # Fallback: use board_name from resource if model still empty
                                    if not router_obj.model and resource.get("board_name"):
                                        router_obj.model = resource["board_name"]
                            except Exception as e:
                                logger.warning(f"Failed to collect stats for '{router_obj.name}': {e}")
                        else:
                            offline_count += 1

                    except Exception as e:
                        offline_count += 1
                        logger.error(f"Error polling router '{router_obj.name}' ({router_obj.ip_address}): {e}")
                        router_obj.is_online = False

                await db.commit()
                logger.info(f"Polling complete: {online_count} online, {offline_count} offline")

            except asyncio.CancelledError:
                logger.warning("Router polling was cancelled")
                raise
            except Exception as e:
                logger.error(f"Error during router polling: {e}")
                await db.rollback()
    except asyncio.CancelledError:
        logger.warning("Router polling cancelled during DB session setup")
    except Exception as e:
        logger.error(f"Failed to open DB session for polling: {e}")


def start_scheduler():
    """Start the background scheduler."""
    settings = get_settings()
    interval = settings.stats_polling_interval

    scheduler.add_job(
        poll_all_routers,
        'interval',
        seconds=interval,
        id='poll_routers',
        name='Poll all routers for status and stats',
        replace_existing=True
    )

    # Run initial poll after 15 seconds to let app fully initialize
    scheduler.add_job(
        poll_all_routers,
        'date',
        run_date=datetime.utcnow() + timedelta(seconds=15),
        id='poll_routers_initial',
        name='Initial router poll'
    )

    scheduler.start()
    logger.info(f"Scheduler started - polling every {interval} seconds (initial poll in 15s)")


def stop_scheduler():
    """Stop the background scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
