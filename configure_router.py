from netmiko import ConnectHandler
import yaml
import sys

def load_devices():
    try:
        with open("devices.yaml") as file:
            return yaml.safe_load(file)["devices"]
    except Exception as e:
        print(f"❌ Error loading devices.yaml: {e}")
        sys.exit(1)

def connect_to_device(device_details):
    try:
        connection = ConnectHandler(
            device_type=device_details["device_type"],
            host=device_details["ip"],
            username=device_details["username"],
            password=device_details["password"],
            secret=device_details["enable_password"],
            timeout=10
        )
        connection.enable()
        return connection
    except Exception as e:
        print(f"❌ Failed to connect to device: {e}")
        return None

def show_menu():
    print("\nRouter Configuration Menu")
    print("1. Basic Interface Configuration")
    print("2. OSPF Configuration")
    print("3. VLAN Configuration")
    print("4. Backup Configuration")
    print("5. Restore Configuration")
    print("6. Show Running Config")
    print("7. Exit")
    return input("Select an option (1-7): ")

def basic_interface_config(connection):
    print("\nBasic Interface Configuration")
    interface = input("Enter interface name (e.g., Gig0/1): ")
    ip_address = input("Enter IP address (e.g., 192.168.1.1): ")
    subnet = input("Enter subnet mask (e.g., 255.255.255.0): ")
    description = input("Enter description (optional): ")
    
    commands = [
        f"interface {interface}",
        f"ip address {ip_address} {subnet}",
        f"description {description}" if description else "no shutdown"
    ]
    
    output = connection.send_config_set(commands)
    print("\nConfiguration applied:")
    print(output)

def ospf_config(connection):
    print("\nOSPF Configuration")
    process_id = input("Enter OSPF process ID (e.g., 1): ")
    network = input("Enter network to advertise (e.g., 192.168.1.0): ")
    wildcard = input("Enter wildcard mask (e.g., 0.0.0.255): ")
    area = input("Enter area ID (e.g., 0): ")
    
    commands = [
        "router ospf " + process_id,
        f"network {network} {wildcard} area {area}"
    ]
    
    output = connection.send_config_set(commands)
    print("\nOSPF configuration applied:")
    print(output)

def vlan_config(connection):
    print("\nVLAN Configuration")
    vlan_id = input("Enter VLAN ID (e.g., 10): ")
    name = input("Enter VLAN name (e.g., SALES): ")
    interface = input("Enter interface to assign (e.g., Gig0/1): ")
    
    commands = [
        f"vlan {vlan_id}",
        f"name {name}",
        f"interface {interface}",
        "switchport mode access",
        f"switchport access vlan {vlan_id}"
    ]
    
    output = connection.send_config_set(commands)
    print("\nVLAN configuration applied:")
    print(output)

def backup_config(connection, device_name):
    config = connection.send_command("show running-config")
    filename = f"{device_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(filename, "w") as file:
        file.write(config)
    
    print(f"\n✅ Configuration backed up to {filename}")

def restore_config(connection):
    filename = input("Enter backup filename to restore: ")
    
    try:
        with open(filename, "r") as file:
            config = file.read()
        
        # Send configuration line by line
        output = connection.send_config_set(config.split('\n'))
        connection.save_config()
        print("\n✅ Configuration restored successfully")
        print(output)
    except Exception as e:
        print(f"❌ Error restoring configuration: {e}")

def main():
    devices = load_devices()
    
    print("Available devices:")
    for i, device in enumerate(devices.keys(), 1):
        print(f"{i}. {device}")
    
    choice = input("Select device to configure (1-{}): ".format(len(devices)))
    try:
        device_name = list(devices.keys())[int(choice)-1]
        device_details = devices[device_name]
    except:
        print("❌ Invalid selection")
        return
    
    connection = connect_to_device(device_details)
    if not connection:
        return
    
    try:
        while True:
            option = show_menu()
            
            if option == "1":
                basic_interface_config(connection)
            elif option == "2":
                ospf_config(connection)
            elif option == "3":
                vlan_config(connection)
            elif option == "4":
                backup_config(connection, device_name)
            elif option == "5":
                restore_config(connection)
            elif option == "6":
                running_config = connection.send_command("show running-config")
                print("\nCurrent running configuration:")
                print(running_config)
            elif option == "7":
                print("Exiting...")
                break
            else:
                print("❌ Invalid option, please try again")
                
            input("\nPress Enter to continue...")
            
    finally:
        connection.disconnect()
        print("Disconnected from device")

if __name__ == "__main__":
    from datetime import datetime
    main()