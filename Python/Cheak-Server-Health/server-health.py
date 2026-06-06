import psutil
import datetime
import os

def get_system_stats():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    
    return cpu, ram, disk

def write_log(cpu, ram, disk):
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    
    log_message = f"[{timestamp}] CPU: {cpu}% | RAM: {ram}% | Disk: {disk}%\n"
    
    with open("server_health.log", "a") as f:
        f.write(log_message)
    
    print(log_message, flush=True)

def check_warnings(cpu, ram, disk):
    warnings = []
    
    if cpu > 80:
        warnings.append(f"تحذير: CPU وصل {cpu}%")
    
    if ram > 80:
        warnings.append(f"تحذير: RAM وصل {ram}%")
    
    if disk > 90:
        warnings.append(f"تحذير: Disk وصل {disk}%")
    
    return warnings

cpu, ram, disk = get_system_stats()
write_log(cpu, ram, disk)
warnings = check_warnings(cpu, ram, disk)

if warnings:
    for w in warnings:
        print(w, flush=True)
else:
    print("كل حاجة تمام!", flush=True)