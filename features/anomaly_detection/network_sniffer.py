from scapy.all import sniff, IP
from features.anomaly_detection.rule_engine import rule_based_detection
from features.anomaly_detection.prevention_engine import block_ip, unblock_expired_ips
from core.config.ids_config import ENABLE_AUTO_BLOCK

def process_packet(packet):
    if IP not in packet:
        return

    src_ip = packet[IP].src

    detected = rule_based_detection(src_ip)

    if detected:
        if ENABLE_AUTO_BLOCK:
            block_ip(src_ip)
            log_event(
                label="possible_dos",
                src_ip=src_ip,
                action="BLOCKED"
            )
        else:
            log_event(
                label="possible_dos",
                src_ip=src_ip,
                action="DETECTED"
            )
    else:
        log_event("normal", src_ip)

    unblock_expired_ips()

def start_sniffing(interface=None):
    sniff(
        prn=process_packet,
        iface=interface,
        store=False
    )
