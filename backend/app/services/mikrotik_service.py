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

    def test_connection(self) -> Dict[str, Any]:
        """Test connection and return router identity."""
        try:
            with self._connection() as api:
                identity = list(api.path("/system/identity"))
                return {
                    "success": True,
                    "identity": identity[0].get("name", "Unknown") if identity else "Unknown"
                }
        except Exception as e:
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
                        "comment": lease.get("comment", "")
                    }
                    for lease in leases
                ]
        except Exception as e:
            logger.error(f"Error getting DHCP leases: {e}")
            return []

    def add_dhcp_lease(self, address: str, mac_address: str, server: str = "default", comment: str = "") -> bool:
        """Add a static DHCP lease."""
        try:
            with self._connection() as api:
                params = {
                    "address": address,
                    "mac-address": mac_address,
                    "server": server
                }
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

    # ==================== WiFi ====================

    def get_wifi_clients(self) -> List[Dict[str, Any]]:
        """Get all connected WiFi clients."""
        try:
            with self._connection() as api:
                # Try wireless/registration-table first (standard)
                try:
                    registrations = list(api.path("/interface/wireless/registration-table"))
                except Exception:
                    registrations = []

                # Also try CAPsMAN if available
                try:
                    capsman = list(api.path("/caps-man/registration-table"))
                    registrations.extend(capsman)
                except Exception:
                    pass

                return [
                    {
                        "interface": reg.get("interface", ""),
                        "mac_address": reg.get("mac-address", ""),
                        "signal_strength": reg.get("signal-strength", ""),
                        "tx_rate": reg.get("tx-rate", ""),
                        "rx_rate": reg.get("rx-rate", ""),
                        "uptime": reg.get("uptime", ""),
                        "bytes_sent": int(reg.get("bytes", "0").split(",")[0]) if reg.get("bytes") else 0,
                        "bytes_received": int(reg.get("bytes", "0,0").split(",")[1]) if "," in reg.get("bytes", "") else 0
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
                interfaces = list(api.path("/interface/wireless"))
                return [
                    {
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
                        "running": iface.get("running", "false") == "true"
                    }
                    for iface in interfaces
                ]
        except Exception as e:
            logger.error(f"Error getting wireless interfaces: {e}")
            return []

    def get_security_profiles(self) -> List[Dict[str, Any]]:
        """Get wireless security profiles."""
        try:
            with self._connection() as api:
                profiles = list(api.path("/interface/wireless/security-profiles"))
                return [
                    {
                        "id": profile.get(".id", ""),
                        "name": profile.get("name", ""),
                        "mode": profile.get("mode", ""),
                        "authentication_types": profile.get("authentication-types", "")
                    }
                    for profile in profiles
                ]
        except Exception as e:
            logger.error(f"Error getting security profiles: {e}")
            return []

    # ==================== Interfaces ====================

    def get_interfaces(self) -> List[Dict[str, Any]]:
        """Get all interfaces."""
        try:
            with self._connection() as api:
                interfaces = list(api.path("/interface"))
                return [
                    {
                        "id": iface.get(".id", ""),
                        "name": iface.get("name", ""),
                        "type": iface.get("type", ""),
                        "mac_address": iface.get("mac-address", ""),
                        "mtu": int(iface.get("mtu", 0)) if iface.get("mtu") else None,
                        "running": iface.get("running", "false") == "true",
                        "disabled": iface.get("disabled", "false") == "true",
                        "comment": iface.get("comment", ""),
                        "tx_bytes": int(iface.get("tx-byte", 0)) if iface.get("tx-byte") else 0,
                        "rx_bytes": int(iface.get("rx-byte", 0)) if iface.get("rx-byte") else 0
                    }
                    for iface in interfaces
                ]
        except Exception as e:
            logger.error(f"Error getting interfaces: {e}")
            return []

    def toggle_interface(self, interface_id: str, enable: bool) -> bool:
        """Enable or disable an interface."""
        try:
            with self._connection() as api:
                if enable:
                    api.path("/interface").update(**{".id": interface_id, "disabled": "no"})
                else:
                    api.path("/interface").update(**{".id": interface_id, "disabled": "yes"})
                return True
        except Exception as e:
            logger.error(f"Error toggling interface: {e}")
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
                        "disabled": addr.get("disabled", "false") == "true",
                        "dynamic": addr.get("dynamic", "false") == "true",
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

    def get_routes(self) -> List[Dict[str, Any]]:
        """Get all routes."""
        try:
            with self._connection() as api:
                routes = list(api.path("/ip/route"))
                return [
                    {
                        "id": route.get(".id", ""),
                        "dst_address": route.get("dst-address", ""),
                        "gateway": route.get("gateway", ""),
                        "distance": int(route.get("distance", 0)),
                        "interface": route.get("interface", ""),
                        "disabled": route.get("disabled", "false") == "true",
                        "dynamic": route.get("dynamic", "false") == "true",
                        "static": route.get("static", "false") == "true",
                        "comment": route.get("comment", "")
                    }
                    for route in routes
                ]
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

    def get_firewall_filter_rules(self) -> List[Dict[str, Any]]:
        """Get all firewall filter rules."""
        try:
            with self._connection() as api:
                rules = list(api.path("/ip/firewall/filter"))
                return [
                    {
                        "id": rule.get(".id", ""),
                        "chain": rule.get("chain", ""),
                        "action": rule.get("action", ""),
                        "src_address": rule.get("src-address", ""),
                        "dst_address": rule.get("dst-address", ""),
                        "protocol": rule.get("protocol", ""),
                        "src_port": rule.get("src-port", ""),
                        "dst_port": rule.get("dst-port", ""),
                        "in_interface": rule.get("in-interface", ""),
                        "out_interface": rule.get("out-interface", ""),
                        "disabled": rule.get("disabled", "false") == "true",
                        "comment": rule.get("comment", ""),
                        "bytes": int(rule.get("bytes", 0)) if rule.get("bytes") else 0,
                        "packets": int(rule.get("packets", 0)) if rule.get("packets") else 0
                    }
                    for rule in rules
                ]
        except Exception as e:
            logger.error(f"Error getting firewall rules: {e}")
            return []

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
                return [
                    {
                        "id": rule.get(".id", ""),
                        "chain": rule.get("chain", ""),
                        "action": rule.get("action", ""),
                        "src_address": rule.get("src-address", ""),
                        "dst_address": rule.get("dst-address", ""),
                        "protocol": rule.get("protocol", ""),
                        "src_port": rule.get("src-port", ""),
                        "dst_port": rule.get("dst-port", ""),
                        "to_addresses": rule.get("to-addresses", ""),
                        "to_ports": rule.get("to-ports", ""),
                        "in_interface": rule.get("in-interface", ""),
                        "out_interface": rule.get("out-interface", ""),
                        "disabled": rule.get("disabled", "false") == "true",
                        "comment": rule.get("comment", "")
                    }
                    for rule in rules
                ]
        except Exception as e:
            logger.error(f"Error getting NAT rules: {e}")
            return []

    # ==================== DNS ====================

    def get_dns_static(self) -> List[Dict[str, Any]]:
        """Get static DNS entries."""
        try:
            with self._connection() as api:
                entries = list(api.path("/ip/dns/static"))
                return [
                    {
                        "id": entry.get(".id", ""),
                        "name": entry.get("name", ""),
                        "address": entry.get("address", ""),
                        "type": entry.get("type", "A"),
                        "ttl": entry.get("ttl", ""),
                        "disabled": entry.get("disabled", "false") == "true",
                        "dynamic": entry.get("dynamic", "false") == "true",
                        "comment": entry.get("comment", "")
                    }
                    for entry in entries
                ]
        except Exception as e:
            logger.error(f"Error getting DNS entries: {e}")
            return []

    def add_dns_static(self, name: str, address: str, ttl: str = "1d", comment: str = "") -> bool:
        """Add a static DNS entry."""
        try:
            with self._connection() as api:
                params = {"name": name, "address": address, "ttl": ttl}
                if comment:
                    params["comment"] = comment
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
                        "max_limit": queue.get("max-limit", ""),
                        "burst_limit": queue.get("burst-limit", ""),
                        "burst_threshold": queue.get("burst-threshold", ""),
                        "burst_time": queue.get("burst-time", ""),
                        "priority": int(queue.get("priority", "8").split("/")[0]),
                        "disabled": queue.get("disabled", "false") == "true",
                        "comment": queue.get("comment", ""),
                        "bytes": int(queue.get("bytes", 0)) if queue.get("bytes") else 0,
                        "packets": int(queue.get("packets", 0)) if queue.get("packets") else 0
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
                api.path("/system").call("reboot")
                return True
        except Exception as e:
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
                        "disabled": user.get("disabled", "false") == "true",
                        "comment": user.get("comment", "")
                    }
                    for user in users
                ]
        except Exception as e:
            logger.error(f"Error getting users: {e}")
            return []

    def backup_config(self) -> Optional[str]:
        """Create a backup and return the file name."""
        try:
            with self._connection() as api:
                import time
                filename = f"backup-{int(time.time())}"
                api.path("/system/backup").call("save", {"name": filename})
                return f"{filename}.backup"
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None

    def export_config(self) -> Optional[str]:
        """Export configuration as text."""
        try:
            with self._connection() as api:
                result = list(api.path("/export"))
                return "\n".join([r.get("ret", "") for r in result]) if result else None
        except Exception as e:
            logger.error(f"Error exporting config: {e}")
            return None
