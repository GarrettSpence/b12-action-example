import hashlib
import hmac
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone


def build_payload():
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") + \
        f"{datetime.now(timezone.utc).microsecond // 1000:03d}Z"

    return {
        "action_run_link": os.environ["ACTION_RUN_LINK"],
        "email": os.environ["SUBMISSION_EMAIL"],
        "name": os.environ["SUBMISSION_NAME"],
        "repository_link": os.environ["REPOSITORY_LINK"],
        "resume_link": os.environ["RESUME_LINK"],
        "timestamp": timestamp,
    }


def sign_payload(body: bytes, secret: str) -> str:
    digest = hmac.new(
        secret.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()
    return f"sha256={digest}"


def main():
    signing_secret = os.environ["SIGNING_SECRET"]

    payload = build_payload()
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    signature = sign_payload(body, signing_secret)

    print(f"Payload: {body.decode('utf-8')}")
    print(f"Signature: {signature}")

    req = urllib.request.Request(
        "https://b12.io/apply/submission",
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Signature-256": signature,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            resp_body = resp.read().decode("utf-8")
            print(f"Status: {resp.status}")
            print(f"Response: {resp_body}")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}", file=sys.stderr)
        print(f"Response: {e.read().decode('utf-8')}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
