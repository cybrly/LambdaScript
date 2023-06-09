import requests
import json
import sys

API_URL = "https://cloud.lambdalabs.com/api/v1/"
AUTH_TOKEN = "API_KEY_HERE"

def print_in_color(text, color_code):
    print(f"\033[{color_code}m{text}\033[0m")

def get_available_instances():
    response = requests.get(API_URL + "instance-types", headers={"Authorization": f"Bearer {AUTH_TOKEN}"})
    data = response.json()["data"]
    gpu_dict = {}
    for number, gpu in enumerate(data, start=1):
        if data[gpu]["regions_with_capacity_available"]:
            gpu_dict[number] = {"name": data[gpu]["instance_type"]["name"], "region": data[gpu]["regions_with_capacity_available"][0]["name"]}
    return gpu_dict

def start_instance(number):
    gpu_dict = get_available_instances()
    if number not in gpu_dict:
        print("No GPU corresponds to the number. Please list GPUs first.")
        sys.exit(1)
    data = {
        "region_name": gpu_dict[number]["region"],
        "instance_type_name": gpu_dict[number]["name"],
        "ssh_key_names": ["Chris"]
    }
    response = requests.post(API_URL + "instance-operations/launch", headers={"Authorization": f"Bearer {AUTH_TOKEN}"}, json=data)
    if response.status_code == 200:
        print_in_color("GPU instance started successfully.", "1;32")
    else:
        print("Failed to start GPU instance.")

def stop_instance(instance_id):
    url = API_URL + "instance-operations/terminate"
    payload = {"instance_ids": [instance_id]}
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        print("Instance terminated successfully.")
    else:
        print(f"Failed to terminate instance. Error: {response.text}")

def check_running_instances():
    response = requests.get(API_URL + "instances", headers={"Authorization": f"Bearer {AUTH_TOKEN}"})
    data = response.json()["data"]
    if not data:
        print_in_color("There are no GPUs currently running.", "1;31")
        return

    for instance in data:
        if instance['status'] == 'active':
            instance_type = instance['instance_type']['name']
            if instance_type.startswith("gpu_8x"):
                print_in_color(f"Instance ID: {instance['id']}, Instance Type: {instance_type}, Status: {instance['status']}", "1;32")
            else:
                print(f"Instance ID: {instance['id']}, Instance Type: {instance_type}, Status: {instance['status']}")

def print_help_menu():
    help_text = """
    USAGE:
        python script_name.py [COMMAND] [ARGUMENT]

    COMMANDS:
        check               Check the status of running instances.
        start <number>      Start a GPU instance with the given number.
        stop <instance_id>  Terminate the instance with the given instance id.
        list                List all available GPU instances.

    """
    print(help_text)

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1].lower() in ["-h", "--help"]:
        print_help_menu()
        sys.exit(0)

    command = sys.argv[1].lower()
    if command == "check":
        check_running_instances()
    elif command == "start":
        if len(sys.argv) < 3:
            print("Missing parameters for 'start'. Use 'start <number>'")
            sys.exit(1)
        start_instance(int(sys.argv[2]))
    elif command == "stop":
        if len(sys.argv) < 3:
            print("Missing parameters for 'stop'. Use 'stop <instance_id>'")
            sys.exit(1)
        stop_instance(sys.argv[2])
    elif command == "list":
        gpu_dict = get_available_instances()
        if not gpu_dict:
            print_in_color("There are no GPUs currently available. Please try again later.", "1;31")
            sys.exit(0)
        for number in gpu_dict:
            print(f"{number}. {gpu_dict[number]['name']}")
    else:
        print(f"Unknown command: {command}. Use 'check', 'start', 'stop' or 'list'")
        sys.exit(1)
