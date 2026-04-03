# IDS / IPS Configuration (Production Ready)

# Detection
WINDOW_SECONDS = 5
PACKET_THRESHOLD = 20  

# Prevention
ENABLE_AUTO_BLOCK = False   
BLOCK_DURATION = 60        

# Environment
DEMO_MODE = False          

# Trusted networks (never block)
TRUSTED_PREFIXES = (
    "127.",        # localhost
    "10.",         # private
    "192.168.",    # private
    "172.16.", "172.17.", "172.18.", "172.19.",
    "172.20.", "172.21.", "172.22.", "172.23.",
    "172.24.", "172.25.", "172.26.", "172.27.",
    "172.28.", "172.29.", "172.30.", "172.31."
)
