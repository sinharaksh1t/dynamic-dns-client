"""
A FreeDNS dynamic DNS client
"""

import argparse
import hashlib
import logging
import os
import sys

import ezgmail
import requests
from dotenv import load_dotenv

logr = logging.getLogger(__name__)


PUBLIC_IP_FILE = "my_public_ip.txt"


def init_logger():
    """Setup logging configuration"""
    logging.basicConfig(
        format="%(levelname)s %(asctime)s: %(message)s",
        filename="app.log",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
        style="%",
    )


def what_is_my_public_ip():
    """Fetch your public IP"""
    logr.info("Fetching current public IP")
    resp = requests.get("https://ipinfo.io/ip")
    if resp.status_code >= 300:
        logr.error("Unexpected error. Unable to fetch the current public IP.")
        sys.exit(1)

    return resp.text


def what_is_my_cached_ip():
    """Fetch your cached public IP"""
    logr.info("Fetching cached public IP")
    try:
        with open(PUBLIC_IP_FILE, "r", encoding="utf-8") as file:
            cached_public_ip = file.readline()
    except FileNotFoundError:
        # If the file is not found, create an empty one
        with open(PUBLIC_IP_FILE, "w", encoding="utf-8") as _:
            pass
        cached_public_ip = ""

    if len(cached_public_ip) == 0:
        logr.info("No cached public IP found")

    return cached_public_ip


def send_email_notification(cached, current):
    """Send email notification"""
    logr.info("Sending email notification")

    # Use command separated recipients if you want more than one
    recipients = os.getenv("recipients")
    if recipients is None:
        logr.error("Recipients list cannot be empty. No email notification sent.")
        return
    subject = "Public IP change notification"
    body = f"Your public IP has probably changed. Cached: {cached}, Current: {current}"
    try:
        ezgmail.send(recipients, subject, body, mimeSubtype="html")
    except Exception as e:
        logr.error("Unexpected Error occurred while sending email: %e", e)
        print(
            "Unexpected Errror occurred. Check the log file `app.log` for more details"
        )
        sys.exit(1)

    logr.info("Email sent successfully")


def sha1_encode(string):
    """Sha1 encode update token"""
    # Encodes a string using SHA1 and returns the hex digest.
    hash_object = hashlib.sha1(string.encode("utf-8"))
    return hash_object.hexdigest()


def update_public_ip_freedns():
    """Update FreeDNS public IP"""
    logr.info("Updating the dynamic DNS record")

    # Get the username and password from env
    username = os.getenv("username")
    passwd = os.getenv("passwd")
    if username is None or passwd is None:
        logr.error("Username or password cannot be empty. Check .env file and retry")
        print(
            "Unexpected Errror occurred. Check the log file `app.log` for more details"
        )
        sys.exit(1)

    decoded_token = f"{username}|{passwd}"
    encoded_token = sha1_encode(decoded_token)

    get_update_url = (
        f"https://freedns.afraid.org/api/?action=getdyndns&v=2&sha={encoded_token}"
    )
    resp = requests.get(get_update_url)
    candidates = resp.text.split("\n")
    url_text = ""
    if len(candidates) > 1:
        domain = os.getenv("domain")
        if domain is None:
            logr.error(
                "You have multiple FreeDNS domains, the `domain` field in .env file is required."
            )
            print(
                "Unexpected Errror occurred. Check the log file `app.log` for more details"
            )
            sys.exit(1)
        for candidate in candidates:
            if domain in candidate:
                url_text = candidate
        if url_text == "":
            logr.error(
                "The provided domain %s is not found in your list of FreeDNS domains.",
                domain,
            )
            print(
                "Unexpected Errror occurred. Check the log file `app.log` for more details"
            )
            sys.exit(1)
    elif len(candidates) == 1:
        url_text = resp.text
    else:
        logr.error("Unexpected error occurred. No FreeDNS domains found.")
        print(
            "Unexpected Errror occurred. Check the log file `app.log` for more details"
        )
        sys.exit(1)

    update_url = url_text.split("|")[-1]

    update_resp = requests.get(update_url)
    logr.info(update_resp.text)


def update_public_ip_cache(current_public_ip):
    """Update the cached public IP"""
    logr.info("Updating the local cache")
    with open(PUBLIC_IP_FILE, "w", encoding="utf-8") as file:
        file.write(current_public_ip)

    logr.info("Cached IP updated successfully")


def parse_arguments():
    """Parse command line arguments"""
    # Parsing command line arugments
    parser = argparse.ArgumentParser(
        description="Parse the command line arguments for this client"
    )
    parser.add_argument(
        "-e",
        "--email",
        default="no",
        type=str,
        choices=["yes", "no"],
        required=False,
        help="Set this flag to 'yes' to receive email notifications when public IP has changed. NOTE: You need the module ezgmail to be installed and instantiated for this option to work.",
    )
    args = parser.parse_args()
    return args


def run():
    """Main method"""
    init_logger()
    load_dotenv()  # This line brings all environment variables from .env into os.getenv
    args = parse_arguments()
    logr.info("Starting dynamic dns client")

    # Fetch current public IP address
    current_public_ip = what_is_my_public_ip()
    logr.info("Current public IP: %s", current_public_ip)

    # Fetch cached public IP address
    cached_public_ip = what_is_my_cached_ip()
    logr.info("Cached public IP: %s", cached_public_ip)

    # Check if the current matches the cached
    if cached_public_ip != current_public_ip:
        logr.info("Public IP has changed, starting to update the cache and DDNS IP")
        # Send Notification email if the --email flag is set
        if args.email == "yes":
            send_email_notification(cached_public_ip, current_public_ip)

        # Update public IP on freedns
        update_public_ip_freedns()

        # Update public IP in the file
        update_public_ip_cache(current_public_ip)
    else:
        print("Public IP has not changed, no updates required")


if __name__ == "__main__":
    run()
