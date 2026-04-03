import time
from collections import defaultdict, deque
from core.config.ids_config import (
    WINDOW_SECONDS,
    PACKET_THRESHOLD,
    TRUSTED_PREFIXES
)

IP_ACTIVITY = defaultdict(deque)
LAST_ALERT = {}

def is_trusted_ip(ip: str) -> bool:
    return ip.startswith(TRUSTED_PREFIXES)

def rule_based_detection(src_ip: str) -> bool:
    if is_trusted_ip(src_ip):
        return False

    now = time.time()
    q = IP_ACTIVITY[src_ip]
    q.append(now)

    # sliding window
    while q and now - q[0] > WINDOW_SECONDS:
        q.popleft()

    if len(q) >= PACKET_THRESHOLD:
        last = LAST_ALERT.get(src_ip, 0)
        if now - last > WINDOW_SECONDS:
            LAST_ALERT[src_ip] = now
            return True

    return False
