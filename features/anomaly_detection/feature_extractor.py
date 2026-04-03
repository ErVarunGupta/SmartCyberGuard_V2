from scapy.all import IP, TCP, UDP
from schema.feature_schema import encode_protocol, encode_flag

def extract_features(packet):
    try:
        ip = packet[IP]
        src_ip = ip.src

        protocol = "tcp" if TCP in packet else "udp" if UDP in packet else "icmp"
        flag = "SF"

        features = {
            "duration": 0,
            "protocol_type": encode_protocol(protocol),
            "flag": encode_flag(flag),
            "src_bytes": len(packet),
            "dst_bytes": 0,
            "land": int(ip.src == ip.dst),
            "wrong_fragment": 0,
            "urgent": 0,
            "hot": 0,
            "num_failed_logins": 0,
            "logged_in": 0,
            "num_compromised": 0,
            "root_shell": 0,
            "su_attempted": 0,
            "num_file_creations": 0,
            "num_shells": 0,
            "num_access_files": 0,
            "is_guest_login": 0,
            "count": 1,
            "srv_count": 1,
            "serror_rate": 0.0,
            "rerror_rate": 0.0,
            "same_srv_rate": 1.0,
            "diff_srv_rate": 0.0,
            "srv_diff_host_rate": 0.0,
            "dst_host_count": 1,
            "dst_host_srv_count": 1,
            "dst_host_diff_srv_rate": 0.0,
            "dst_host_same_src_port_rate": 1.0,
            "dst_host_srv_diff_host_rate": 0.0,
        }

        return src_ip, features

    except Exception:
        return None, None
