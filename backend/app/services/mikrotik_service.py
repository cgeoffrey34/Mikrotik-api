import ssl
import socket
from typing import Optional, Dict, Any, List
from librouteros import connect
from librouteros.exceptions import TrapError, ConnectionClosed, FatalError
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


class MikrotikService:
    """Service for communicating with Mikrotik routers via their API."""

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        port: int = 8728,
        use_ssl: bool = False,
        timeout: int = 10
    ):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.use_ssl = use_ssl
        self.timeout = timeout
        self._api = None

    @contextmanager
    def _connection(self):
        """Context manager for API connection."""
        api = None
        try:
            if self.use_ssl:
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                api = connect(
                    host=self.host,
                    username=self.username,
                    password=self.password,
                    port=self.port,
                    ssl_wrapper=ssl_context.wrap_socket,
                    timeout=self.timeout
                )
            else:
                api = connect(
                    host=self.host,
                    username=self.username,
                    password=self.password,
                    port=self.port,
                    timeout=self.timeout
                )
            yield api
        except (TrapError, ConnectionClosed, FatalError, socket.error, OSError) as e:
            logger.error(f"Connection error to {self.host}: {e}")
            raise
        finally:
            if api:
                try:
                    api.close()
                except Exception:
                    pass

    def _safe_int(self, value, default=0) -> int:
        """Safely convert value to int."""
        if value is None:
            return default
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    def _parse_bytes(self, value: str, index: int) -> int:
        """Parse bytes from comma-separated string."""
        try:
            if not value:
                return 0
            parts = str(value).split(",")
            if len(parts) > index:
                return int(parts[index].strip())
            return 0
        except (ValueError, IndexError):
            return 0

    def test_connection(self) -> Dict[str, Any]:
        """Test connection and return router identity."""
        logger.info(f"Testing connection to {self.host}:{self.port} (SSL={self.use_ssl}, user={self.username})")
        try:
            with self._connection() as api:
                identity = list(api.path("/system/identity"))
                name = identity[0].get("name", "Unknown") if identity else "Unknown"
                logger.info(f"Successfully connected to {self.host}:{self.port} - Identity: {name}")
                return {
                    "success": True,
                    "identity": name
                }
        except Exception as e:
            logger.error(f"Failed to connect to {self.host}:{self.port} - {type(e).__name__}: {e}")
            return {"success": False, "error": str(e)}

    def get_system_resource(self) -> Optional[Dict[str, Any]]:
        """Get system resource information (CPU, RAM, disk, uptime)."""
        try:
            with self._connection() as api:
                resources = list(api.path("/system/resource"))
                if resources:
                    res = resources[0]
                    return {
                        "cpu_load": int(res.get("cpu-load", 0)),
                        "memory_used": int(res.get("total-memory", 0)) - int(res.get("free-memory", 0)),
                        "memory_total": int(res.get("total-memory", 0)),
                        "disk_used": int(res.get("total-hdd-space", 0)) - int(res.get("free-hdd-space", 0)),
                        "disk_total": int(res.get("total-hdd-space", 0)),
                        "uptime": res.get("uptime", ""),
                        "version": res.get("version", ""),
                        "board_name": res.get("board-name", ""),
                        "architecture": res.get("architecture-name", ""),
                        "cpu": res.get("cpu", ""),
                        "cpu_count": res.get("cpu-count", 1)
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting system resource: {e}")
            return None

    def get_system_identity(self) -> Optional[str]:
        """Get router identity/name."""
        try:
            with self._connection() as api:
                identity = list(api.path("/system/identity"))
                return identity[0].get("name") if identity else None
        except Exception as e:
            logger.error(f"Error getting identity: {e}")
            return None

    def get_routerboard_info(self) -> Optional[Dict[str, Any]]:
        """Get RouterBoard information (model, serial, firmware)."""
        try:
            with self._connection() as api:
                rb = list(api.path("/system/routerboard"))
                if rb:
                    info = rb[0]
                    return {
                        "model": info.get("model", ""),
                        "serial_number": info.get("serial-number", ""),
                        "firmware": info.get("current-firmware", ""),
                        "factory_firmware": info.get("factory-firmware", ""),
                        "upgrade_firmware": info.get("upgrade-firmware", "")
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting routerboard info: {e}")
            return None

    # ==================== DHCP ====================

    def get_dhcp_leases(self) -> List[Dict[str, Any]]:
        """Get all DHCP leases."""
        try:
            with self._connection() as api:
                leases = list(api.path("/ip/dhcp-server/lease"))
                return [
                    {
                        "id": lease.get(".id", ""),
                        "address": lease.get("address", ""),
                        "mac_address": lease.get("mac-address", ""),
                        "client_id": lease.get("client-id", ""),
                        "hostname": lease.get("host-name", ""),
                        "server": lease.get("server", ""),
                        "status": lease.get("status", ""),
                        "expires_after": lease.get("expires-after", ""),
                        "last_seen": lease.get("last-seen", ""),
                        "comment": lease.get("comment", ""),
                        "dynamic": lease.get("dynamic", "false") == "true"
                    }
                    for lease in leases
                ]
        except Exception as e:
            logger.error(f"Error getting DHCP leases: {e}")
            return []

    def add_dhcp_lease(self, address: str, mac_address: str, server: str = "default",
                       hostname: str = "", comment: str = "") -> bool:
        """Add a static DHCP lease."""
        try:
            with self._connection() as api:
                params = {
                    "address": address,
                    "mac-address": mac_address,
                    "server": server
                }
                if hostname:
                    params["host-name"] = hostname
                if comment:
                    params["comment"] = comment
                api.path("/ip/dhcp-server/lease").add(**params)
                return True
        except Exception as e:
            logger.error(f"Error adding DHCP lease: {e}")
            return False

    def delete_dhcp_lease(self, lease_id: str) -> bool:
        """Delete a DHCP lease."""
        try:
            with self._connection() as api:
                api.path("/ip/dhcp-server/lease").remove(lease_id)
                return True
        except Exception as e:
            logger.error(f"Error deleting DHCP lease: {e}")
            return False

    def make_dhcp_lease_static(self, lease_id: str) -> bool:
        """Make a dynamic DHCP lease static."""
        try:
            with self._connection() as api:
                api.path("/ip/dhcp-server/lease").call("make-static", {".id": lease_id})
                return True
        except Exception as e:
            logger.error(f"Error making lease static: {e}")
            return False

    def get_dhcp_servers(self) -> List[Dict[str, Any]]:
        """Get all DHCP servers."""
        try:
            with self._connection() as api:
                servers = list(api.path("/ip/dhcp-server"))
                return [
                    {
                        "id": srv.get(".id", ""),
                        "name": srv.get("name", ""),
                        "interface": srv.get("interface", ""),
                        "address_pool": srv.get("address-pool", ""),
                        "lease_time": srv.get("lease-time", ""),
                        "disabled": srv.get("disabled", "false") == "true",
                        "invalid": srv.get("invalid", "false") == "true",
                        "authoritative": srv.get("authoritative", ""),
                        "use_radius": srv.get("use-radius", "false") == "true"
                    }
                    for srv in servers
                ]
        except Exception as e:
            logger.error(f"Error getting DHCP servers: {e}")
            return []

    def get_dhcp_networks(self) -> List[Dict[str, Any]]:
        """Get all DHCP network configurations."""
        try:
            with self._connection() as api:
                networks = list(api.path("/ip/dhcp-server/network"))
                return [
                    {
                        "id": net.get(".id", ""),
                        "address": net.get("address", ""),
                        "gateway": net.get("gateway", ""),
                        "dns_server": net.get("dns-server", ""),
                        "domain": net.get("domain", ""),
                        "netmask": net.get("netmask", ""),
                        "ntp_server": net.get("ntp-server", ""),
                        "wins_server": net.get("wins-server", ""),
                        "comment": net.get("comment", "")
                    }
                    for net in networks
                ]
        except Exception as e:
            logger.error(f"Error getting DHCP networks: {e}")
            return []

    def get_ip_pools(self) -> List[Dict[str, Any]]:
        """Get all IP pools."""
        try:
            with self._connection() as api:
                pools = list(api.path("/ip/pool"))
                return [
                    {
                        "id": pool.get(".id", ""),
                        "name": pool.get("name", ""),
                        "ranges": pool.get("ranges", ""),
                        "next_pool": pool.get("next-pool", ""),
                        "comment": pool.get("comment", "")
                    }
                    for pool in pools
                ]
        except Exception as e:
            logger.error(f"Error getting IP pools: {e}")
            return []

    def toggle_dhcp_server(self, server_id: str, enable: bool) -> bool:
        """Enable or disable a DHCP server."""
        try:
            with self._connection() as api:
                api.path("/ip/dhcp-server").update(
                    **{".id": server_id, "disabled": "no" if enable else "yes"}
                )
                return True
        except Exception as e:
            logger.error(f"Error toggling DHCP server: {e}")
            return False

    # ==================== WiFi ====================

    def get_wifi_clients(self) -> List[Dict[str, Any]]:
        """Get all connected WiFi clients."""
        try:
            with self._connection() as api:
                registrations = []

                # Try standard wireless registration table
                try:
                    regs = list(api.path("/interface/wireless/registration-table"))
                    registrations.extend(regs)
                except Exception:
                    pass

                # Try CAPsMAN registration table
                try:
                    capsman = list(api.path("/caps-man/registration-table"))
                    registrations.extend(capsman)
                except Exception:
                    pass

                # Try WiFi (RouterOS 7.13+) registration table
                try:
                    wifi = list(api.path("/interface/wifi/registration-table"))
                    registrations.extend(wifi)
                except Exception:
                    pass

                return [
                    {
                        "interface": reg.get("interface", ""),
                        "mac_address": reg.get("mac-address", ""),
                        "signal_strength": reg.get("signal-strength", reg.get("signal", "")),
                        "tx_rate": reg.get("tx-rate", ""),
                        "rx_rate": reg.get("rx-rate", ""),
                        "uptime": reg.get("uptime", ""),
                        "bytes_sent": self._parse_bytes(reg.get("bytes", ""), 0),
                        "bytes_received": self._parse_bytes(reg.get("bytes", ""), 1),
                        "ssid": reg.get("ssid", "")
                    }
                    for reg in registrations
                ]
        except Exception as e:
            logger.error(f"Error getting WiFi clients: {e}")
            return []

    def get_wireless_interfaces(self) -> List[Dict[str, Any]]:
        """Get all wireless interfaces."""
        try:
            with self._connection() as api:
                interfaces = []

                # Try standard wireless
                try:
                    wireless = list(api.path("/interface/wireless"))
                    for iface in wireless:
                        interfaces.append({
                            "id": iface.get(".id", ""),
                            "name": iface.get("name", ""),
                            "mac_address": iface.get("mac-address", ""),
                            "ssid": iface.get("ssid", ""),
                            "mode": iface.get("mode", ""),
                            "band": iface.get("band", ""),
                            "channel_width": iface.get("channel-width", ""),
                            "frequency": iface.get("frequency", ""),
                            "security_profile": iface.get("security-profile", ""),
                            "disabled": iface.get("disabled", "false") == "true",
                            "running": iface.get("running", "false") == "true",
                            "interface_type": "wireless"
                        })
                except Exception as e:
                    logger.debug(f"No standard wireless: {e}")

                # Try WiFi (RouterOS 7.13+)
                try:
                    wifi = list(api.path("/interface/wifi"))
                    for iface in wifi:
                        interfaces.append({
                            "id": iface.get(".id", ""),
                            "name": iface.get("name", ""),
                            "mac_address": iface.get("mac-address", ""),
                            "ssid": iface.get("configuration.ssid", iface.get("ssid", "")),
                            "mode": iface.get("configuration.mode", iface.get("mode", "")),
                            "band": iface.get("configuration.band", ""),
                            "channel_width": iface.get("configuration.channel.width", ""),
                            "frequency": iface.get("configuration.channel.frequency", ""),
                            "security_profile": iface.get("security", ""),
                            "disabled": iface.get("disabled", "false") == "true",
                            "running": iface.get("running", "false") == "true",
                            "interface_type": "wifi"
                        })
                except Exception as e:
                    logger.debug(f"No WiFi interfaces: {e}")

                return interfaces
        except Exception as e:
            logger.error(f"Error getting wireless interfaces: {e}")
            return []

    def get_security_profiles(self) -> List[Dict[str, Any]]:
        """Get wireless security profiles."""
        try:
            with self._connection() as api:
                profiles = []

                # Try standard wireless security profiles
                try:
                    wireless_profiles = list(api.path("/interface/wireless/security-profiles"))
                    for profile in wireless_profiles:
                        profiles.append({
                            "id": profile.get(".id", ""),
                            "name": profile.get("name", ""),
                            "mode": profile.get("mode", ""),
                            "authentication_types": profile.get("authentication-types", ""),
                            "wpa_pre_shared_key": "****" if profile.get("wpa-pre-shared-key") else "",
                            "wpa2_pre_shared_key": "****" if profile.get("wpa2-pre-shared-key") else "",
                            "profile_type": "wireless"
                        })
                except Exception:
                    pass

                # Try WiFi security (RouterOS 7.13+)
                try:
                    wifi_security = list(api.path("/interface/wifi/security"))
                    for sec in wifi_security:
                        profiles.append({
                            "id": sec.get(".id", ""),
                            "name": sec.get("name", ""),
                            "mode": sec.get("authentication-types", ""),
                            "authentication_types": sec.get("authentication-types", ""),
                            "passphrase": "****" if sec.get("passphrase") else "",
                            "profile_type": "wifi"
                        })
                except Exception:
                    pass

                return profiles
        except Exception as e:
            logger.error(f"Error getting security profiles: {e}")
            return []

    def update_wireless_interface(self, interface_id: str, ssid: str = None,
                                   security_profile: str = None, disabled: bool = None) -> bool:
        """Update wireless interface settings."""
        try:
            with self._connection() as api:
                params = {".id": interface_id}
                if ssid is not None:
                    params["ssid"] = ssid
                if security_profile is not None:
                    params["security-profile"] = security_profile
                if disabled is not None:
                    params["disabled"] = "yes" if disabled else "no"
                api.path("/interface/wireless").update(**params)
                return True
        except Exception as e:
            logger.error(f"Error updating wireless interface: {e}")
            return False

    # ==================== Interfaces ====================

    def get_interfaces(self) -> List[Dict[str, Any]]:
        """Get all interfaces."""
        try:
            with self._connection() as api:
                interfaces = list(api.path("/interface"))
                result = []
                for iface in interfaces:
                    result.append({
                        "id": iface.get(".id", ""),
                        "name": iface.get("name", ""),
                        "default_name": iface.get("default-name", ""),
                        "type": iface.get("type", ""),
                        "mac_address": iface.get("mac-address", ""),
                        "mtu": self._safe_int(iface.get("actual-mtu", iface.get("mtu"))),
                        "l2mtu": self._safe_int(iface.get("l2mtu")),
                        "running": iface.get("running", "false") == "true",
                        "disabled": iface.get("disabled", "false") == "true",
                        "comment": iface.get("comment", ""),
                        "tx_bytes": self._safe_int(iface.get("tx-byte", 0)),
                        "rx_bytes": self._safe_int(iface.get("rx-byte", 0)),
                        "tx_packets": self._safe_int(iface.get("tx-packet", 0)),
                        "rx_packets": self._safe_int(iface.get("rx-packet", 0)),
                        "link_downs": self._safe_int(iface.get("link-downs", 0))
                    })
                return result
        except Exception as e:
            logger.error(f"Error getting interfaces: {e}")
            return []

    def toggle_interface(self, interface_id: str, enable: bool) -> bool:
        """Enable or disable an interface."""
        try:
            with self._connection() as api:
                api.path("/interface").update(
                    **{".id": interface_id, "disabled": "no" if enable else "yes"}
                )
                return True
        except Exception as e:
            logger.error(f"Error toggling interface: {e}")
            return False

    # ==================== Bridges ====================

    def get_bridges(self) -> List[Dict[str, Any]]:
        """Get all bridge interfaces."""
        try:
            with self._connection() as api:
                bridges = list(api.path("/interface/bridge"))
                return [
                    {
                        "id": br.get(".id", ""),
                        "name": br.get("name", ""),
                        "mac_address": br.get("mac-address", ""),
                        "mtu": self._safe_int(br.get("mtu", br.get("actual-mtu"))),
                        "protocol_mode": br.get("protocol-mode", ""),
                        "fast_forward": br.get("fast-forward", "false") == "true",
                        "igmp_snooping": br.get("igmp-snooping", "false") == "true",
                        "vlan_filtering": br.get("vlan-filtering", "false") == "true",
                        "admin_mac": br.get("admin-mac", ""),
                        "ageing_time": br.get("ageing-time", ""),
                        "arp": br.get("arp", ""),
                        "disabled": br.get("disabled", "false") == "true",
                        "running": br.get("running", "false") == "true",
                        "comment": br.get("comment", "")
                    }
                    for br in bridges
                ]
        except Exception as e:
            logger.error(f"Error getting bridges: {e}")
            return []

    def get_bridge_ports(self) -> List[Dict[str, Any]]:
        """Get all bridge ports."""
        try:
            with self._connection() as api:
                ports = list(api.path("/interface/bridge/port"))
                return [
                    {
                        "id": port.get(".id", ""),
                        "bridge": port.get("bridge", ""),
                        "interface": port.get("interface", ""),
                        "hw": port.get("hw", "false") == "true",
                        "pvid": self._safe_int(port.get("pvid", 1)),
                        "frame_types": port.get("frame-types", ""),
                        "ingress_filtering": port.get("ingress-filtering", "false") == "true",
                        "disabled": port.get("disabled", "false") == "true",
                        "inactive": port.get("inactive", "false") == "true",
                        "comment": port.get("comment", "")
                    }
                    for port in ports
                ]
        except Exception as e:
            logger.error(f"Error getting bridge ports: {e}")
            return []

    def get_bridge_vlans(self) -> List[Dict[str, Any]]:
        """Get bridge VLAN configurations."""
        try:
            with self._connection() as api:
                vlans = list(api.path("/interface/bridge/vlan"))
                return [
                    {
                        "id": vlan.get(".id", ""),
                        "bridge": vlan.get("bridge", ""),
                        "vlan_ids": vlan.get("vlan-ids", ""),
                        "tagged": vlan.get("tagged", ""),
                        "untagged": vlan.get("untagged", ""),
                        "disabled": vlan.get("disabled", "false") == "true",
                        "comment": vlan.get("comment", "")
                    }
                    for vlan in vlans
                ]
        except Exception as e:
            logger.error(f"Error getting bridge VLANs: {e}")
            return []

    def add_bridge(self, name: str, comment: str = "", vlan_filtering: bool = False) -> bool:
        """Add a new bridge."""
        try:
            with self._connection() as api:
                params = {"name": name}
                if comment:
                    params["comment"] = comment
                if vlan_filtering:
                    params["vlan-filtering"] = "yes"
                api.path("/interface/bridge").add(**params)
                return True
        except Exception as e:
            logger.error(f"Error adding bridge: {e}")
            return False

    def add_bridge_port(self, bridge: str, interface: str, pvid: int = 1, comment: str = "") -> bool:
        """Add an interface to a bridge."""
        try:
            with self._connection() as api:
                params = {
                    "bridge": bridge,
                    "interface": interface,
                    "pvid": str(pvid)
                }
                if comment:
                    params["comment"] = comment
                api.path("/interface/bridge/port").add(**params)
                return True
        except Exception as e:
            logger.error(f"Error adding bridge port: {e}")
            return False

    def delete_bridge_port(self, port_id: str) -> bool:
        """Remove an interface from a bridge."""
        try:
            with self._connection() as api:
                api.path("/interface/bridge/port").remove(port_id)
                return True
        except Exception as e:
            logger.error(f"Error deleting bridge port: {e}")
            return False

    def delete_bridge(self, bridge_id: str) -> bool:
        """Delete a bridge."""
        try:
            with self._connection() as api:
                api.path("/interface/bridge").remove(bridge_id)
                return True
        except Exception as e:
            logger.error(f"Error deleting bridge: {e}")
            return False

    # ==================== IP Addresses ====================

    def get_ip_addresses(self) -> List[Dict[str, Any]]:
        """Get all IP addresses."""
        try:
            with self._connection() as api:
                addresses = list(api.path("/ip/address"))
                return [
                    {
                        "id": addr.get(".id", ""),
                        "address": addr.get("address", ""),
                        "network": addr.get("network", ""),
                        "interface": addr.get("interface", ""),
                        "actual_interface": addr.get("actual-interface", ""),
                        "disabled": addr.get("disabled", "false") == "true",
                        "dynamic": addr.get("dynamic", "false") == "true",
                        "invalid": addr.get("invalid", "false") == "true",
                        "comment": addr.get("comment", "")
                    }
                    for addr in addresses
                ]
        except Exception as e:
            logger.error(f"Error getting IP addresses: {e}")
            return []

    def add_ip_address(self, address: str, interface: str, comment: str = "") -> bool:
        """Add an IP address."""
        try:
            with self._connection() as api:
                params = {"address": address, "interface": interface}
                if comment:
                    params["comment"] = comment
                api.path("/ip/address").add(**params)
                return True
        except Exception as e:
            logger.error(f"Error adding IP address: {e}")
            return False

    def delete_ip_address(self, address_id: str) -> bool:
        """Delete an IP address."""
        try:
            with self._connection() as api:
                api.path("/ip/address").remove(address_id)
                return True
        except Exception as e:
            logger.error(f"Error deleting IP address: {e}")
            return False

    # ==================== Routes ====================

    def _is_true(self, value) -> bool:
        """Check if a RouterOS API value is truthy (handles both bool and str)."""
        if isinstance(value, bool):
            return value
        return str(value).lower() == "true"

    def _safe_str(self, value, default="") -> str:
        """Safely convert a RouterOS API value to string (handles lists, ints, bools)."""
        if value is None:
            return default
        if isinstance(value, (list, tuple)):
            return ",".join(str(v) for v in value)
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)

    def get_routes(self) -> List[Dict[str, Any]]:
        """Get all routes."""
        try:
            with self._connection() as api:
                routes = list(api.path("/ip/route"))
                result = []
                if routes:
                    logger.info(f"Sample route raw data: {dict(routes[0])}")
                for route in routes:
                    is_static = self._is_true(route.get("static", False))
                    is_dynamic = self._is_true(route.get("dynamic", False))
                    is_connect = self._is_true(route.get("connect", False))
                    is_ospf = self._is_true(route.get("ospf", False))
                    is_bgp = self._is_true(route.get("bgp", False))
                    is_rip = self._is_true(route.get("rip", False))
                    is_dhcp = self._is_true(route.get("dhcp", False))
                    is_vpn = self._is_true(route.get("vpn", False))
                    is_modem = self._is_true(route.get("modem", False))

                    # Determine route type
                    gw_status = route.get("gateway-status", "").lower() if isinstance(route.get("gateway-status"), str) else ""
                    if is_connect:
                        route_type = "connected"
                    elif is_static:
                        route_type = "static"
                    elif is_ospf or "ospf" in gw_status:
                        route_type = "ospf"
                    elif is_bgp or "bgp" in gw_status:
                        route_type = "bgp"
                    elif is_rip or "rip" in gw_status:
                        route_type = "rip"
                    elif is_dhcp or "dhcp" in gw_status:
                        route_type = "dhcp"
                    elif is_vpn or "vpn" in gw_status:
                        route_type = "vpn"
                    elif is_modem:
                        route_type = "modem"
                    elif is_dynamic:
                        route_type = "dynamic"
                    else:
                        route_type = "other"

                    result.append({
                        "id": route.get(".id", ""),
                        "dst_address": route.get("dst-address", ""),
                        "gateway": route.get("gateway", ""),
                        "gateway_status": route.get("gateway-status", ""),
                        "distance": self._safe_int(route.get("distance", 0)),
                        "scope": self._safe_int(route.get("scope", 0)),
                        "interface": route.get("interface", ""),
                        "disabled": self._is_true(route.get("disabled", False)),
                        "dynamic": is_dynamic,
                        "static": is_static,
                        "connect": is_connect,
                        "active": self._is_true(route.get("active", False)),
                        "route_type": route_type,
                        "routing_table": route.get("routing-table", "main"),
                        "comment": route.get("comment", "")
                    })
                return result
        except Exception as e:
            logger.error(f"Error getting routes: {e}")
            return []

    def add_route(self, dst_address: str, gateway: str, distance: int = 1, comment: str = "") -> bool:
        """Add a static route."""
        try:
            with self._connection() as api:
                params = {
                    "dst-address": dst_address,
                    "gateway": gateway,
                    "distance": str(distance)
                }
                if comment:
                    params["comment"] = comment
                api.path("/ip/route").add(**params)
                return True
        except Exception as e:
            logger.error(f"Error adding route: {e}")
            return False

    def delete_route(self, route_id: str) -> bool:
        """Delete a route."""
        try:
            with self._connection() as api:
                api.path("/ip/route").remove(route_id)
                return True
        except Exception as e:
            logger.error(f"Error deleting route: {e}")
            return False

    # ==================== Firewall ====================

    def _parse_firewall_rule(self, rule: Dict) -> Dict[str, Any]:
        """Parse a single firewall filter rule from RouterOS API data."""
        return {
            "id": rule.get(".id", ""),
            "chain": self._safe_str(rule.get("chain")),
            "action": self._safe_str(rule.get("action")),
            "src_address": self._safe_str(rule.get("src-address")),
            "dst_address": self._safe_str(rule.get("dst-address")),
            "src_address_list": self._safe_str(rule.get("src-address-list")),
            "dst_address_list": self._safe_str(rule.get("dst-address-list")),
            "protocol": self._safe_str(rule.get("protocol")),
            "src_port": self._safe_str(rule.get("src-port")),
            "dst_port": self._safe_str(rule.get("dst-port")),
            "in_interface": self._safe_str(rule.get("in-interface")),
            "in_interface_list": self._safe_str(rule.get("in-interface-list")),
            "out_interface": self._safe_str(rule.get("out-interface")),
            "out_interface_list": self._safe_str(rule.get("out-interface-list")),
            "connection_state": self._safe_str(rule.get("connection-state")),
            "disabled": self._is_true(rule.get("disabled", False)),
            "invalid": self._is_true(rule.get("invalid", False)),
            "dynamic": self._is_true(rule.get("dynamic", False)),
            "comment": self._safe_str(rule.get("comment")),
            "bytes": self._safe_int(rule.get("bytes", 0)),
            "packets": self._safe_int(rule.get("packets", 0)),
            "log": self._is_true(rule.get("log", False)),
            "log_prefix": self._safe_str(rule.get("log-prefix")),
        }

    def get_firewall_filter_rules(self) -> List[Dict[str, Any]]:
        """Get all firewall filter rules."""
        try:
            with self._connection() as api:
                rules = list(api.path("/ip/firewall/filter"))
                if rules:
                    logger.info(f"Filter: {len(rules)} rules, sample raw: {dict(rules[0])}")
                result = []
                for rule in rules:
                    try:
                        result.append(self._parse_firewall_rule(rule))
                    except Exception as e:
                        logger.error(f"Error parsing filter rule {rule.get('.id', '?')}: {e} - raw: {dict(rule)}")
                return result
        except Exception as e:
            logger.error(f"Error getting firewall rules: {e}")
            return []

    def add_firewall_rule(self, chain: str, action: str, src_address: str = None,
                          dst_address: str = None, protocol: str = None,
                          src_port: str = None, dst_port: str = None,
                          in_interface: str = None, out_interface: str = None,
                          connection_state: str = None, comment: str = None,
                          disabled: bool = False) -> bool:
        """Add a firewall filter rule."""
        try:
            with self._connection() as api:
                params = {"chain": chain, "action": action}
                if src_address:
                    params["src-address"] = src_address
                if dst_address:
                    params["dst-address"] = dst_address
                if protocol:
                    params["protocol"] = protocol
                if src_port:
                    params["src-port"] = src_port
                if dst_port:
                    params["dst-port"] = dst_port
                if in_interface:
                    params["in-interface"] = in_interface
                if out_interface:
                    params["out-interface"] = out_interface
                if connection_state:
                    params["connection-state"] = connection_state
                if comment:
                    params["comment"] = comment
                if disabled:
                    params["disabled"] = "yes"
                api.path("/ip/firewall/filter").add(**params)
                return True
        except Exception as e:
            logger.error(f"Error adding firewall rule: {e}")
            return False

    def delete_firewall_rule(self, rule_id: str) -> bool:
        """Delete a firewall filter rule."""
        try:
            with self._connection() as api:
                api.path("/ip/firewall/filter").remove(rule_id)
                return True
        except Exception as e:
            logger.error(f"Error deleting firewall rule: {e}")
            return False

    def toggle_firewall_rule(self, rule_id: str, enable: bool) -> bool:
        """Enable or disable a firewall rule."""
        try:
            with self._connection() as api:
                api.path("/ip/firewall/filter").update(
                    **{".id": rule_id, "disabled": "no" if enable else "yes"}
                )
                return True
        except Exception as e:
            logger.error(f"Error toggling firewall rule: {e}")
            return False

    def get_nat_rules(self) -> List[Dict[str, Any]]:
        """Get all NAT rules."""
        try:
            with self._connection() as api:
                rules = list(api.path("/ip/firewall/nat"))
                if rules:
                    logger.info(f"NAT: {len(rules)} rules, sample raw: {dict(rules[0])}")
                result = []
                for rule in rules:
                    try:
                        result.append({
                            "id": rule.get(".id", ""),
                            "chain": self._safe_str(rule.get("chain")),
                            "action": self._safe_str(rule.get("action")),
                            "src_address": self._safe_str(rule.get("src-address")),
                            "dst_address": self._safe_str(rule.get("dst-address")),
                            "protocol": self._safe_str(rule.get("protocol")),
                            "src_port": self._safe_str(rule.get("src-port")),
                            "dst_port": self._safe_str(rule.get("dst-port")),
                            "to_addresses": self._safe_str(rule.get("to-addresses")),
                            "to_ports": self._safe_str(rule.get("to-ports")),
                            "in_interface": self._safe_str(rule.get("in-interface")),
                            "in_interface_list": self._safe_str(rule.get("in-interface-list")),
                            "out_interface": self._safe_str(rule.get("out-interface")),
                            "out_interface_list": self._safe_str(rule.get("out-interface-list")),
                            "disabled": self._is_true(rule.get("disabled", False)),
                            "invalid": self._is_true(rule.get("invalid", False)),
                            "dynamic": self._is_true(rule.get("dynamic", False)),
                            "comment": self._safe_str(rule.get("comment")),
                            "bytes": self._safe_int(rule.get("bytes", 0)),
                            "packets": self._safe_int(rule.get("packets", 0)),
                        })
                    except Exception as e:
                        logger.error(f"Error parsing NAT rule {rule.get('.id', '?')}: {e} - raw: {dict(rule)}")
                return result
        except Exception as e:
            logger.error(f"Error getting NAT rules: {e}")
            return []

    def add_nat_rule(self, chain: str, action: str, src_address: str = None,
                     dst_address: str = None, protocol: str = None,
                     src_port: str = None, dst_port: str = None,
                     to_addresses: str = None, to_ports: str = None,
                     in_interface: str = None, out_interface: str = None,
                     comment: str = None, disabled: bool = False) -> bool:
        """Add a NAT rule."""
        try:
            with self._connection() as api:
                params = {"chain": chain, "action": action}
                if src_address:
                    params["src-address"] = src_address
                if dst_address:
                    params["dst-address"] = dst_address
                if protocol:
                    params["protocol"] = protocol
                if src_port:
                    params["src-port"] = src_port
                if dst_port:
                    params["dst-port"] = dst_port
                if to_addresses:
                    params["to-addresses"] = to_addresses
                if to_ports:
                    params["to-ports"] = to_ports
                if in_interface:
                    params["in-interface"] = in_interface
                if out_interface:
                    params["out-interface"] = out_interface
                if comment:
                    params["comment"] = comment
                if disabled:
                    params["disabled"] = "yes"
                api.path("/ip/firewall/nat").add(**params)
                return True
        except Exception as e:
            logger.error(f"Error adding NAT rule: {e}")
            return False

    def delete_nat_rule(self, rule_id: str) -> bool:
        """Delete a NAT rule."""
        try:
            with self._connection() as api:
                api.path("/ip/firewall/nat").remove(rule_id)
                return True
        except Exception as e:
            logger.error(f"Error deleting NAT rule: {e}")
            return False

    def toggle_nat_rule(self, rule_id: str, enable: bool) -> bool:
        """Enable or disable a NAT rule."""
        try:
            with self._connection() as api:
                api.path("/ip/firewall/nat").update(
                    **{".id": rule_id, "disabled": "no" if enable else "yes"}
                )
                return True
        except Exception as e:
            logger.error(f"Error toggling NAT rule: {e}")
            return False

    # ==================== Mangle ====================

    def get_mangle_rules(self) -> List[Dict[str, Any]]:
        """Get all mangle rules."""
        try:
            with self._connection() as api:
                rules = list(api.path("/ip/firewall/mangle"))
                if rules:
                    logger.info(f"Mangle: {len(rules)} rules, sample raw: {dict(rules[0])}")
                result = []
                for r in rules:
                    try:
                        result.append({
                            "id": r.get(".id", ""),
                            "chain": self._safe_str(r.get("chain")),
                            "action": self._safe_str(r.get("action")),
                            "src_address": self._safe_str(r.get("src-address")),
                            "dst_address": self._safe_str(r.get("dst-address")),
                            "src_address_list": self._safe_str(r.get("src-address-list")),
                            "dst_address_list": self._safe_str(r.get("dst-address-list")),
                            "protocol": self._safe_str(r.get("protocol")),
                            "src_port": self._safe_str(r.get("src-port")),
                            "dst_port": self._safe_str(r.get("dst-port")),
                            "in_interface": self._safe_str(r.get("in-interface")),
                            "in_interface_list": self._safe_str(r.get("in-interface-list")),
                            "out_interface": self._safe_str(r.get("out-interface")),
                            "out_interface_list": self._safe_str(r.get("out-interface-list")),
                            "connection_state": self._safe_str(r.get("connection-state")),
                            "new_packet_mark": self._safe_str(r.get("new-packet-mark")),
                            "new_connection_mark": self._safe_str(r.get("new-connection-mark")),
                            "new_routing_mark": self._safe_str(r.get("new-routing-mark")),
                            "passthrough": self._is_true(r.get("passthrough", True)),
                            "disabled": self._is_true(r.get("disabled", False)),
                            "invalid": self._is_true(r.get("invalid", False)),
                            "dynamic": self._is_true(r.get("dynamic", False)),
                            "comment": self._safe_str(r.get("comment")),
                            "bytes": self._safe_int(r.get("bytes", 0)),
                            "packets": self._safe_int(r.get("packets", 0)),
                            "log": self._is_true(r.get("log", False)),
                            "log_prefix": self._safe_str(r.get("log-prefix")),
                            "connection_mark": self._safe_str(r.get("connection-mark")),
                            "packet_mark": self._safe_str(r.get("packet-mark")),
                            "routing_mark": self._safe_str(r.get("routing-mark")),
                        })
                    except Exception as e:
                        logger.error(f"Error parsing mangle rule {r.get('.id', '?')}: {e}")
                return result
        except Exception as e:
            logger.error(f"Error getting mangle rules: {e}")
            return []

    def add_mangle_rule(self, **kwargs) -> bool:
        """Add a mangle rule."""
        try:
            with self._connection() as api:
                params = {}
                field_map = {
                    "chain": "chain", "action": "action",
                    "src_address": "src-address", "dst_address": "dst-address",
                    "src_address_list": "src-address-list", "dst_address_list": "dst-address-list",
                    "protocol": "protocol", "src_port": "src-port", "dst_port": "dst-port",
                    "in_interface": "in-interface", "out_interface": "out-interface",
                    "connection_state": "connection-state",
                    "new_packet_mark": "new-packet-mark",
                    "new_connection_mark": "new-connection-mark",
                    "new_routing_mark": "new-routing-mark",
                    "passthrough": "passthrough",
                    "comment": "comment",
                }
                for py_key, ros_key in field_map.items():
                    val = kwargs.get(py_key)
                    if val is not None and val != "":
                        if isinstance(val, bool):
                            params[ros_key] = "yes" if val else "no"
                        else:
                            params[ros_key] = str(val)
                if kwargs.get("disabled"):
                    params["disabled"] = "yes"
                api.path("/ip/firewall/mangle").add(**params)
                return True
        except Exception as e:
            logger.error(f"Error adding mangle rule: {e}")
            return False

    def delete_mangle_rule(self, rule_id: str) -> bool:
        """Delete a mangle rule."""
        try:
            with self._connection() as api:
                api.path("/ip/firewall/mangle").remove(rule_id)
                return True
        except Exception as e:
            logger.error(f"Error deleting mangle rule: {e}")
            return False

    def toggle_mangle_rule(self, rule_id: str, enable: bool) -> bool:
        """Enable or disable a mangle rule."""
        try:
            with self._connection() as api:
                api.path("/ip/firewall/mangle").update(
                    **{".id": rule_id, "disabled": "no" if enable else "yes"}
                )
                return True
        except Exception as e:
            logger.error(f"Error toggling mangle rule: {e}")
            return False

    # ==================== RAW ====================

    def get_raw_rules(self) -> List[Dict[str, Any]]:
        """Get all RAW firewall rules."""
        try:
            with self._connection() as api:
                rules = list(api.path("/ip/firewall/raw"))
                if rules:
                    logger.info(f"RAW: {len(rules)} rules, sample raw: {dict(rules[0])}")
                result = []
                for r in rules:
                    try:
                        result.append({
                            "id": r.get(".id", ""),
                            "chain": self._safe_str(r.get("chain")),
                            "action": self._safe_str(r.get("action")),
                            "src_address": self._safe_str(r.get("src-address")),
                            "dst_address": self._safe_str(r.get("dst-address")),
                            "src_address_list": self._safe_str(r.get("src-address-list")),
                            "dst_address_list": self._safe_str(r.get("dst-address-list")),
                            "protocol": self._safe_str(r.get("protocol")),
                            "src_port": self._safe_str(r.get("src-port")),
                            "dst_port": self._safe_str(r.get("dst-port")),
                            "in_interface": self._safe_str(r.get("in-interface")),
                            "in_interface_list": self._safe_str(r.get("in-interface-list")),
                            "out_interface": self._safe_str(r.get("out-interface")),
                            "out_interface_list": self._safe_str(r.get("out-interface-list")),
                            "connection_state": self._safe_str(r.get("connection-state")),
                            "disabled": self._is_true(r.get("disabled", False)),
                            "invalid": self._is_true(r.get("invalid", False)),
                            "dynamic": self._is_true(r.get("dynamic", False)),
                            "comment": self._safe_str(r.get("comment")),
                            "bytes": self._safe_int(r.get("bytes", 0)),
                            "packets": self._safe_int(r.get("packets", 0)),
                            "log": self._is_true(r.get("log", False)),
                            "log_prefix": self._safe_str(r.get("log-prefix")),
                        })
                    except Exception as e:
                        logger.error(f"Error parsing RAW rule {r.get('.id', '?')}: {e}")
                return result
        except Exception as e:
            logger.error(f"Error getting RAW rules: {e}")
            return []

    def add_raw_rule(self, **kwargs) -> bool:
        """Add a RAW firewall rule."""
        try:
            with self._connection() as api:
                params = {}
                field_map = {
                    "chain": "chain", "action": "action",
                    "src_address": "src-address", "dst_address": "dst-address",
                    "src_address_list": "src-address-list", "dst_address_list": "dst-address-list",
                    "protocol": "protocol", "src_port": "src-port", "dst_port": "dst-port",
                    "in_interface": "in-interface", "out_interface": "out-interface",
                    "connection_state": "connection-state",
                    "comment": "comment",
                }
                for py_key, ros_key in field_map.items():
                    val = kwargs.get(py_key)
                    if val is not None and val != "":
                        params[ros_key] = str(val)
                if kwargs.get("disabled"):
                    params["disabled"] = "yes"
                api.path("/ip/firewall/raw").add(**params)
                return True
        except Exception as e:
            logger.error(f"Error adding RAW rule: {e}")
            return False

    def delete_raw_rule(self, rule_id: str) -> bool:
        """Delete a RAW firewall rule."""
        try:
            with self._connection() as api:
                api.path("/ip/firewall/raw").remove(rule_id)
                return True
        except Exception as e:
            logger.error(f"Error deleting RAW rule: {e}")
            return False

    def toggle_raw_rule(self, rule_id: str, enable: bool) -> bool:
        """Enable or disable a RAW rule."""
        try:
            with self._connection() as api:
                api.path("/ip/firewall/raw").update(
                    **{".id": rule_id, "disabled": "no" if enable else "yes"}
                )
                return True
        except Exception as e:
            logger.error(f"Error toggling RAW rule: {e}")
            return False

    # ==================== Service Ports ====================

    def get_service_ports(self) -> List[Dict[str, Any]]:
        """Get all firewall service ports (ALG helpers)."""
        try:
            with self._connection() as api:
                ports = list(api.path("/ip/firewall/service-port"))
                logger.info(f"Service ports: {len(ports)} entries")
                if ports:
                    logger.info(f"Service port sample raw: {dict(ports[0])}")
                result = []
                for p in ports:
                    try:
                        result.append({
                            "id": p.get(".id", ""),
                            "name": self._safe_str(p.get("name")),
                            "ports": self._safe_str(p.get("ports")),
                            "disabled": self._is_true(p.get("disabled", False)),
                            "invalid": self._is_true(p.get("invalid", False)),
                        })
                    except Exception as e:
                        logger.error(f"Error parsing service port {p.get('.id', '?')}: {e}")
                return result
        except Exception as e:
            logger.error(f"Error getting service ports: {e}")
            return []

    def toggle_service_port(self, port_id: str, enable: bool) -> bool:
        """Enable or disable a service port."""
        try:
            with self._connection() as api:
                api.path("/ip/firewall/service-port").update(
                    **{".id": port_id, "disabled": "no" if enable else "yes"}
                )
                return True
        except Exception as e:
            logger.error(f"Error toggling service port: {e}")
            return False

    # ==================== Connections ====================

    def get_connections(self) -> List[Dict[str, Any]]:
        """Get all active firewall connections."""
        try:
            with self._connection() as api:
                conns = list(api.path("/ip/firewall/connection"))
                result = []
                for c in conns:
                    try:
                        result.append({
                            "id": c.get(".id", ""),
                            "protocol": self._safe_str(c.get("protocol")),
                            "src_address": self._safe_str(c.get("src-address")),
                            "dst_address": self._safe_str(c.get("dst-address")),
                            "reply_src_address": self._safe_str(c.get("reply-src-address")),
                            "reply_dst_address": self._safe_str(c.get("reply-dst-address")),
                            "tcp_state": self._safe_str(c.get("tcp-state")),
                            "timeout": self._safe_str(c.get("timeout")),
                            "connection_mark": self._safe_str(c.get("connection-mark")),
                            "assured": self._is_true(c.get("assured", False)),
                            "confirmed": self._is_true(c.get("confirmed", False)),
                            "dying": self._is_true(c.get("dying", False)),
                            "fasttrack": self._is_true(c.get("fasttrack", False)),
                            "orig_bytes": self._safe_int(c.get("orig-bytes", 0)),
                            "repl_bytes": self._safe_int(c.get("repl-bytes", 0)),
                            "orig_packets": self._safe_int(c.get("orig-packets", 0)),
                            "repl_packets": self._safe_int(c.get("repl-packets", 0)),
                        })
                    except Exception as e:
                        logger.error(f"Error parsing connection {c.get('.id', '?')}: {e}")
                return result
        except Exception as e:
            logger.error(f"Error getting connections: {e}")
            return []

    def remove_connection(self, conn_id: str) -> bool:
        """Remove a connection from the connection table."""
        try:
            with self._connection() as api:
                api.path("/ip/firewall/connection").remove(conn_id)
                return True
        except Exception as e:
            logger.error(f"Error removing connection: {e}")
            return False

    # ==================== Address Lists ====================

    def get_address_lists(self) -> List[Dict[str, Any]]:
        """Get all firewall address list entries."""
        try:
            with self._connection() as api:
                entries = list(api.path("/ip/firewall/address-list"))
                result = []
                for e in entries:
                    try:
                        result.append({
                            "id": e.get(".id", ""),
                            "list": self._safe_str(e.get("list")),
                            "address": self._safe_str(e.get("address")),
                            "timeout": self._safe_str(e.get("timeout")),
                            "creation_time": self._safe_str(e.get("creation-time")),
                            "disabled": self._is_true(e.get("disabled", False)),
                            "dynamic": self._is_true(e.get("dynamic", False)),
                            "comment": self._safe_str(e.get("comment")),
                        })
                    except Exception as ex:
                        logger.error(f"Error parsing address list entry {e.get('.id', '?')}: {ex}")
                return result
        except Exception as e:
            logger.error(f"Error getting address lists: {e}")
            return []

    def add_address_list_entry(self, list_name: str, address: str, timeout: str = "", comment: str = "", disabled: bool = False) -> bool:
        """Add an entry to a firewall address list."""
        try:
            with self._connection() as api:
                params = {
                    "list": list_name,
                    "address": address,
                }
                if timeout:
                    params["timeout"] = timeout
                if comment:
                    params["comment"] = comment
                if disabled:
                    params["disabled"] = "yes"
                api.path("/ip/firewall/address-list").add(**params)
                return True
        except Exception as e:
            logger.error(f"Error adding address list entry: {e}")
            return False

    def delete_address_list_entry(self, entry_id: str) -> bool:
        """Delete an address list entry."""
        try:
            with self._connection() as api:
                api.path("/ip/firewall/address-list").remove(entry_id)
                return True
        except Exception as e:
            logger.error(f"Error deleting address list entry: {e}")
            return False

    def toggle_address_list_entry(self, entry_id: str, enable: bool) -> bool:
        """Enable or disable an address list entry."""
        try:
            with self._connection() as api:
                api.path("/ip/firewall/address-list").update(
                    **{".id": entry_id, "disabled": "no" if enable else "yes"}
                )
                return True
        except Exception as e:
            logger.error(f"Error toggling address list entry: {e}")
            return False

    # ==================== DNS ====================

    def get_dns_settings(self) -> Optional[Dict[str, Any]]:
        """Get DNS server settings."""
        try:
            with self._connection() as api:
                dns = list(api.path("/ip/dns"))
                if dns:
                    d = dns[0]
                    return {
                        "servers": d.get("servers", ""),
                        "dynamic_servers": d.get("dynamic-servers", ""),
                        "allow_remote_requests": d.get("allow-remote-requests", "false") == "true",
                        "cache_size": self._safe_int(d.get("cache-size", 2048)),
                        "cache_max_ttl": d.get("cache-max-ttl", ""),
                        "cache_used": self._safe_int(d.get("cache-used", 0))
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting DNS settings: {e}")
            return None

    def get_dns_static(self) -> List[Dict[str, Any]]:
        """Get static DNS entries."""
        try:
            with self._connection() as api:
                entries = list(api.path("/ip/dns/static"))
                return [
                    {
                        "id": entry.get(".id", ""),
                        "name": entry.get("name", entry.get("regexp", "")),
                        "address": entry.get("address", ""),
                        "cname": entry.get("cname", ""),
                        "mx_exchange": entry.get("mx-exchange", ""),
                        "mx_preference": entry.get("mx-preference", ""),
                        "srv_target": entry.get("srv-target", ""),
                        "srv_port": entry.get("srv-port", ""),
                        "text": entry.get("text", ""),
                        "ns": entry.get("ns", ""),
                        "type": entry.get("type", "A"),
                        "ttl": entry.get("ttl", "1d"),
                        "disabled": entry.get("disabled", "false") == "true",
                        "dynamic": entry.get("dynamic", "false") == "true",
                        "regexp": entry.get("regexp", ""),
                        "forward_to": entry.get("forward-to", ""),
                        "comment": entry.get("comment", "")
                    }
                    for entry in entries
                ]
        except Exception as e:
            logger.error(f"Error getting DNS entries: {e}")
            return []

    def add_dns_static(self, name: str, record_type: str = "A", address: str = None,
                       cname: str = None, mx_exchange: str = None, mx_preference: int = None,
                       text: str = None, ns: str = None, srv_target: str = None,
                       srv_port: int = None, forward_to: str = None,
                       ttl: str = "1d", comment: str = "", disabled: bool = False) -> bool:
        """Add a static DNS entry with support for all record types."""
        try:
            with self._connection() as api:
                params = {"name": name, "ttl": ttl}

                if record_type == "A":
                    if address:
                        params["address"] = address
                    params["type"] = "A"
                elif record_type == "AAAA":
                    if address:
                        params["address"] = address
                    params["type"] = "AAAA"
                elif record_type == "CNAME":
                    if cname:
                        params["cname"] = cname
                    params["type"] = "CNAME"
                elif record_type == "MX":
                    if mx_exchange:
                        params["mx-exchange"] = mx_exchange
                    if mx_preference is not None:
                        params["mx-preference"] = str(mx_preference)
                    params["type"] = "MX"
                elif record_type == "TXT":
                    if text:
                        params["text"] = text
                    params["type"] = "TXT"
                elif record_type == "NS":
                    if ns:
                        params["ns"] = ns
                    params["type"] = "NS"
                elif record_type == "SRV":
                    if srv_target:
                        params["srv-target"] = srv_target
                    if srv_port is not None:
                        params["srv-port"] = str(srv_port)
                    params["type"] = "SRV"
                elif record_type == "NXDOMAIN":
                    params["type"] = "NXDOMAIN"
                elif record_type == "FWD":
                    if forward_to:
                        params["forward-to"] = forward_to
                    params["type"] = "FWD"
                else:
                    if address:
                        params["address"] = address

                if comment:
                    params["comment"] = comment
                if disabled:
                    params["disabled"] = "yes"

                api.path("/ip/dns/static").add(**params)
                return True
        except Exception as e:
            logger.error(f"Error adding DNS entry: {e}")
            return False

    def delete_dns_static(self, entry_id: str) -> bool:
        """Delete a static DNS entry."""
        try:
            with self._connection() as api:
                api.path("/ip/dns/static").remove(entry_id)
                return True
        except Exception as e:
            logger.error(f"Error deleting DNS entry: {e}")
            return False

    def toggle_dns_entry(self, entry_id: str, enable: bool) -> bool:
        """Enable or disable a DNS entry."""
        try:
            with self._connection() as api:
                api.path("/ip/dns/static").update(
                    **{".id": entry_id, "disabled": "no" if enable else "yes"}
                )
                return True
        except Exception as e:
            logger.error(f"Error toggling DNS entry: {e}")
            return False

    def flush_dns_cache(self) -> bool:
        """Flush DNS cache."""
        try:
            with self._connection() as api:
                cache_path = api.path("/ip/dns/cache")
                tuple(cache_path("flush"))
                return True
        except Exception as e:
            logger.error(f"Error flushing DNS cache: {e}")
            return False

    # ==================== Queues (QoS) ====================

    def get_simple_queues(self) -> List[Dict[str, Any]]:
        """Get simple queue rules."""
        try:
            with self._connection() as api:
                queues = list(api.path("/queue/simple"))
                return [
                    {
                        "id": queue.get(".id", ""),
                        "name": queue.get("name", ""),
                        "target": queue.get("target", ""),
                        "parent": queue.get("parent", ""),
                        "max_limit": queue.get("max-limit", ""),
                        "limit_at": queue.get("limit-at", ""),
                        "burst_limit": queue.get("burst-limit", ""),
                        "burst_threshold": queue.get("burst-threshold", ""),
                        "burst_time": queue.get("burst-time", ""),
                        "priority": self._safe_int(queue.get("priority", "8").split("/")[0]),
                        "disabled": queue.get("disabled", "false") == "true",
                        "invalid": queue.get("invalid", "false") == "true",
                        "comment": queue.get("comment", ""),
                        "bytes": self._safe_int(queue.get("bytes", 0)),
                        "packets": self._safe_int(queue.get("packets", 0)),
                        "rate": queue.get("rate", "")
                    }
                    for queue in queues
                ]
        except Exception as e:
            logger.error(f"Error getting queues: {e}")
            return []

    def toggle_queue(self, queue_id: str, enable: bool) -> bool:
        """Enable or disable a queue."""
        try:
            with self._connection() as api:
                api.path("/queue/simple").update(
                    **{".id": queue_id, "disabled": "no" if enable else "yes"}
                )
                return True
        except Exception as e:
            logger.error(f"Error toggling queue: {e}")
            return False

    # ==================== System ====================

    def get_active_connections(self) -> int:
        """Get number of active connections (connection tracking)."""
        try:
            with self._connection() as api:
                connections = list(api.path("/ip/firewall/connection"))
                return len(connections)
        except Exception as e:
            logger.error(f"Error getting connections: {e}")
            return 0

    def reboot(self) -> bool:
        """Reboot the router."""
        try:
            with self._connection() as api:
                system_path = api.path("/system")
                tuple(system_path("reboot"))
                return True
        except Exception as e:
            # Connection will be closed during reboot, this is expected
            if "connection" in str(e).lower() or "closed" in str(e).lower():
                return True
            logger.error(f"Error rebooting: {e}")
            return False

    def get_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get system logs."""
        try:
            with self._connection() as api:
                logs = list(api.path("/log"))
                return [
                    {
                        "id": log.get(".id", ""),
                        "time": log.get("time", ""),
                        "topics": log.get("topics", ""),
                        "message": log.get("message", "")
                    }
                    for log in logs[-limit:]
                ]
        except Exception as e:
            logger.error(f"Error getting logs: {e}")
            return []

    def get_users(self) -> List[Dict[str, Any]]:
        """Get system users."""
        try:
            with self._connection() as api:
                users = list(api.path("/user"))
                return [
                    {
                        "id": user.get(".id", ""),
                        "name": user.get("name", ""),
                        "group": user.get("group", ""),
                        "address": user.get("address", ""),
                        "last_logged_in": user.get("last-logged-in", ""),
                        "disabled": user.get("disabled", "false") == "true",
                        "comment": user.get("comment", "")
                    }
                    for user in users
                ]
        except Exception as e:
            logger.error(f"Error getting users: {e}")
            return []

    def backup_config(self, name: str = None, password: str = None) -> Optional[str]:
        """Create a backup and return the file name."""
        try:
            with self._connection() as api:
                import time
                if not name:
                    name = f"backup-{int(time.time())}"

                params = {"name": name}
                if password:
                    params["password"] = password

                backup_path = api.path("/system/backup")
                tuple(backup_path("save", **params))

                return f"{name}.backup"
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None

    def get_backup_files(self) -> List[Dict[str, Any]]:
        """List backup files on the router."""
        try:
            with self._connection() as api:
                files = list(api.path("/file"))
                return [
                    {
                        "name": f.get("name", ""),
                        "size": self._safe_int(f.get("size", 0)),
                        "creation_time": f.get("creation-time", "")
                    }
                    for f in files
                    if f.get("name", "").endswith(".backup") or f.get("name", "").endswith(".rsc")
                ]
        except Exception as e:
            logger.error(f"Error getting backup files: {e}")
            return []

    def export_config(self) -> Optional[str]:
        """Export configuration as text."""
        try:
            with self._connection() as api:
                config_parts = []

                # System identity
                try:
                    identity = list(api.path("/system/identity"))
                    if identity:
                        config_parts.append(f"# System Identity: {identity[0].get('name', 'Unknown')}")
                        config_parts.append(f"/system identity set name=\"{identity[0].get('name', '')}\"")
                except Exception:
                    pass

                # IP addresses
                try:
                    addresses = list(api.path("/ip/address"))
                    if addresses:
                        config_parts.append("\n# IP Addresses")
                        for addr in addresses:
                            if addr.get("dynamic", "false") != "true":
                                line = f"/ip address add address={addr.get('address')} interface={addr.get('interface')}"
                                if addr.get("comment"):
                                    line += f' comment="{addr.get("comment")}"'
                                config_parts.append(line)
                except Exception:
                    pass

                # DHCP servers
                try:
                    dhcp = list(api.path("/ip/dhcp-server"))
                    if dhcp:
                        config_parts.append("\n# DHCP Servers")
                        for srv in dhcp:
                            line = f"/ip dhcp-server add name={srv.get('name')} interface={srv.get('interface')} address-pool={srv.get('address-pool')}"
                            if srv.get("lease-time"):
                                line += f" lease-time={srv.get('lease-time')}"
                            config_parts.append(line)
                except Exception:
                    pass

                # Firewall filter
                try:
                    rules = list(api.path("/ip/firewall/filter"))
                    if rules:
                        config_parts.append("\n# Firewall Filter Rules")
                        for rule in rules:
                            if rule.get("dynamic", "false") != "true":
                                line = f"/ip firewall filter add chain={rule.get('chain')} action={rule.get('action')}"
                                if rule.get("protocol"):
                                    line += f" protocol={rule.get('protocol')}"
                                if rule.get("dst-port"):
                                    line += f" dst-port={rule.get('dst-port')}"
                                if rule.get("src-address"):
                                    line += f" src-address={rule.get('src-address')}"
                                if rule.get("dst-address"):
                                    line += f" dst-address={rule.get('dst-address')}"
                                if rule.get("comment"):
                                    line += f' comment="{rule.get("comment")}"'
                                config_parts.append(line)
                except Exception:
                    pass

                # NAT rules
                try:
                    nat = list(api.path("/ip/firewall/nat"))
                    if nat:
                        config_parts.append("\n# NAT Rules")
                        for rule in nat:
                            if rule.get("dynamic", "false") != "true":
                                line = f"/ip firewall nat add chain={rule.get('chain')} action={rule.get('action')}"
                                if rule.get("out-interface"):
                                    line += f" out-interface={rule.get('out-interface')}"
                                if rule.get("src-address"):
                                    line += f" src-address={rule.get('src-address')}"
                                if rule.get("to-addresses"):
                                    line += f" to-addresses={rule.get('to-addresses')}"
                                if rule.get("comment"):
                                    line += f' comment="{rule.get("comment")}"'
                                config_parts.append(line)
                except Exception:
                    pass

                # Bridges
                try:
                    bridges = list(api.path("/interface/bridge"))
                    if bridges:
                        config_parts.append("\n# Bridges")
                        for br in bridges:
                            line = f"/interface bridge add name={br.get('name')}"
                            if br.get("vlan-filtering", "false") == "true":
                                line += " vlan-filtering=yes"
                            if br.get("comment"):
                                line += f' comment="{br.get("comment")}"'
                            config_parts.append(line)
                except Exception:
                    pass

                # Bridge ports
                try:
                    ports = list(api.path("/interface/bridge/port"))
                    if ports:
                        config_parts.append("\n# Bridge Ports")
                        for port in ports:
                            line = f"/interface bridge port add bridge={port.get('bridge')} interface={port.get('interface')}"
                            config_parts.append(line)
                except Exception:
                    pass

                # Static routes
                try:
                    routes = list(api.path("/ip/route"))
                    static_routes = [r for r in routes if r.get("static", "false") == "true"]
                    if static_routes:
                        config_parts.append("\n# Static Routes")
                        for route in static_routes:
                            line = f"/ip route add dst-address={route.get('dst-address')} gateway={route.get('gateway')}"
                            if route.get("comment"):
                                line += f' comment="{route.get("comment")}"'
                            config_parts.append(line)
                except Exception:
                    pass

                # DNS static entries
                try:
                    dns = list(api.path("/ip/dns/static"))
                    if dns:
                        config_parts.append("\n# DNS Static Entries")
                        for entry in dns:
                            if entry.get("dynamic", "false") != "true":
                                line = f"/ip dns static add name={entry.get('name')}"
                                if entry.get("address"):
                                    line += f" address={entry.get('address')}"
                                if entry.get("type"):
                                    line += f" type={entry.get('type')}"
                                config_parts.append(line)
                except Exception:
                    pass

                return "\n".join(config_parts) if config_parts else "# Empty configuration"

        except Exception as e:
            logger.error(f"Error exporting config: {e}")
            return None

    def get_system_health(self) -> Optional[Dict[str, Any]]:
        """Get system health information (temperature, voltage, etc.)."""
        try:
            with self._connection() as api:
                health = list(api.path("/system/health"))
                if health:
                    h = health[0]
                    return {
                        "temperature": h.get("temperature", h.get("cpu-temperature")),
                        "voltage": h.get("voltage"),
                        "cpu_temperature": h.get("cpu-temperature"),
                        "board_temperature": h.get("board-temperature")
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return None
