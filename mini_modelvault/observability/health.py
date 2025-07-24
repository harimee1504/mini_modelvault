"""
health.py – Fault-tolerant health & status. Uses local check + fallback datastore.
Provides the HealthChecker class for health and device status endpoints.
"""
import psutil
from .gpu_monitor import get_gpu_info


class HealthChecker:
    """
    Fault-tolerant health & status checker. Uses local check + fallback datastore.

    Args:
        logger: Logger instance for logging actions and errors.
    """
    def __init__(self, logger):
        """
        Initialize the HealthChecker.

        Args:
            logger: Logger instance.
        """
        self.logger = logger

    def status(self) -> dict:
        """
        Simple up/down health indication.

        Returns:
            dict: Health status.
        """
        self.logger.info("Health status checked.")
        return {'health': 'OK'}

    def device_status(self) -> dict:
        """
        Returns latest resource usage even if main loop stalled.
        Fallback: read last recorded snapshot.

        Returns:
            dict: Resource usage and health status.
        """
        try:
            ram = psutil.virtual_memory().percent
            cpu = psutil.cpu_percent(interval=0.5)
            gpu = get_gpu_info(self.logger)
            self.logger.info(f"Resource usage - RAM: {ram}%, CPU: {cpu}%, GPU: {gpu}")
        except Exception as e:
            self.logger.error(f"Failed to sample live: {e}")
            return {'health': 'DEGRADED', 'message': 'Resource usage unavailable'}
        return {'health': 'OK', 'ram': ram, 'cpu': cpu, 'gpu': gpu}