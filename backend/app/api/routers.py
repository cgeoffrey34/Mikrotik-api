from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List
from datetime import datetime, timedelta
import logging

from ..database import get_db
from ..models import Router, RouterStats
from ..schemas import (
    RouterCreate,
    RouterUpdate,
    RouterResponse,
    RouterListResponse,
    RouterStatsResponse,
    RouterDetailResponse
)
from ..services import MikrotikService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/routers", tags=["routers"])


@router.get("", response_model=RouterListResponse)
async def get_routers(db: AsyncSession = Depends(get_db)):
    """Get all registered routers."""
    result = await db.execute(select(Router))
    routers = result.scalars().all()
    return RouterListResponse(
        routers=[RouterResponse.model_validate(r) for r in routers],
        total=len(routers)
    )


@router.get("/{router_id}", response_model=RouterDetailResponse)
async def get_router(router_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific router with its stats."""
    result = await db.execute(
        select(Router)
        .options(selectinload(Router.stats))
        .where(Router.id == router_id)
    )
    router_obj = result.scalar_one_or_none()

    if not router_obj:
        raise HTTPException(status_code=404, detail="Router not found")

    # Get latest stats
    stats_result = await db.execute(
        select(RouterStats)
        .where(RouterStats.router_id == router_id)
        .order_by(RouterStats.recorded_at.desc())
        .limit(50)
    )
    stats_list = stats_result.scalars().all()

    response = RouterDetailResponse.model_validate(router_obj)
    if stats_list:
        response.current_stats = RouterStatsResponse.model_validate(stats_list[0])
        response.stats_history = [RouterStatsResponse.model_validate(s) for s in stats_list]

    return response


@router.post("", response_model=RouterResponse, status_code=status.HTTP_201_CREATED)
async def create_router(router_data: RouterCreate, db: AsyncSession = Depends(get_db)):
    """Add a new router."""
    logger.info(f"Creating router '{router_data.name}' at {router_data.ip_address}:{router_data.api_port}")

    # Test connection first
    service = MikrotikService(
        host=router_data.ip_address,
        username=router_data.username,
        password=router_data.password,
        port=router_data.api_port,
        use_ssl=router_data.use_ssl
    )

    test_result = service.test_connection()
    logger.info(f"Connection test for '{router_data.name}': {test_result}")

    # Create router record
    new_router = Router(
        name=router_data.name,
        ip_address=router_data.ip_address,
        api_port=router_data.api_port,
        username=router_data.username,
        password=router_data.password,
        use_ssl=router_data.use_ssl,
        location=router_data.location,
        notes=router_data.notes,
        router_type=router_data.router_type,
        site=router_data.site,
        group=router_data.group,
        tags=router_data.tags,
        is_online=test_result["success"]
    )

    if test_result["success"]:
        new_router.last_seen = datetime.utcnow()

        # Get router info
        rb_info = service.get_routerboard_info()
        if rb_info:
            new_router.model = rb_info.get("model")
            new_router.serial_number = rb_info.get("serial_number")
            new_router.firmware_version = rb_info.get("firmware")

        resource = service.get_system_resource()
        if resource:
            new_router.ros_version = resource.get("version")

    db.add(new_router)
    await db.commit()
    await db.refresh(new_router)

    return RouterResponse.model_validate(new_router)


@router.put("/{router_id}", response_model=RouterResponse)
async def update_router(
    router_id: int,
    router_data: RouterUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a router."""
    result = await db.execute(select(Router).where(Router.id == router_id))
    router_obj = result.scalar_one_or_none()

    if not router_obj:
        raise HTTPException(status_code=404, detail="Router not found")

    update_data = router_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(router_obj, field, value)

    await db.commit()
    await db.refresh(router_obj)

    return RouterResponse.model_validate(router_obj)


@router.delete("/{router_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_router(router_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a router."""
    result = await db.execute(select(Router).where(Router.id == router_id))
    router_obj = result.scalar_one_or_none()

    if not router_obj:
        raise HTTPException(status_code=404, detail="Router not found")

    await db.delete(router_obj)
    await db.commit()


@router.post("/{router_id}/test", response_model=dict)
async def test_router_connection(router_id: int, db: AsyncSession = Depends(get_db)):
    """Test connection to a router."""
    result = await db.execute(select(Router).where(Router.id == router_id))
    router_obj = result.scalar_one_or_none()

    if not router_obj:
        raise HTTPException(status_code=404, detail="Router not found")

    logger.info(f"Testing connection for router #{router_id} ({router_obj.name}) at {router_obj.ip_address}:{router_obj.api_port}")

    service = MikrotikService(
        host=router_obj.ip_address,
        username=router_obj.username,
        password=router_obj.password,
        port=router_obj.api_port,
        use_ssl=router_obj.use_ssl
    )

    test_result = service.test_connection()
    logger.info(f"Connection test for router #{router_id} ({router_obj.name}): {test_result}")

    # Update router status
    router_obj.is_online = test_result["success"]
    if test_result["success"]:
        router_obj.last_seen = datetime.utcnow()

    await db.commit()

    return test_result


@router.post("/{router_id}/refresh", response_model=RouterStatsResponse)
async def refresh_router_stats(router_id: int, db: AsyncSession = Depends(get_db)):
    """Refresh stats for a router."""
    result = await db.execute(select(Router).where(Router.id == router_id))
    router_obj = result.scalar_one_or_none()

    if not router_obj:
        raise HTTPException(status_code=404, detail="Router not found")

    service = MikrotikService(
        host=router_obj.ip_address,
        username=router_obj.username,
        password=router_obj.password,
        port=router_obj.api_port,
        use_ssl=router_obj.use_ssl
    )

    # Get stats
    resource = service.get_system_resource()
    if not resource:
        raise HTTPException(status_code=503, detail="Could not connect to router")

    wifi_clients = service.get_wifi_clients()
    dhcp_leases = service.get_dhcp_leases()
    connections = service.get_active_connections()

    # Create stats record
    stats = RouterStats(
        router_id=router_id,
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

    # Update router info
    router_obj.is_online = True
    router_obj.last_seen = datetime.utcnow()
    router_obj.ros_version = resource.get("version")

    # Populate missing routerboard info
    if not router_obj.model or not router_obj.serial_number or not router_obj.firmware_version:
        rb_info = service.get_routerboard_info()
        if rb_info:
            if not router_obj.model:
                router_obj.model = rb_info.get("model") or resource.get("board_name")
            if not router_obj.serial_number:
                router_obj.serial_number = rb_info.get("serial_number")
            if not router_obj.firmware_version:
                router_obj.firmware_version = rb_info.get("firmware")
        elif not router_obj.model and resource.get("board_name"):
            router_obj.model = resource["board_name"]

    await db.commit()
    await db.refresh(stats)

    return RouterStatsResponse.model_validate(stats)


@router.get("/{router_id}/stats", response_model=List[RouterStatsResponse])
async def get_router_stats(
    router_id: int,
    hours: int = 24,
    db: AsyncSession = Depends(get_db)
):
    """Get historical stats for a router."""
    since = datetime.utcnow() - timedelta(hours=hours)

    result = await db.execute(
        select(RouterStats)
        .where(RouterStats.router_id == router_id)
        .where(RouterStats.recorded_at >= since)
        .order_by(RouterStats.recorded_at.desc())
    )
    stats = result.scalars().all()

    return [RouterStatsResponse.model_validate(s) for s in stats]
