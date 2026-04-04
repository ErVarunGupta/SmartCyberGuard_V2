import psutil
import time

prev_disk = psutil.disk_io_counters()


def get_heavy_process_count(threshold=5):
    count = 0
    for p in psutil.process_iter(['cpu_percent']):
        try:
            if p.info['cpu_percent'] > threshold:
                count += 1
        except:
            pass
    return count


def extract_system_features():
    global prev_disk

    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    # 🔥 Disk IO
    current_disk = psutil.disk_io_counters()
    disk_read = current_disk.read_bytes - prev_disk.read_bytes
    disk_write = current_disk.write_bytes - prev_disk.write_bytes
    prev_disk = current_disk

    # 🔋 Battery
    battery = psutil.sensors_battery()
    battery_percent = battery.percent if battery else 100

    # 🔢 Processes
    process_count = len(psutil.pids())
    heavy_process_count = get_heavy_process_count()

    return [
        cpu,
        ram,
        disk,
        disk_read,
        disk_write,
        battery_percent,
        process_count,
        heavy_process_count
    ]