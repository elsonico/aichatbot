"""Gunicorn configuration file."""

import multiprocessing

# Basic binding - IP and port
bind = "0.0.0.0:5004"

workers = multiprocessing.cpu_count() * 2 + 1
threads = 2
timeout = 120

# SSL Configuration
certfile = '/etc/letsencrypt/live/vauva.ampiainen.net/fullchain.pem'
keyfile = '/etc/letsencrypt/live/vauva.ampiainen.net/privkey.pem'
ssl_version = "TLSv1_2"

if certfile and keyfile:
    bind = f"0.0.0.0:5004"  # Ensure the bind is to the right IP and port
    cert_reqs = 0  # This specifies requirements for the client certificates, 0 means no requirements
    ciphers = "ECDHE-RSA-AES128-GCM-SHA256"  # This is an example set of ciphers. Adjust according to your security needs.

