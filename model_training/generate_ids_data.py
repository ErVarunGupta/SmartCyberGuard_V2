import random
import pandas as pd

data = []

# NORMAL TRAFFIC
for _ in range(5000):
    packet_count = random.randint(5, 20)
    byte_count = random.randint(500, 5000)

    avg_packet_size = byte_count / packet_count
    packet_rate = random.uniform(1, 5)

    tcp_ratio = random.uniform(0.4, 0.9)
    udp_ratio = 1 - tcp_ratio

    unique_ports = random.randint(1, 5)

    label = 0

    data.append([
        packet_count,
        byte_count,
        avg_packet_size,
        packet_rate,
        tcp_ratio,
        udp_ratio,
        unique_ports,
        label
    ])

# ATTACK TRAFFIC
for _ in range(3000):
    packet_count = random.randint(50, 200)
    byte_count = random.randint(10000, 50000)

    avg_packet_size = byte_count / packet_count
    packet_rate = random.uniform(10, 50)

    tcp_ratio = random.uniform(0.8, 1.0)
    udp_ratio = 1 - tcp_ratio

    unique_ports = random.randint(10, 50)

    label = 1

    data.append([
        packet_count,
        byte_count,
        avg_packet_size,
        packet_rate,
        tcp_ratio,
        udp_ratio,
        unique_ports,
        label
    ])


# EXTREME ATTACK (DDOS STYLE)
for _ in range(2000):
    packet_count = random.randint(200, 500)
    byte_count = random.randint(50000, 200000)

    avg_packet_size = byte_count / packet_count
    packet_rate = random.uniform(50, 150)

    tcp_ratio = random.uniform(0.9, 1.0)
    udp_ratio = 1 - tcp_ratio

    unique_ports = random.randint(50, 200)

    label = 1

    data.append([
        packet_count,
        byte_count,
        avg_packet_size,
        packet_rate,
        tcp_ratio,
        udp_ratio,
        unique_ports,
        label
    ])

df = pd.DataFrame(data, columns=[
    "packet_count",
    "byte_count",
    "avg_packet_size",
    "packet_rate",
    "tcp_ratio",
    "udp_ratio",
    "unique_ports",
    "label"
])

df.to_csv("data/ids_dataset.csv", index=False)

print("✅ Dataset created")