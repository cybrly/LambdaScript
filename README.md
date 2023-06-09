# Lambda Script
Unofficial command line app to interact with Lambda Labs official API.  Visit https://lambdalabs.com/ to sign-up and get your own API key. This script will not work without it.

# Installation

Download repo and install requirements:
```
git clone https://github.com/cybrly/LambdaScript.git
cd LambdaScript
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

Update .env file:
```
AUTH_TOKEN="your_token"
SSH_KEY_NAMES="your_key_name"
SSH_KEY_PATH ="you_key_path"
```

# Usage
```
python3 lambda.py -h                                                                                                                                 ─╯
  USAGE:
        python lambda.py [COMMAND] [ARGUMENT]

    COMMANDS:
        list                    List all available GPU instances.
        check                   Check the status of running instances.
        start <number>          Start a GPU instance with the given number.
        stop <instance_id>      Terminate the instance with the given instance id.
        connect <instance_id>   Open an SSH connection to the instance with the given instance id.
        hashcat                 Continuously check for 'gpu_8x_a100' availability, and start it as soon as it becomes available.
```
