# Lambda Script
Unofficial command line app to interact with Lambda Labs official API.  Visit https://lambdalabs.com/ to sign-up and get your own API key. This script will not work without it.

# Installation
```
git clone https://github.com/cybrly/LambdaScript.git
cd LambdaScript
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
vim .env and add in your API key and SSH key name.
```

# Usage
```
python3 lambda.py -h                                                                                                                                 ─╯

    USAGE:
        python lambda.py [COMMAND] [ARGUMENT]

    COMMANDS:
        check               Check the status of running instances.
        start <number>      Start a GPU instance with the given number.
        stop <instance_id>  Terminate the instance with the given instance id.
        list                List all available GPU instances.
```
