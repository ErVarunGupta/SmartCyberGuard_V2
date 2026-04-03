FEATURE_ORDER = [
    'duration','protocol_type','flag','src_bytes','dst_bytes','land',
    'wrong_fragment','urgent','hot','num_failed_logins','logged_in',
    'num_compromised','root_shell','su_attempted','num_file_creations',
    'num_shells','num_access_files','is_guest_login','count','srv_count',
    'serror_rate','rerror_rate','same_srv_rate','diff_srv_rate',
    'srv_diff_host_rate','dst_host_count','dst_host_srv_count',
    'dst_host_diff_srv_rate','dst_host_same_src_port_rate',
    'dst_host_srv_diff_host_rate'
]

PROTOCOL_MAP = {"icmp": 0, "tcp": 1, "udp": 2}
FLAG_MAP = {"SF": 0, "S0": 1, "REJ": 2}

def encode_protocol(p):
    return PROTOCOL_MAP.get(p, 1)

def encode_flag(f):
    return FLAG_MAP.get(f, 0)
