from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Router(Base):
    __tablename__ = "routers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    ip_address = Column(String(45), nullable=False)
    api_port = Column(Integer, default=8728)
    username = Column(String(100), nullable=False)
    password = Column(String(255), nullable=False)
    use_ssl = Column(Boolean, default=False)

    # Status
    is_online = Column(Boolean, default=False)
    last_seen = Column(DateTime(timezone=True), nullable=True)

    # Router info (cached)
    model = Column(String(100), nullable=True)
    serial_number = Column(String(100), nullable=True)
    ros_version = Column(String(50), nullable=True)
    firmware_version = Column(String(50), nullable=True)

    # Metadata
    location = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relations
    stats = relationship("RouterStats", back_populates="router", cascade="all, delete-orphan")


class RouterStats(Base):
    __tablename__ = "router_stats"

    id = Column(Integer, primary_key=True, index=True)
    router_id = Column(Integer, ForeignKey("routers.id", ondelete="CASCADE"), nullable=False)

    # System stats
    cpu_load = Column(Float, nullable=True)
    memory_used = Column(Integer, nullable=True)  # bytes
    memory_total = Column(Integer, nullable=True)  # bytes
    disk_used = Column(Integer, nullable=True)  # bytes
    disk_total = Column(Integer, nullable=True)  # bytes
    uptime = Column(String(100), nullable=True)

    # Network stats
    wifi_clients = Column(Integer, default=0)
    dhcp_leases = Column(Integer, default=0)
    active_connections = Column(Integer, default=0)

    # Timestamp
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relations
    router = relationship("Router", back_populates="stats")
