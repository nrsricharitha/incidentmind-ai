"""Safe simulated service diagnostic inspection tool."""

from typing import Any, Dict
from src.agent.schemas import ServiceHealth, ServiceStatus

# Deterministic simulated service profiles for demo/diagnostic evaluation
SIMULATED_PROFILES: Dict[str, Dict[str, Any]] = {
    "payment-api": {
        "status": ServiceStatus.DEGRADED,
        "health_state": "Degraded - High connection acquisition wait time",
        "latency_ms": 3420.5,
        "error_rate_pct": 28.4,
        "connection_state": "DB Connection Pool Starvation (active: 50/50)",
        "active_connections": 50,
        "max_connections": 50,
        "recent_deployment": "Release v2.4.1 deployed 3 hours ago (commit 9f4a1c)",
    },
    "database": {
        "status": ServiceStatus.DEGRADED,
        "health_state": "Pool Saturation - PostgreSQL RDS replica pool full",
        "latency_ms": 1850.0,
        "error_rate_pct": 19.5,
        "connection_state": "Max connections reached; 48 waiting requests",
        "active_connections": 100,
        "max_connections": 100,
        "recent_deployment": "Maintenance window completed 2 days ago",
    },
    "cache-service": {
        "status": ServiceStatus.HEALTHY,
        "health_state": "Healthy - Redis cluster operational",
        "latency_ms": 1.8,
        "error_rate_pct": 0.01,
        "connection_state": "Connected (84/10000 clients)",
        "active_connections": 84,
        "max_connections": 10000,
        "recent_deployment": "Version 7.2.4 deployed 14 days ago",
    },
    "order-service": {
        "status": ServiceStatus.HEALTHY,
        "health_state": "Healthy - All circuit breakers closed",
        "latency_ms": 42.0,
        "error_rate_pct": 0.1,
        "connection_state": "Normal (15/100 connections)",
        "active_connections": 15,
        "max_connections": 100,
        "recent_deployment": "Release v1.18.0 deployed yesterday",
    },
    "user-service": {
        "status": ServiceStatus.HEALTHY,
        "health_state": "Healthy - Auth token cache valid",
        "latency_ms": 28.0,
        "error_rate_pct": 0.05,
        "connection_state": "Normal (12/100 connections)",
        "active_connections": 12,
        "max_connections": 100,
        "recent_deployment": "Release v3.0.2 deployed 5 days ago",
    },
    "api-gateway": {
        "status": ServiceStatus.DEGRADED,
        "health_state": "Degraded - Backpressure on /v1/payments route",
        "latency_ms": 2980.0,
        "error_rate_pct": 14.2,
        "connection_state": "Upstream socket pool near limit",
        "active_connections": 420,
        "max_connections": 500,
        "recent_deployment": "Envoy proxy config update 6 hours ago",
    },
}


def inspect_service(service_name: str) -> Dict[str, Any]:
    """Inspect the runtime health and diagnostics of a service.

    NOTE: This is a safe simulated diagnostic tool designed for demo and testing.
    No production systems are modified or contacted.

    Args:
        service_name: Name of the service to inspect (e.g. 'payment-api', 'database', 'cache-service').

    Returns:
        Structured health diagnostics including status, latency, error rate,
        connection state, and recent deployment information.
    """
    normalized = service_name.lower().strip()
    profile = SIMULATED_PROFILES.get(normalized)

    if not profile:
        # Fallback profile for unknown service
        return ServiceHealth(
            service_name=service_name,
            status=ServiceStatus.HEALTHY,
            health_state="Simulated healthy baseline - no active anomalies detected",
            latency_ms=45.0,
            error_rate_pct=0.0,
            connection_state="Connected",
            active_connections=10,
            max_connections=100,
            recent_deployment="Baseline deployment",
            simulated=True,
        ).model_dump()

    return ServiceHealth(
        service_name=service_name,
        status=profile["status"],
        health_state=profile["health_state"],
        latency_ms=profile["latency_ms"],
        error_rate_pct=profile["error_rate_pct"],
        connection_state=profile["connection_state"],
        active_connections=profile["active_connections"],
        max_connections=profile["max_connections"],
        recent_deployment=profile["recent_deployment"],
        simulated=True,
    ).model_dump()
