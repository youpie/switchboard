import logging
import os
import socket
import re

import requests

WEBHOOK_NAME = os.getenv("webhook_name", "incoming_call")
PORT = 514

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', PORT))

logger = logging.getLogger("switchboard")
logging.basicConfig(level=logging.DEBUG)

logger.info("Listening for Grandstream messages, set your ATA syslog address to the IP of your Home Assistant instance...")

while True:
    data, addr = sock.recvfrom(4096)
    message = data.decode(errors='ignore')
    logger.debug(message)

    if not "startRing" in message:
        continue

    match = re.search(r'CID\s+(\d{10}),', message)
    if not match:
        continue
    phone_number = match.group(1)

    if caller_name == phone_number:
        caller_name = None

    logger.info(f"Incoming call from {phone_number}")
    headers = {
        "Authorization": f"Bearer {os.environ['SUPERVISOR_TOKEN']}"
    }
    try:
        requests.post("http://supervisor/core/api/webhook/"+ WEBHOOK_NAME, headers=headers, json={"phone_number": phone_number})
        logger.info(f"Sent webhook to endpoint {WEBHOOK_NAME}")
    except Exception as e:
        logger.error(f"Failed to send webhook to endpoint {WEBHOOK_NAME}")