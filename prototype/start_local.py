"""Load the ignored test SMTP settings and start the local prototype; no email on startup."""

import argparse
import json
import os
import secrets
from pathlib import Path

import server


def main():
    """Load configuration into this process, check it, then optionally run the API.

    Reads .env.smtp.json beside this script. The password is plaintext on disk;
    it is never printed. --check-config validates format without network I/O.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-config", action="store_true", help="Validate local settings without connecting or sending.")
    args = parser.parse_args()
    path = Path(__file__).resolve().with_name(".env.smtp.json")
    config = json.loads(path.read_text(encoding="utf-8-sig"))
    fields = {"HOST": "host", "PORT": "port", "MODE": "mode", "USER": "user",
              "FROM": "sender", "TO": "recipient", "PASSWORD": "password"}
    for target, source in fields.items():
        os.environ["SMTP_" + target] = str(config[source])
    try:
        server.smtp_settings()
        if len(os.environ["SMTP_PASSWORD"]) != 16:
            print("Warning: saved Gmail app password is not 16 characters; authentication may fail.")
        if args.check_config:
            print("SMTP configuration format checked; no network connection made and no email sent.")
            return
        os.environ["API_TOKEN"] = os.environ.get("API_TOKEN") or secrets.token_urlsafe(32)
        print("API token for your local client terminal:", os.environ["API_TOKEN"], flush=True)
        server.main()
    finally:
        os.environ.pop("SMTP_PASSWORD", None)


if __name__ == "__main__":
    main()
