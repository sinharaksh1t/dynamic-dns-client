# FreeDNS Dynamic DNS Client

A [FreeDNS](https://freedns.afraid.org/) client to update dynamic DNS entries.

## Usage

The client needs to be run from the host whose dynamic public IP needs to be updated as your FreeDNS domain entry.

1. Create a virtual environment and activate it

```
python -m venv venv

source venv/bin/activate
```

2. Install dependencies

```
pip install ezgmail python-dotenv
```

Note: `ezgmail` is required only if you wish to receive email notifications when the public IP has changed. By default the client will not send email notification since this requires `ezgmail` to be configured appropriately. Setting up `ezgmail` with the required configurations and credentials is outside the scope of this project. Refer [EZGmail documentation](https://ezgmail.readthedocs.io/en/latest/) for detailed steps to set this up if you'd like to receive email notifications. If not, you can skip this part and simply continue using the client with its default settings.

3. Create a `.env` file and enter the following properties (Note: This file is gitignored so the credentials are not uploaded anywhere, they're safe in your local machine where only you have access to it)

```
username=your_freedns_login_username
passwd=your_freedns_login_password
domain=your.freednsdomain.com # This is only required if you have multiple FreeDNS domains and they're UN-Linked
recipients=your.email@example.com # This is only required if you have set up ezgmail to receive notifications
```

NOTE: If you have multiple FreeDNS domains for different machines having different public IPs, then make sure that the settings on your [home page](https://freedns.afraid.org/dynamic/index.php) is set to: `Link updates of the same IP together? Currently UN-Linked/OFF`
If it says `Currently Linked/ON` FreeDNS will update all the domains with the public IP of the machine from which this code is run.

4. Execute the code

```
python freedns_ddns_client.py

# If you wish to receive email notifications:
python freedns_ddns_client.py -e yes
# OR
python freedns_ddns_client.py --email yes
```
