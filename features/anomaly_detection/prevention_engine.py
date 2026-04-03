import subprocess
import time
from core.config.ids_config import BLOCK_DURATION

BLOCKED_IPS = {}

def block_ip(ip: str):
    if ip in BLOCKED_IPS:
        return

    cmd = (
        f'netsh advfirewall firewall add rule '
        f'name="CyberGuard_Block_{ip}" '
        f'dir=in action=block remoteip={ip}'
    )

    subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    BLOCKED_IPS[ip] = time.time()

def unblock_expired_ips():
    now = time.time()

    for ip, ts in list(BLOCKED_IPS.items()):
        if now - ts > BLOCK_DURATION:
            cmd = (
                f'netsh advfirewall firewall delete rule '
                f'name="CyberGuard_Block_{ip}"'
            )
            subprocess.run(
                cmd,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            del BLOCKED_IPS[ip]
