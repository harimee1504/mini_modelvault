"""
gpu_monitor.py – collects GPU info using `nvidia-smi`.
Provides a function to collect and log GPU utilization and memory usage.
"""
import subprocess
import platform
from typing import Optional
from loguru import logger as default_logger

def get_gpu_info(logger: Optional[object] = None) -> dict:
    """
    Collect GPU info using nvidia-smi. Logs actions and errors.

    Args:
        logger (Optional[object]): Optional loguru logger instance.

    Returns:
        dict: Dictionary with GPU info or error.
    """
    log = logger or default_logger
    os_type = platform.system()
    log.info(f"Detecting OS: {os_type}")
    if os_type == 'Darwin':  # macOS
        log.warning('GPU monitoring is not supported on macOS (no NVIDIA GPU support).')
        return {'gpu': 'Unavailable', 'error': 'GPU monitoring is not supported on macOS (no NVIDIA GPU support).'}
    if os_type not in ['Linux', 'Windows']:
        log.warning(f'Unsupported OS: {os_type}')
        return {'gpu': 'Unavailable', 'error': f'Unsupported OS: {os_type}'}
    try:
        result = subprocess.check_output([
            "nvidia-smi",
            "--query-gpu=utilization.gpu,memory.total,memory.used",
            "--format=csv,nounits,noheader"
        ], stderr=subprocess.STDOUT)
        usage = result.decode().strip().split(', ')
        log.info(f"GPU usage: {usage}")
        return {
            'gpu_util': usage[0] + '%',
            'mem_total': usage[1] + ' MiB',
            'mem_used': usage[2] + ' MiB'
        }
    except FileNotFoundError:
        log.error('nvidia-smi not found. Ensure NVIDIA drivers are installed and nvidia-smi is in your PATH.')
        return {'gpu': 'Unavailable', 'error': 'nvidia-smi not found. Ensure NVIDIA drivers are installed and nvidia-smi is in your PATH.'}
    except subprocess.CalledProcessError as e:
        output = e.output.decode() if hasattr(e, 'output') else str(e)
        if 'No devices were found' in output or 'NVIDIA-SMI has failed' in output:
            log.error('No NVIDIA GPU detected on this system.')
            return {'gpu': 'Unavailable', 'error': 'No NVIDIA GPU detected on this system.'}
        log.error(f'GPU error: {output.strip()}')
        return {'gpu': 'Unavailable', 'error': output.strip()}
    except Exception as e:
        log.error(f'Unknown GPU error: {e}')
        return {'gpu': 'Unavailable', 'error': str(e)}