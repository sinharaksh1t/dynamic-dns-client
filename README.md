# freedns-ddns-client

A simple [FreeDNS](https://freedns.afraid.org/) client to update dynamic DNS entries.

## Usage

This code needs to be run from the server whose public IP you

1. Create a virtual environment

```
python -m venv venv
```

2. Install dependencies

```
pip install ezgmail python-dotenv
```

Note: `ezgmail` is required only if you wish to receive email notifications when the public IP has changed. Setting up `ezgmail` with the required configurations and credentials is outside the scope of this project. Refer [EZGmail documentation](https://ezgmail.readthedocs.io/en/latest/) for detailed steps to set this up.

3. Create a `.env` file and enter the following properties

```
username=your_freedns_login_username
passwd=your_freedns_login_password
recipients=your.email@example.com # This is only required if you are setting up ezgmail to receive notifications
```

4. Execute the code

```
python freedns_ddns_client.py

# If you wish to receive email notifications:
python freedns_ddns_client.py -e yes
# OR
python freedns_ddns_client.py --email yes
```
