from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from ..database import get_db
from ..models import Router
from ..schemas import (
    DHCPLease,
    WifiClient,
    Interface,
    FirewallRule,
    NATRule,
    DNSEntry,
    QueueRule,
    IPAddress,
    Route,
    WirelessInterface,
    WirelessSecurityProfile
)
from ..services import MikrotikService

router = APIRouter(prefix="/routers/{router_id}", tags=["mikrotik"])


async def get_router_service(router_id: int, db: AsyncSession) -> tuple[Router, MikrotikService]:
    """Helper to get router and its service."""
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

    return router_obj, service


# ==================== DHCP ====================

@router.get("/dhcp/leases", response_model=List[DHCPLease])
async def get_dhcp_leases(router_id: int, db: AsyncSession = Depends(get_db)):
    """Get DHCP leases from router."""
    _, service = await get_router_service(router_id, db)
    leases = service.get_dhcp_leases()
    return [DHCPLease(**lease) for lease in leases]


@router.post("/dhcp/leases")
async def add_dhcp_lease(
    router_id: int,
    address: str,
    mac_address: str,
    server: str = "default",
    comment: str = "",
    db: AsyncSession = Depends(get_db)
):
    """Add a static DHCP lease."""
    _, service = await get_router_service(router_id, db)
    success = service.add_dhcp_lease(address, mac_address, server, comment)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add DHCP lease")
    return {"success": True}


@router.delete("/dhcp/leases/{lease_id}")
async def delete_dhcp_lease(router_id: int, lease_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a DHCP lease."""
    _, service = await get_router_service(router_id, db)
    success = service.delete_dhcp_lease(lease_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete DHCP lease")
    return {"success": True}


# ==================== WiFi ====================

@router.get("/wifi/clients", response_model=List[WifiClient])
async def get_wifi_clients(router_id: int, db: AsyncSession = Depends(get_db)):
    """Get connected WiFi clients."""
    _, service = await get_router_service(router_id, db)
    clients = service.get_wifi_clients()
    return [WifiClient(**client) for client in clients]


@router.get("/wifi/interfaces", response_model=List[WirelessInterface])
async def get_wireless_interfaces(router_id: int, db: AsyncSession = Depends(get_db)):
    """Get wireless interfaces."""
    _, service = await get_router_service(router_id, db)
    interfaces = service.get_wireless_interfaces()
    return [WirelessInterface(**iface) for iface in interfaces]


@router.get("/wifi/security-profiles", response_model=List[WirelessSecurityProfile])
async def get_security_profiles(router_id: int, db: AsyncSession = Depends(get_db)):
    """Get wireless security profiles."""
    _, service = await get_router_service(router_id, db)
    profiles = service.get_security_profiles()
    return [WirelessSecurityProfile(**profile) for profile in profiles]


# ==================== Interfaces ====================

@router.get("/interfaces", response_model=List[Interface])
async def get_interfaces(router_id: int, db: AsyncSession = Depends(get_db)):
    """Get all interfaces."""
    _, service = await get_router_service(router_id, db)
    interfaces = service.get_interfaces()
    return [Interface(**iface) for iface in interfaces]


@router.post("/interfaces/{interface_id}/toggle")
async def toggle_interface(
    router_id: int,
    interface_id: str,
    enable: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """Enable or disable an interface."""
    _, service = await get_router_service(router_id, db)
    success = service.toggle_interface(interface_id, enable)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to toggle interface")
    return {"success": True}


# ==================== IP Addresses ====================

@router.get("/ip/addresses", response_model=List[IPAddress])
async def get_ip_addresses(router_id: int, db: AsyncSession = Depends(get_db)):
    """Get all IP addresses."""
    _, service = await get_router_service(router_id, db)
    addresses = service.get_ip_addresses()
    return [IPAddress(**addr) for addr in addresses]


@router.post("/ip/addresses")
async def add_ip_address(
    router_id: int,
    address: str,
    interface: str,
    comment: str = "",
    db: AsyncSession = Depends(get_db)
):
    """Add an IP address."""
    _, service = await get_router_service(router_id, db)
    success = service.add_ip_address(address, interface, comment)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add IP address")
    return {"success": True}


@router.delete("/ip/addresses/{address_id}")
async def delete_ip_address(router_id: int, address_id: str, db: AsyncSession = Depends(get_db)):
    """Delete an IP address."""
    _, service = await get_router_service(router_id, db)
    success = service.delete_ip_address(address_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete IP address")
    return {"success": True}


# ==================== Routes ====================

@router.get("/ip/routes", response_model=List[Route])
async def get_routes(router_id: int, db: AsyncSession = Depends(get_db)):
    """Get all routes."""
    _, service = await get_router_service(router_id, db)
    routes = service.get_routes()
    return [Route(**route) for route in routes]


@router.post("/ip/routes")
async def add_route(
    router_id: int,
    dst_address: str,
    gateway: str,
    distance: int = 1,
    comment: str = "",
    db: AsyncSession = Depends(get_db)
):
    """Add a static route."""
    _, service = await get_router_service(router_id, db)
    success = service.add_route(dst_address, gateway, distance, comment)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add route")
    return {"success": True}


@router.delete("/ip/routes/{route_id}")
async def delete_route(router_id: int, route_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a route."""
    _, service = await get_router_service(router_id, db)
    success = service.delete_route(route_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete route")
    return {"success": True}


# ==================== Firewall ====================

@router.get("/firewall/filter", response_model=List[FirewallRule])
async def get_firewall_rules(router_id: int, db: AsyncSession = Depends(get_db)):
    """Get firewall filter rules."""
    _, service = await get_router_service(router_id, db)
    rules = service.get_firewall_filter_rules()
    return [FirewallRule(**rule) for rule in rules]


@router.post("/firewall/filter/{rule_id}/toggle")
async def toggle_firewall_rule(
    router_id: int,
    rule_id: str,
    enable: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """Enable or disable a firewall rule."""
    _, service = await get_router_service(router_id, db)
    success = service.toggle_firewall_rule(rule_id, enable)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to toggle firewall rule")
    return {"success": True}


@router.get("/firewall/nat", response_model=List[NATRule])
async def get_nat_rules(router_id: int, db: AsyncSession = Depends(get_db)):
    """Get NAT rules."""
    _, service = await get_router_service(router_id, db)
    rules = service.get_nat_rules()
    return [NATRule(**rule) for rule in rules]


# ==================== DNS ====================

@router.get("/dns/static", response_model=List[DNSEntry])
async def get_dns_entries(router_id: int, db: AsyncSession = Depends(get_db)):
    """Get static DNS entries."""
    _, service = await get_router_service(router_id, db)
    entries = service.get_dns_static()
    return [DNSEntry(**entry) for entry in entries]


@router.post("/dns/static")
async def add_dns_entry(
    router_id: int,
    name: str,
    address: str,
    ttl: str = "1d",
    comment: str = "",
    db: AsyncSession = Depends(get_db)
):
    """Add a static DNS entry."""
    _, service = await get_router_service(router_id, db)
    success = service.add_dns_static(name, address, ttl, comment)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add DNS entry")
    return {"success": True}


@router.delete("/dns/static/{entry_id}")
async def delete_dns_entry(router_id: int, entry_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a static DNS entry."""
    _, service = await get_router_service(router_id, db)
    success = service.delete_dns_static(entry_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete DNS entry")
    return {"success": True}


# ==================== Queues (QoS) ====================

@router.get("/queues/simple", response_model=List[QueueRule])
async def get_queues(router_id: int, db: AsyncSession = Depends(get_db)):
    """Get simple queue rules."""
    _, service = await get_router_service(router_id, db)
    queues = service.get_simple_queues()
    return [QueueRule(**queue) for queue in queues]


@router.post("/queues/simple/{queue_id}/toggle")
async def toggle_queue(
    router_id: int,
    queue_id: str,
    enable: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """Enable or disable a queue."""
    _, service = await get_router_service(router_id, db)
    success = service.toggle_queue(queue_id, enable)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to toggle queue")
    return {"success": True}


# ==================== System ====================

@router.get("/system/logs")
async def get_logs(router_id: int, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Get system logs."""
    _, service = await get_router_service(router_id, db)
    logs = service.get_logs(limit)
    return logs


@router.get("/system/users")
async def get_users(router_id: int, db: AsyncSession = Depends(get_db)):
    """Get system users."""
    _, service = await get_router_service(router_id, db)
    users = service.get_users()
    return users


@router.post("/system/reboot")
async def reboot_router(router_id: int, db: AsyncSession = Depends(get_db)):
    """Reboot the router."""
    _, service = await get_router_service(router_id, db)
    success = service.reboot()
    if not success:
        raise HTTPException(status_code=500, detail="Failed to reboot router")
    return {"success": True, "message": "Router is rebooting"}


@router.post("/system/backup")
async def create_backup(router_id: int, db: AsyncSession = Depends(get_db)):
    """Create a backup on the router."""
    _, service = await get_router_service(router_id, db)
    filename = service.backup_config()
    if not filename:
        raise HTTPException(status_code=500, detail="Failed to create backup")
    return {"success": True, "filename": filename}


@router.get("/system/export")
async def export_config(router_id: int, db: AsyncSession = Depends(get_db)):
    """Export router configuration as text."""
    _, service = await get_router_service(router_id, db)
    config = service.export_config()
    if not config:
        raise HTTPException(status_code=500, detail="Failed to export configuration")
    return {"success": True, "config": config}
