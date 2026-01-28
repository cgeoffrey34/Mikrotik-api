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
    router_type: Optional[str] = None
    site: Optional[str] = None
    group: Optional[str] = None
    tags: Optional[str] = None
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
    router_type: Optional[str] = None
    site: Optional[str] = None
    group: Optional[str] = None
    tags: Optional[str] = None
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
    router_type: Optional[str]
    site: Optional[str]
    group: Optional[str]
    tags: Optional[str]
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
    status: str = ""
    expires_after: Optional[str] = None
    last_seen: Optional[str] = None
    comment: Optional[str] = None
    dynamic: bool = False


class DHCPServer(BaseModel):
    id: str
    name: str
    interface: str
    address_pool: Optional[str] = None
    lease_time: Optional[str] = None
    disabled: bool = False
    invalid: bool = False
    authoritative: Optional[str] = None
    use_radius: bool = False


class DHCPNetwork(BaseModel):
    id: str
    address: str
    gateway: Optional[str] = None
    dns_server: Optional[str] = None
    domain: Optional[str] = None
    netmask: Optional[str] = None
    ntp_server: Optional[str] = None
    wins_server: Optional[str] = None
    comment: Optional[str] = None


class IPPool(BaseModel):
    id: str
    name: str
    ranges: str
    next_pool: Optional[str] = None
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
    ssid: Optional[str] = None


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
    interface_type: Optional[str] = None


class WirelessSecurityProfile(BaseModel):
    id: str
    name: str
    mode: Optional[str] = None
    authentication_types: Optional[str] = None
    wpa_pre_shared_key: Optional[str] = None
    wpa2_pre_shared_key: Optional[str] = None
    passphrase: Optional[str] = None
    profile_type: Optional[str] = None


# Interface schemas
class Interface(BaseModel):
    id: str
    name: str
    default_name: Optional[str] = None
    type: str = ""
    mac_address: Optional[str] = None
    mtu: Optional[int] = None
    l2mtu: Optional[int] = None
    running: bool = False
    disabled: bool = False
    comment: Optional[str] = None
    tx_bytes: Optional[int] = None
    rx_bytes: Optional[int] = None
    tx_packets: Optional[int] = None
    rx_packets: Optional[int] = None
    link_downs: Optional[int] = None


# Bridge schemas
class Bridge(BaseModel):
    id: str
    name: str
    mac_address: Optional[str] = None
    mtu: Optional[int] = None
    protocol_mode: Optional[str] = None
    fast_forward: bool = False
    igmp_snooping: bool = False
    vlan_filtering: bool = False
    admin_mac: Optional[str] = None
    ageing_time: Optional[str] = None
    arp: Optional[str] = None
    disabled: bool = False
    running: bool = False
    comment: Optional[str] = None


class BridgePort(BaseModel):
    id: str
    bridge: str
    interface: str
    hw: bool = False
    pvid: int = 1
    frame_types: Optional[str] = None
    ingress_filtering: bool = False
    disabled: bool = False
    inactive: bool = False
    comment: Optional[str] = None


class BridgeVlan(BaseModel):
    id: str
    bridge: str
    vlan_ids: str
    tagged: Optional[str] = None
    untagged: Optional[str] = None
    disabled: bool = False
    comment: Optional[str] = None


# IP Address schemas
class IPAddress(BaseModel):
    id: str
    address: str
    network: Optional[str] = None
    interface: str
    actual_interface: Optional[str] = None
    disabled: bool = False
    dynamic: bool = False
    invalid: bool = False
    comment: Optional[str] = None


# Route schemas
class Route(BaseModel):
    id: str
    dst_address: str
    gateway: Optional[str] = None
    gateway_status: Optional[str] = None
    distance: int = 0
    scope: Optional[int] = None
    interface: Optional[str] = None
    disabled: bool = False
    dynamic: bool = False
    static: bool = False
    connect: bool = False
    active: bool = False
    route_type: str = "other"
    routing_table: Optional[str] = None
    comment: Optional[str] = None


# Firewall schemas
class FirewallRule(BaseModel):
    id: str
    chain: str
    action: str
    src_address: Optional[str] = None
    dst_address: Optional[str] = None
    src_address_list: Optional[str] = None
    dst_address_list: Optional[str] = None
    protocol: Optional[str] = None
    src_port: Optional[str] = None
    dst_port: Optional[str] = None
    in_interface: Optional[str] = None
    in_interface_list: Optional[str] = None
    out_interface: Optional[str] = None
    out_interface_list: Optional[str] = None
    connection_state: Optional[str] = None
    disabled: bool = False
    invalid: bool = False
    dynamic: bool = False
    comment: Optional[str] = None
    bytes: Optional[int] = None
    packets: Optional[int] = None
    log: bool = False
    log_prefix: Optional[str] = None


class FirewallRuleCreate(BaseModel):
    chain: str
    action: str
    src_address: Optional[str] = None
    dst_address: Optional[str] = None
    protocol: Optional[str] = None
    src_port: Optional[str] = None
    dst_port: Optional[str] = None
    in_interface: Optional[str] = None
    out_interface: Optional[str] = None
    connection_state: Optional[str] = None
    comment: Optional[str] = None
    disabled: bool = False


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
    in_interface_list: Optional[str] = None
    out_interface: Optional[str] = None
    out_interface_list: Optional[str] = None
    disabled: bool = False
    invalid: bool = False
    dynamic: bool = False
    comment: Optional[str] = None
    bytes: Optional[int] = None
    packets: Optional[int] = None


class NATRuleCreate(BaseModel):
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
    comment: Optional[str] = None
    disabled: bool = False


# Mangle schemas
class MangleRule(BaseModel):
    id: str
    chain: str
    action: str
    src_address: Optional[str] = None
    dst_address: Optional[str] = None
    src_address_list: Optional[str] = None
    dst_address_list: Optional[str] = None
    protocol: Optional[str] = None
    src_port: Optional[str] = None
    dst_port: Optional[str] = None
    in_interface: Optional[str] = None
    in_interface_list: Optional[str] = None
    out_interface: Optional[str] = None
    out_interface_list: Optional[str] = None
    connection_state: Optional[str] = None
    new_packet_mark: Optional[str] = None
    new_connection_mark: Optional[str] = None
    new_routing_mark: Optional[str] = None
    passthrough: bool = True
    disabled: bool = False
    invalid: bool = False
    dynamic: bool = False
    comment: Optional[str] = None
    bytes: Optional[int] = None
    packets: Optional[int] = None
    log: bool = False
    log_prefix: Optional[str] = None
    connection_mark: Optional[str] = None
    packet_mark: Optional[str] = None
    routing_mark: Optional[str] = None


class MangleRuleCreate(BaseModel):
    chain: str
    action: str
    src_address: Optional[str] = None
    dst_address: Optional[str] = None
    src_address_list: Optional[str] = None
    dst_address_list: Optional[str] = None
    protocol: Optional[str] = None
    src_port: Optional[str] = None
    dst_port: Optional[str] = None
    in_interface: Optional[str] = None
    out_interface: Optional[str] = None
    connection_state: Optional[str] = None
    new_packet_mark: Optional[str] = None
    new_connection_mark: Optional[str] = None
    new_routing_mark: Optional[str] = None
    passthrough: bool = True
    comment: Optional[str] = None
    disabled: bool = False


# RAW schemas
class RawRule(BaseModel):
    id: str
    chain: str
    action: str
    src_address: Optional[str] = None
    dst_address: Optional[str] = None
    src_address_list: Optional[str] = None
    dst_address_list: Optional[str] = None
    protocol: Optional[str] = None
    src_port: Optional[str] = None
    dst_port: Optional[str] = None
    in_interface: Optional[str] = None
    in_interface_list: Optional[str] = None
    out_interface: Optional[str] = None
    out_interface_list: Optional[str] = None
    connection_state: Optional[str] = None
    disabled: bool = False
    invalid: bool = False
    dynamic: bool = False
    comment: Optional[str] = None
    bytes: Optional[int] = None
    packets: Optional[int] = None
    log: bool = False
    log_prefix: Optional[str] = None


class RawRuleCreate(BaseModel):
    chain: str
    action: str
    src_address: Optional[str] = None
    dst_address: Optional[str] = None
    src_address_list: Optional[str] = None
    dst_address_list: Optional[str] = None
    protocol: Optional[str] = None
    src_port: Optional[str] = None
    dst_port: Optional[str] = None
    in_interface: Optional[str] = None
    out_interface: Optional[str] = None
    connection_state: Optional[str] = None
    comment: Optional[str] = None
    disabled: bool = False


# Service Port schemas
class ServicePort(BaseModel):
    id: str
    name: str
    ports: Optional[str] = None
    disabled: bool = False
    invalid: bool = False


# Connection schemas
class ConnectionEntry(BaseModel):
    id: str
    protocol: Optional[str] = None
    src_address: Optional[str] = None
    dst_address: Optional[str] = None
    reply_src_address: Optional[str] = None
    reply_dst_address: Optional[str] = None
    tcp_state: Optional[str] = None
    timeout: Optional[str] = None
    connection_mark: Optional[str] = None
    assured: bool = False
    confirmed: bool = False
    dying: bool = False
    fasttrack: bool = False
    orig_bytes: Optional[int] = None
    repl_bytes: Optional[int] = None
    orig_packets: Optional[int] = None
    repl_packets: Optional[int] = None


# Address List schemas
class AddressListEntry(BaseModel):
    id: str
    list: str
    address: str
    timeout: Optional[str] = None
    creation_time: Optional[str] = None
    disabled: bool = False
    dynamic: bool = False
    comment: Optional[str] = None


class AddressListEntryCreate(BaseModel):
    list: str
    address: str
    timeout: Optional[str] = None
    comment: Optional[str] = None
    disabled: bool = False


# DNS schemas
class DNSEntry(BaseModel):
    id: str
    name: str
    address: Optional[str] = None
    cname: Optional[str] = None
    mx_exchange: Optional[str] = None
    mx_preference: Optional[str] = None
    srv_target: Optional[str] = None
    srv_port: Optional[str] = None
    text: Optional[str] = None
    ns: Optional[str] = None
    type: Optional[str] = "A"
    ttl: Optional[str] = None
    disabled: bool = False
    dynamic: bool = False
    regexp: Optional[str] = None
    forward_to: Optional[str] = None
    comment: Optional[str] = None


class DNSEntryCreate(BaseModel):
    name: str
    record_type: str = "A"
    address: Optional[str] = None
    cname: Optional[str] = None
    mx_exchange: Optional[str] = None
    mx_preference: Optional[int] = None
    text: Optional[str] = None
    ns: Optional[str] = None
    srv_target: Optional[str] = None
    srv_port: Optional[int] = None
    forward_to: Optional[str] = None
    ttl: str = "1d"
    comment: Optional[str] = None
    disabled: bool = False


class DNSSettings(BaseModel):
    servers: Optional[str] = None
    dynamic_servers: Optional[str] = None
    allow_remote_requests: bool = False
    cache_size: Optional[int] = None
    cache_max_ttl: Optional[str] = None
    cache_used: Optional[int] = None
    use_doh_server: Optional[str] = None
    verify_doh_cert: bool = False
    max_udp_packet_size: Optional[int] = None
    max_concurrent_queries: Optional[int] = None
    max_concurrent_tcp_sessions: Optional[int] = None


class DNSSettingsUpdate(BaseModel):
    servers: Optional[str] = None
    allow_remote_requests: Optional[bool] = None
    cache_size: Optional[int] = None
    cache_max_ttl: Optional[str] = None
    use_doh_server: Optional[str] = None
    verify_doh_cert: Optional[bool] = None


class DNSCacheEntry(BaseModel):
    id: str
    name: str
    type: str
    data: str
    ttl: Optional[str] = None
    static: bool = False


# QoS schemas
class QueueRule(BaseModel):
    id: str
    name: str
    target: str
    parent: Optional[str] = None
    max_limit: Optional[str] = None
    limit_at: Optional[str] = None
    burst_limit: Optional[str] = None
    burst_threshold: Optional[str] = None
    burst_time: Optional[str] = None
    priority: Optional[int] = None
    disabled: bool = False
    invalid: bool = False
    comment: Optional[str] = None
    bytes: Optional[int] = None
    packets: Optional[int] = None
    rate: Optional[str] = None


# Detail response with stats
class RouterDetailResponse(RouterResponse):
    current_stats: Optional[RouterStatsResponse] = None
    stats_history: List[RouterStatsResponse] = []
