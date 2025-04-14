import ping3
import subprocess
import re
from nmap import PortScanner

# Routers for ping and SNMP
ROUTERS = ["192.168.2.240", "192.168.2.241","192.168.2.243"]

# SNMP OIDs
OIDS = {
    "hostname": "1.3.6.1.4.1.9.2.1.3.0",
    "domain": "1.3.6.1.4.1.9.2.1.4.0",
    "uptime": "1.3.6.1.4.1.9.2.1.8.0",
    "location": "1.3.6.1.4.1.9.2.1.61.0",
    "cpu_5s": "1.3.6.1.4.1.9.2.1.56.0",
    "cpu_1m": "1.3.6.1.4.1.9.2.1.57.0",
    "cpu_5m": "1.3.6.1.4.1.9.2.1.58.0",
    "mem_total": "1.3.6.1.4.1.9.2.1.14.0",
    "mem_used": "1.3.6.1.4.1.9.2.1.15.0",
    "mem_free": "1.3.6.1.4.1.9.2.1.16.0",
}

def snmp_query(ip, oid):
    cmd = f"snmpwalk -v2c -c public {ip} {oid}"
    try:
        output = subprocess.check_output(cmd, shell=True).decode()
        match = re.search(r'(?::\s+)(.*)$', output)
        return match.group(1).strip() if match else "ParseError"
    except subprocess.CalledProcessError:
        return "Error"

def get_int_snmp(ip, oid):
    value = snmp_query(ip, oid)
    try:
        return int(re.search(r'\d+', value).group())
    except:
        return -1

def monitor_router(ip):
    print(f"\n🔍 Monitoring {ip}")
    print("=" * 50)

    # Device Info
    hostname = snmp_query(ip, OIDS["hostname"])
    domain = snmp_query(ip, OIDS["domain"])
    uptime = snmp_query(ip, OIDS["uptime"])
    location = snmp_query(ip, OIDS["location"])

    # CPU Info
    cpu_5s = snmp_query(ip, OIDS["cpu_5s"])
    cpu_1m = snmp_query(ip, OIDS["cpu_1m"])
    cpu_5m = snmp_query(ip, OIDS["cpu_5m"])

    # Memory Info
    mem_total = get_int_snmp(ip, OIDS["mem_total"])
    mem_used = get_int_snmp(ip, OIDS["mem_used"])
    mem_free = get_int_snmp(ip, OIDS["mem_free"])
    mem_usage = (mem_used / mem_total) * 100 if mem_total > 0 else 0

    # Display SNMP Data
    print(f"🖥️  Hostname   : {hostname}")
    print(f"🌐 Domain     : {domain}")
    print(f"⏱️  Uptime     : {uptime}")
    print(f"📍 Location   : {location}")
    print()
    print(f"🧠 CPU Load   →  5s: {cpu_5s}%  |  1m: {cpu_1m}%  |  5m: {cpu_5m}%")
    print(f"💾 Memory     →  Total: {mem_total} KB  |  Used: {mem_used} KB  |  Free: {mem_free} KB")
    print(f"📊 Mem Usage  →  {mem_usage:.1f}%" if mem_total > 0 else "📊 Mem Usage  →  Error")

def ping_and_scan():
    print("\n🚀 Starting Router Monitoring (Ping + Port Scan)...")
    scanner = PortScanner()

    # Ping check
    print("\n🔍 Ping Check:")
    for ip in ROUTERS:
        response = ping3.ping(ip, timeout=2)
        print(f"  {ip}: {'✅ UP' if response else '❌ DOWN'}")

    # Port scan
    print("\n📡 Port Scan:")
    for ip in ROUTERS:
        try:
            scanner.scan(ip, "22,23,80,443")
            if ip in scanner.all_hosts():
                for proto in scanner[ip].all_protocols():
                    for port in scanner[ip][proto]:
                        state = scanner[ip][proto][port]["state"]
                        print(f"  {ip}: Port {port}/{proto} -> {state}")
            else:
                print(f"  {ip}: Host not responding to scans")
        except Exception as e:
            print(f"  ⚠️ {ip}: Scan failed - {str(e)}")

def main():
    print("📡 Cisco Router Monitor via SNMP, Ping, and Port Scan")
    for ip in ROUTERS:
        monitor_router(ip)
    ping_and_scan()

if __name__ == "__main__":
    main()
