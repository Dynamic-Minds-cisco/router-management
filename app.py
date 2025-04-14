# Import necessary packages
from flask import Flask, render_template
import subprocess

# Initialize Flask app
app = Flask(__name__)

# List of router IPs for monitoring
ROUTERS = ["192.168.2.240", "192.168.2.241","192.168.2.243"
]

# Define SNMP OIDs for various metrics (hostname, domain, uptime, CPU, memory, etc.)
OIDS = {
    "hostname": "1.3.6.1.4.1.9.2.1.3.0",
    "domain": "1.3.6.1.4.1.9.2.1.4.0",
    "uptime": "1.3.6.1.2.1.1.3.0",
    "cpu_5s": "1.3.6.1.4.1.9.2.1.56.0",
    "cpu_1m": "1.3.6.1.4.1.9.2.1.57.0",
    "cpu_5m": "1.3.6.1.4.1.9.2.1.58.0",
    "mem_total": "1.3.6.1.4.1.9.2.1.8.0",
    "mem_used": "1.3.6.1.4.1.9.2.1.9.0",
    "if_count": "1.3.6.1.2.1.2.1.0",
    "interfaces_name": "1.3.6.1.2.1.2.2.1.2",  # To get interface names
    "interfaces_status": "1.3.6.1.2.1.2.2.1.8"  # To get interface operational status
}

# Function to fetch SNMP data (hostname, uptime, CPU, memory, etc.) for a given IP and OID
def get_snmp(ip, oid, parse_as='int'):
    try:
        # Execute SNMP command to get data from the router
        output = subprocess.check_output(f"snmpget -v2c -c public {ip} {oid}", shell=True).decode()

        # Parse the output based on requested format ('int', 'str', 'uptime')
        if parse_as == 'int':
            return int(output.split()[-1])  # For integer values (e.g., CPU, memory)
        elif parse_as == 'str':
            return output.split("STRING:")[-1].strip().strip('"')  # For string values (e.g., hostname, domain)
        elif parse_as == 'uptime':
            return int(output.split("(")[-1].split(")")[0].strip().split()[0])  # For uptime values
    except Exception as e:
        # Handle exceptions in case SNMP fetch fails
        print(f"Error fetching {oid} from {ip}: {e}")
        return None

# Function to get interface names and statuses from a router
def get_interfaces(ip):
    """Fetch interface names and statuses from the router"""
    try:
        # Fetch interface names using SNMP
        names_output = subprocess.check_output(f"snmpwalk -v2c -c public {ip} {OIDS['interfaces_name']}", shell=True).decode()
        names = {}
        # Parse interface names from SNMP output
        for line in names_output.splitlines():
            try:
                interface_index = int(line.split()[0].split('.')[-1])
                interface_name = line.split('=')[1].strip().strip('"').replace('STRING: ', '')
                names[interface_index] = interface_name
            except ValueError:
                continue  # Skip lines that don't contain valid interface information

        # Fetch interface statuses using SNMP
        status_output = subprocess.check_output(f"snmpwalk -v2c -c public {ip} {OIDS['interfaces_status']}", shell=True).decode()
        statuses = {}
        # Parse interface statuses (up/down) from SNMP output
        for line in status_output.splitlines():
            try:
                interface_index = int(line.split()[0].split('.')[-1])
                status = 'up' if 'up' in line else 'down'
                statuses[interface_index] = status
            except ValueError:
                continue  # Skip lines that don't contain valid status information

        # Combine interface names and statuses into a list of tuples
        interfaces = []
        for index in range(1, len(names) + 1):
            if index in names:
                interface_name = names.get(index, f"Unknown {index}")
                status = statuses.get(index, 'down')
                interfaces.append((interface_name, status))

        return interfaces  # Return list of interface name and status pairs
    except Exception as e:
        print(f"Error fetching interface names and statuses from {ip}: {e}")
        return []  # Return empty list in case of an error

# Define the Flask route for displaying the dashboard
@app.route("/dashboard")
def dashboard():
    router_data = []  # List to store data for each router

    # Iterate over the routers and fetch SNMP data
    for ip in ROUTERS:
        hostname = get_snmp(ip, OIDS['hostname'], 'str') or 'Unknown'
        domain = get_snmp(ip, OIDS['domain'], 'str') or 'Unknown'
        uptime = get_snmp(ip, OIDS['uptime'], 'uptime') or 0
        cpu_5s = get_snmp(ip, OIDS['cpu_5s']) or 0
        cpu_1m = get_snmp(ip, OIDS['cpu_1m']) or 0
        cpu_5m = get_snmp(ip, OIDS['cpu_5m']) or 0
        mem_total = get_snmp(ip, OIDS['mem_total']) or 1
        mem_used = get_snmp(ip, OIDS['mem_used']) or 0
        mem_percent = (mem_used / mem_total) * 100  # Calculate memory usage percentage
        iface_count = get_snmp(ip, OIDS['if_count']) or 0
        interfaces = get_interfaces(ip)  # Fetch interfaces and their status

        # Append collected data to router_data list
        router_data.append({
            'ip': ip,
            'hostname': hostname,
            'domain': domain,
            'uptime': uptime,
            'cpu': {'5s': cpu_5s, '1m': cpu_1m, '5m': cpu_5m},
            'memory': {'total': mem_total, 'used': mem_used, 'percent': mem_percent},
            'interface_count': iface_count,
            'interfaces': interfaces
        })

    # Render the dashboard template and pass the router data
    return render_template("dashboard.html", routers=router_data)

# Run the Flask app on all available IP addresses and port 8080
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
