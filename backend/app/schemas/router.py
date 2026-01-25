from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# Router schemas
class RouterBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    ip_address: str = Field(..., min_length=7, max_length=45)
    api_port: int = Field(default=8728, ge=1, le=65535)
    username: str = Field(..., min_length=1, max_length=100)
    use_ssl: bool = False
    location: Optional[str] = None
    notes: Optional[str] = None


class RouterCreate(RouterBase):
    password: str = Field(..., min_length=1, max_length=255)


class RouterUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    ip_address: Optional[str] = Field(None, min_length=7, max_length=45)
    api_port: Optional[int] = Field(None, ge=1, le=65535)
    username: Optional[str] = Field(None, min_length=1, max_length=100)
    password: Optional[str] = Field(None, min_length=1, max_length=255)
    use_ssl: Optional[bool] = None
    location: Optional[str] = None
    notes: Optional[str] = None


class RouterResponse(BaseModel):
    id: int
    name: str
    ip_address: str
    api_port: int
    username: str
    use_ssl: bool
    is_online: bool
    last_seen: Optional[datetime]
    model: Optional[str]
    serial_number: Optional[str]
    ros_version: Optional[str]
    firmware_version: Optional[str]
    location: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class RouterListResponse(BaseModel):
    routers: List[RouterResponse]
    total: int


# Stats schemas
class RouterStatsResponse(BaseModel):
    id: int
    router_id: int
    cpu_load: Optional[float]
    memory_used: Optional[int]
    memory_total: Optional[int]
    memory_percent: Optional[float] = None
    disk_used: Optional[int]
    disk_total: Optional[int]
    disk_percent: Optional[float] = None
    uptime: Optional[str]
    wifi_clients: int = 0
    dhcp_leases: int = 0
    active_connections: int = 0
    recorded_at: datetime

    class Config:
        from_attributes = True

    def __init__(self, **data):
        super().__init__(**data)
        if self.memory_used and self.memory_total:
            self.memory_percent = round((self.memory_used / self.memory_total) * 100, 1)
        if self.disk_used and self.disk_total:
            self.disk_percent = round((self.disk_used / self.disk_total) * 100, 1)


# DHCP schemas
class DHCPLease(BaseModel):
    id: str
    address: str
    mac_address: str
    client_id: Optional[str] = None
    hostname: Optional[str] = None
    server: Optional[str] = None
    status: str
    expires_after: Optional[str] = None
    last_seen: Optional[str] = None
    comment: Optional[str] = None


# WiFi schemas
class WifiClient(BaseModel):
    interface: str
    mac_address: str
    signal_strength: Optional[str] = None
    tx_rate: Optional[str] = None
    rx_rate: Optional[str] = None
    uptime: Optional[str] = None
    bytes_sent: Optional[int] = None
    bytes_received: Optional[int] = None


# Interface schemas
class Interface(BaseModel):
    id: str
    name: str
    type: str
    mac_address: Optional[str] = None
    mtu: Optional[int] = None
    running: bool = False
    disabled: bool = False
    comment: Optional[str] = None
    tx_bytes: Optional[int] = None
    rx_bytes: Optional[int] = None


# IP Address schemas
class IPAddress(BaseModel):
    id: str
    address: str
    network: Optional[str] = None
    interface: str
    disabled: bool = False
    dynamic: bool = False
    comment: Optional[str] = None


# Route schemas
class Route(BaseModel):
    id: str
    dst_address: str
    gateway: Optional[str] = None
    distance: int = 0
    interface: Optional[str] = None
    disabled: bool = False
    dynamic: bool = False
    static: bool = False
    comment: Optional[str] = None


# Firewall schemas
class FirewallRule(BaseModel):
    id: str
    chain: str
    action: str
    src_address: Optional[str] = None
    dst_address: Optional[str] = None
    protocol: Optional[str] = None
    src_port: Optional[str] = None
    dst_port: Optional[str] = None
    in_interface: Optional[str] = None
    out_interface: Optional[str] = None
    disabled: bool = False
    comment: Optional[str] = None
    bytes: Optional[int] = None
    packets: Optional[int] = None


class NATRule(BaseModel):
    id: str
    chain: str
    action: str
    src_address: Optional[str] = None
    dst_address: Optional[str] = None
    protocol: Optional[str] = None
    src_port: Optional[str] = None
    dst_port: Optional[str] = None
    to_addresses: Optional[str] = None
    to_ports: Optional[str] = None
    in_interface: Optional[str] = None
    out_interface: Optional[str] = None
    disabled: bool = False
    comment: Optional[str] = None


# DNS schemas
class DNSEntry(BaseModel):
    id: str
    name: str
    address: Optional[str] = None
    type: Optional[str] = None
    ttl: Optional[str] = None
    disabled: bool = False
    dynamic: bool = False
    comment: Optional[str] = None


# QoS schemas
class QueueRule(BaseModel):
    id: str
    name: str
    target: str
    max_limit: Optional[str] = None
    burst_limit: Optional[str] = None
    burst_threshold: Optional[str] = None
    burst_time: Optional[str] = None
    priority: Optional[int] = None
    disabled: bool = False
    comment: Optional[str] = None
    bytes: Optional[int] = None
    packets: Optional[int] = None


# Wireless schemas
class WirelessInterface(BaseModel):
    id: str
    name: str
    mac_address: Optional[str] = None
    ssid: Optional[str] = None
    mode: Optional[str] = None
    band: Optional[str] = None
    channel_width: Optional[str] = None
    frequency: Optional[str] = None
    security_profile: Optional[str] = None
    disabled: bool = False
    running: bool = False


class WirelessSecurityProfile(BaseModel):
    id: str
    name: str
    mode: Optional[str] = None
    authentication_types: Optional[str] = None
    wpa_pre_shared_key: Optional[str] = None
    wpa2_pre_shared_key: Optional[str] = None


# Detail response with stats
class RouterDetailResponse(RouterResponse):
    current_stats: Optional[RouterStatsResponse] = None
    stats_history: List[RouterStatsResponse] = []
