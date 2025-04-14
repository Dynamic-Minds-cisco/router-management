import subprocess
import time
import re
import requests

# Router configuration
router_ips = ['192.168.2.240', '192.168.2.241',"192.168.2.243"]  # List of router IPs to monitor
community = 'public'  # SNMP community string
interface_oid = '1.3.6.1.2.1.2.2.1.8'  # OID for interface status (used to check if the interface is up or down)

# Discord webhook URL for sending alerts
webhook_url = 'https://discord.com/api/webhooks/1360949849239064648/GE7hOSfnnDnj0LaD1ELYAB9GxPstocCxfFLWI8n8-pCjbzOOq9CKkFIcPYISkLhJRc8s'

# Store previous interface states to detect changes (e.g., up or down)
previous_states = {}

# Function to send alert to Discord (via webhook)
def send_discord_alert(message):
    """
    Sends a message to Discord via a webhook when an interface status changes.
    :param message: The message to be sent to Discord.
    """
    data = {"content": message}  # Data to be sent to Discord
    try:
        response = requests.post(webhook_url, json=data)  # Send POST request to Discord
        if response.status_code != 204:  # Check if the response is successful
            print(f"Failed to send alert: {response.status_code}, {response.text}")
    except Exception as e:  # Handle exceptions (e.g., network issues)
        print(f"Exception sending alert: {e}")

# Function to perform SNMP get operation
def snmp_get(ip, oid):
    """
    Executes an SNMP get command to fetch the status of interfaces on the router.
    :param ip: IP address of the router.
    :param oid: OID (Object Identifier) to retrieve interface status.
    :return: The output of the SNMP command or None in case of failure.
    """
    try:
        # Execute SNMP walk command and capture the output
        output = subprocess.check_output(['snmpwalk', '-v2c', '-c', community, ip, oid], timeout=3)
        return output.decode()  # Return decoded output (string format)
    except Exception as e:  # Handle exceptions if the SNMP query fails
        return None

# Function to parse interface statuses from SNMP output
def parse_interfaces(output):
    """
    Extracts the interface statuses (up or down) from the SNMP output using regular expressions.
    :param output: The SNMP output containing interface statuses.
    :return: A list of interface statuses (up or down).
    """
    return re.findall(r'INTEGER: (\w+)', output) if output else []  # Regular expression to extract statuses

# Main loop to monitor routers
def monitor():
    """
    Main monitoring loop that continuously checks the router interfaces' status.
    Sends alerts when there is a status change (up/down).
    """
    while True:
        # Iterate over each router IP in the list
        for ip in router_ips:
            output = snmp_get(ip, interface_oid)  # Get the SNMP output for the specified OID
            current_status = 'down'  # Default to 'down' if no output is received
            interfaces = parse_interfaces(output)  # Parse the output to extract interface statuses

            # Check if the output contains 'up' to set the current status
            if output:
                if 'up' in output.lower():
                    current_status = 'up'
            else:
                current_status = 'down'  # If no output, assume the interface is down

            # Check if the status has changed compared to the previous state
            prev = previous_states.get(ip)  # Get the previous state from the dictionary
            if prev != current_status:  # If the status has changed
                # Send an alert to Discord
                send_discord_alert(f"⚠️ Router {ip} is now {current_status.upper()} (was {prev.upper() if prev else 'UNKNOWN'})")
                previous_states[ip] = current_status  # Update the previous state
            else:
                # No change, print status for the router
                print(f"No change for {ip}, still {current_status}")

        time.sleep(10)  # Sleep for 10 seconds before checking again (can adjust frequency here)

# Entry point to run the monitoring function
if __name__ == "__main__":
    monitor()  # Start the monitoring loop
