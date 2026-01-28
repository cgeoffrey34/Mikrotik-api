from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from ..database import get_db
from ..models import Router
from ..schemas import (
    DHCPLease, DHCPServer, DHCPNetwork, IPPool,
    WifiClient, WirelessInterface, WirelessSecurityProfile,
    Interface,
    Bridge, BridgePort, BridgeVlan,
    IPAddress, Route,
    FirewallRule, FirewallRuleCreate, NATRule, NATRuleCreate,
    MangleRule, MangleRuleCreate, RawRule, RawRuleCreate,
    ServicePort, ConnectionEntry, AddressListEntry, AddressListEntryCreate,
    DNSEntry, DNSEntryCreate, DNSSettings, DNSSettingsUpdate, DNSCacheEntry,
    QueueRule
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
    hostname: str = "",
    comment: str = "",
    db: AsyncSession = Depends(get_db)
):
    """Add a static DHCP lease."""
    _, service = await get_router_service(router_id, db)
    success = service.add_dhcp_lease(address, mac_address, server, hostname, comment)
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


@router.post("/dhcp/leases/{lease_id}/make-static")
async def make_dhcp_lease_static(router_id: int, lease_id: str, db: AsyncSession = Depends(get_db)):
    """Make a dynamic DHCP lease static."""
    _, service = await get_router_service(router_id, db)
    success = service.make_dhcp_lease_static(lease_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to make lease static")
    return {"success": True}


@router.get("/dhcp/servers", response_model=List[DHCPServer])
async def get_dhcp_servers(router_id: int, db: AsyncSession = Depends(get_db)):
    """Get DHCP servers."""
    _, service = await get_router_service(router_id, db)
    servers = service.get_dhcp_servers()
    return [DHCPServer(**srv) for srv in servers]


@router.post("/dhcp/servers/{server_id}/toggle")
async def toggle_dhcp_server(
    router_id: int,
    server_id: str,
    enable: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """Enable or disable a DHCP server."""
    _, service = await get_router_service(router_id, db)
    success = service.toggle_dhcp_server(server_id, enable)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to toggle DHCP server")
    return {"success": True}


@router.get("/dhcp/networks", response_model=List[DHCPNetwork])
async def get_dhcp_networks(router_id: int, db: AsyncSession = Depends(get_db)):
    """Get DHCP network configurations."""
    _, service = await get_router_service(router_id, db)
    networks = service.get_dhcp_networks()
    return [DHCPNetwork(**net) for net in networks]


@router.get("/dhcp/pools", response_model=List[IPPool])
async def get_ip_pools(router_id: int, db: AsyncSession = Depends(get_db)):
    """Get IP pools."""
    _, service = await get_router_service(router_id, db)
    pools = service.get_ip_pools()
    return [IPPool(**pool) for pool in pools]


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


@router.post("/wifi/interfaces/{interface_id}/update")
async def update_wireless_interface(
    router_id: int,
    interface_id: str,
    ssid: str = None,
    security_profile: str = None,
    disabled: bool = None,
    db: AsyncSession = Depends(get_db)
):
    """Update wireless interface settings."""
    _, service = await get_router_service(router_id, db)
    success = service.update_wireless_interface(interface_id, ssid, security_profile, disabled)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update wireless interface")
    return {"success": True}


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


# ==================== Bridges ====================

@router.get("/bridges", response_model=List[Bridge])
async def get_bridges(router_id: int, db: AsyncSession = Depends(get_db)):
    """Get all bridges."""
    _, service = await get_router_service(router_id, db)
    bridges = service.get_bridges()
    return [Bridge(**br) for br in bridges]


@router.post("/bridges")
async def add_bridge(
    router_id: int,
    name: str,
    comment: str = "",
    vlan_filtering: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Add a new bridge."""
    _, service = await get_router_service(router_id, db)
    success = service.add_bridge(name, comment, vlan_filtering)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add bridge")
    return {"success": True}


@router.delete("/bridges/{bridge_id}")
async def delete_bridge(router_id: int, bridge_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a bridge."""
    _, service = await get_router_service(router_id, db)
    success = service.delete_bridge(bridge_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete bridge")
    return {"success": True}


@router.get("/bridges/ports", response_model=List[BridgePort])
async def get_bridge_ports(router_id: int, db: AsyncSession = Depends(get_db)):
    """Get all bridge ports."""
    _, service = await get_router_service(router_id, db)
    ports = service.get_bridge_ports()
    return [BridgePort(**port) for port in ports]


@router.post("/bridges/ports")
async def add_bridge_port(
    router_id: int,
    bridge: str,
    interface: str,
    pvid: int = 1,
    comment: str = "",
    db: AsyncSession = Depends(get_db)
):
    """Add an interface to a bridge."""
    _, service = await get_router_service(router_id, db)
    success = service.add_bridge_port(bridge, interface, pvid, comment)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add bridge port")
    return {"success": True}


@router.delete("/bridges/ports/{port_id}")
async def delete_bridge_port(router_id: int, port_id: str, db: AsyncSession = Depends(get_db)):
    """Remove an interface from a bridge."""
    _, service = await get_router_service(router_id, db)
    success = service.delete_bridge_port(port_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete bridge port")
    return {"success": True}


@router.get("/bridges/vlans", response_model=List[BridgeVlan])
async def get_bridge_vlans(router_id: int, db: AsyncSession = Depends(get_db)):
    """Get bridge VLAN configurations."""
    _, service = await get_router_service(router_id, db)
    vlans = service.get_bridge_vlans()
    return [BridgeVlan(**vlan) for vlan in vlans]


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

@router.get("/firewall/filter")
async def get_firewall_rules(router_id: int, db: AsyncSession = Depends(get_db)):
    """Get firewall filter rules."""
    _, service = await get_router_service(router_id, db)
    return service.get_firewall_filter_rules()


@router.post("/firewall/filter")
async def add_firewall_rule(
    router_id: int,
    rule: FirewallRuleCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add a firewall filter rule."""
    _, service = await get_router_service(router_id, db)
    success = service.add_firewall_rule(
        chain=rule.chain,
        action=rule.action,
        src_address=rule.src_address,
        dst_address=rule.dst_address,
        protocol=rule.protocol,
        src_port=rule.src_port,
        dst_port=rule.dst_port,
        in_interface=rule.in_interface,
        out_interface=rule.out_interface,
        connection_state=rule.connection_state,
        comment=rule.comment,
        disabled=rule.disabled
    )
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add firewall rule")
    return {"success": True}


@router.delete("/firewall/filter/{rule_id}")
async def delete_firewall_rule(router_id: int, rule_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a firewall filter rule."""
    _, service = await get_router_service(router_id, db)
    success = service.delete_firewall_rule(rule_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete firewall rule")
    return {"success": True}


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


@router.get("/firewall/nat")
async def get_nat_rules(router_id: int, db: AsyncSession = Depends(get_db)):
    """Get NAT rules."""
    _, service = await get_router_service(router_id, db)
    return service.get_nat_rules()


@router.post("/firewall/nat")
async def add_nat_rule(
    router_id: int,
    rule: NATRuleCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add a NAT rule."""
    _, service = await get_router_service(router_id, db)
    success = service.add_nat_rule(
        chain=rule.chain,
        action=rule.action,
        src_address=rule.src_address,
        dst_address=rule.dst_address,
        protocol=rule.protocol,
        src_port=rule.src_port,
        dst_port=rule.dst_port,
        to_addresses=rule.to_addresses,
        to_ports=rule.to_ports,
        in_interface=rule.in_interface,
        out_interface=rule.out_interface,
        comment=rule.comment,
        disabled=rule.disabled
    )
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add NAT rule")
    return {"success": True}


@router.delete("/firewall/nat/{rule_id}")
async def delete_nat_rule(router_id: int, rule_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a NAT rule."""
    _, service = await get_router_service(router_id, db)
    success = service.delete_nat_rule(rule_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete NAT rule")
    return {"success": True}


@router.post("/firewall/nat/{rule_id}/toggle")
async def toggle_nat_rule(
    router_id: int,
    rule_id: str,
    enable: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """Enable or disable a NAT rule."""
    _, service = await get_router_service(router_id, db)
    success = service.toggle_nat_rule(rule_id, enable)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to toggle NAT rule")
    return {"success": True}


# ==================== Mangle ====================

@router.get("/firewall/mangle")
async def get_mangle_rules(router_id: int, db: AsyncSession = Depends(get_db)):
    """Get mangle rules."""
    _, service = await get_router_service(router_id, db)
    return service.get_mangle_rules()


@router.post("/firewall/mangle")
async def add_mangle_rule(
    router_id: int,
    rule: MangleRuleCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add a mangle rule."""
    _, service = await get_router_service(router_id, db)
    success = service.add_mangle_rule(**rule.model_dump(exclude_none=True))
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add mangle rule")
    return {"success": True}


@router.delete("/firewall/mangle/{rule_id}")
async def delete_mangle_rule(router_id: int, rule_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a mangle rule."""
    _, service = await get_router_service(router_id, db)
    success = service.delete_mangle_rule(rule_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete mangle rule")
    return {"success": True}


@router.post("/firewall/mangle/{rule_id}/toggle")
async def toggle_mangle_rule(
    router_id: int,
    rule_id: str,
    enable: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """Enable or disable a mangle rule."""
    _, service = await get_router_service(router_id, db)
    success = service.toggle_mangle_rule(rule_id, enable)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to toggle mangle rule")
    return {"success": True}


# ==================== RAW ====================

@router.get("/firewall/raw")
async def get_raw_rules(router_id: int, db: AsyncSession = Depends(get_db)):
    """Get RAW firewall rules."""
    _, service = await get_router_service(router_id, db)
    return service.get_raw_rules()


@router.post("/firewall/raw")
async def add_raw_rule(
    router_id: int,
    rule: RawRuleCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add a RAW firewall rule."""
    _, service = await get_router_service(router_id, db)
    success = service.add_raw_rule(**rule.model_dump(exclude_none=True))
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add RAW rule")
    return {"success": True}


@router.delete("/firewall/raw/{rule_id}")
async def delete_raw_rule(router_id: int, rule_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a RAW rule."""
    _, service = await get_router_service(router_id, db)
    success = service.delete_raw_rule(rule_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete RAW rule")
    return {"success": True}


@router.post("/firewall/raw/{rule_id}/toggle")
async def toggle_raw_rule(
    router_id: int,
    rule_id: str,
    enable: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """Enable or disable a RAW rule."""
    _, service = await get_router_service(router_id, db)
    success = service.toggle_raw_rule(rule_id, enable)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to toggle RAW rule")
    return {"success": True}


# ==================== Service Ports ====================

@router.get("/firewall/service-ports")
async def get_service_ports(router_id: int, db: AsyncSession = Depends(get_db)):
    """Get firewall service ports (ALG helpers)."""
    _, service = await get_router_service(router_id, db)
    return service.get_service_ports()


@router.post("/firewall/service-ports/{port_id}/toggle")
async def toggle_service_port(
    router_id: int,
    port_id: str,
    enable: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """Enable or disable a service port."""
    _, service = await get_router_service(router_id, db)
    success = service.toggle_service_port(port_id, enable)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to toggle service port")
    return {"success": True}


# ==================== Connections ====================

@router.get("/firewall/connections")
async def get_connections(router_id: int, db: AsyncSession = Depends(get_db)):
    """Get active firewall connections."""
    _, service = await get_router_service(router_id, db)
    return service.get_connections()


@router.delete("/firewall/connections/{conn_id}")
async def remove_connection(router_id: int, conn_id: str, db: AsyncSession = Depends(get_db)):
    """Remove a connection from the tracking table."""
    _, service = await get_router_service(router_id, db)
    success = service.remove_connection(conn_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to remove connection")
    return {"success": True}


# ==================== Address Lists ====================

@router.get("/firewall/address-lists")
async def get_address_lists(router_id: int, db: AsyncSession = Depends(get_db)):
    """Get firewall address list entries."""
    _, service = await get_router_service(router_id, db)
    return service.get_address_lists()


@router.post("/firewall/address-lists")
async def add_address_list_entry(
    router_id: int,
    entry: AddressListEntryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add an entry to a firewall address list."""
    _, service = await get_router_service(router_id, db)
    success = service.add_address_list_entry(
        list_name=entry.list,
        address=entry.address,
        timeout=entry.timeout or "",
        comment=entry.comment or "",
        disabled=entry.disabled
    )
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add address list entry")
    return {"success": True}


@router.delete("/firewall/address-lists/{entry_id}")
async def delete_address_list_entry(router_id: int, entry_id: str, db: AsyncSession = Depends(get_db)):
    """Delete an address list entry."""
    _, service = await get_router_service(router_id, db)
    success = service.delete_address_list_entry(entry_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete address list entry")
    return {"success": True}


@router.post("/firewall/address-lists/{entry_id}/toggle")
async def toggle_address_list_entry(
    router_id: int,
    entry_id: str,
    enable: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """Enable or disable an address list entry."""
    _, service = await get_router_service(router_id, db)
    success = service.toggle_address_list_entry(entry_id, enable)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to toggle address list entry")
    return {"success": True}


# ==================== DNS ====================

@router.get("/dns/settings", response_model=DNSSettings)
async def get_dns_settings(router_id: int, db: AsyncSession = Depends(get_db)):
    """Get DNS server settings."""
    _, service = await get_router_service(router_id, db)
    settings = service.get_dns_settings()
    if not settings:
        raise HTTPException(status_code=500, detail="Failed to get DNS settings")
    return DNSSettings(**settings)


@router.get("/dns/static", response_model=List[DNSEntry])
async def get_dns_entries(router_id: int, db: AsyncSession = Depends(get_db)):
    """Get static DNS entries."""
    _, service = await get_router_service(router_id, db)
    entries = service.get_dns_static()
    return [DNSEntry(**entry) for entry in entries]


@router.post("/dns/static")
async def add_dns_entry(
    router_id: int,
    entry: DNSEntryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add a static DNS entry (supports A, AAAA, CNAME, MX, TXT, NS, SRV, NXDOMAIN, FWD)."""
    _, service = await get_router_service(router_id, db)
    success = service.add_dns_static(
        name=entry.name,
        record_type=entry.record_type,
        address=entry.address,
        cname=entry.cname,
        mx_exchange=entry.mx_exchange,
        mx_preference=entry.mx_preference,
        text=entry.text,
        ns=entry.ns,
        srv_target=entry.srv_target,
        srv_port=entry.srv_port,
        forward_to=entry.forward_to,
        ttl=entry.ttl,
        comment=entry.comment,
        disabled=entry.disabled
    )
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


@router.post("/dns/static/{entry_id}/toggle")
async def toggle_dns_entry(
    router_id: int,
    entry_id: str,
    enable: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """Enable or disable a DNS entry."""
    _, service = await get_router_service(router_id, db)
    success = service.toggle_dns_entry(entry_id, enable)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to toggle DNS entry")
    return {"success": True}


@router.post("/dns/cache/flush")
async def flush_dns_cache(router_id: int, db: AsyncSession = Depends(get_db)):
    """Flush DNS cache."""
    _, service = await get_router_service(router_id, db)
    success = service.flush_dns_cache()
    if not success:
        raise HTTPException(status_code=500, detail="Failed to flush DNS cache")
    return {"success": True}


@router.get("/dns/cache")
async def get_dns_cache(router_id: int, db: AsyncSession = Depends(get_db)):
    """Get DNS cache entries."""
    _, service = await get_router_service(router_id, db)
    return service.get_dns_cache()


@router.put("/dns/settings")
async def update_dns_settings(
    router_id: int,
    settings: DNSSettingsUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update DNS server settings."""
    _, service = await get_router_service(router_id, db)
    success = service.update_dns_settings(
        servers=settings.servers,
        allow_remote_requests=settings.allow_remote_requests,
        cache_size=settings.cache_size,
        cache_max_ttl=settings.cache_max_ttl,
        use_doh_server=settings.use_doh_server,
        verify_doh_cert=settings.verify_doh_cert
    )
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update DNS settings")
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
async def create_backup(
    router_id: int,
    name: str = None,
    password: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Create a backup on the router."""
    _, service = await get_router_service(router_id, db)
    filename = service.backup_config(name, password)
    if not filename:
        raise HTTPException(status_code=500, detail="Failed to create backup")
    return {"success": True, "filename": filename}


@router.get("/system/backups")
async def get_backup_files(router_id: int, db: AsyncSession = Depends(get_db)):
    """List backup files on the router."""
    _, service = await get_router_service(router_id, db)
    files = service.get_backup_files()
    return files


@router.get("/system/export")
async def export_config(router_id: int, db: AsyncSession = Depends(get_db)):
    """Export router configuration as text."""
    _, service = await get_router_service(router_id, db)
    config = service.export_config()
    if not config:
        raise HTTPException(status_code=500, detail="Failed to export configuration")
    return {"success": True, "config": config}


@router.get("/system/health")
async def get_system_health(router_id: int, db: AsyncSession = Depends(get_db)):
    """Get system health information."""
    _, service = await get_router_service(router_id, db)
    health = service.get_system_health()
    return health or {}
