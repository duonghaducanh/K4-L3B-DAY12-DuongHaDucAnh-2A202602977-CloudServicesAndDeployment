"""Print reproducible HTTP smoke evidence without exposing the API key."""
import argparse
import json
import os
import uuid

import httpx
from dotenv import load_dotenv


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--cloud", action="store_true")
    args = parser.parse_args()
    load_dotenv()
    key = os.getenv("DEPLOY_API_KEY" if args.cloud else "AGENT_API_KEY")
    with httpx.Client(base_url=args.url.rstrip("/"), timeout=60) as client:
        for path in ("/health", "/ready"):
            response = client.get(path)
            print(path, response.status_code, response.text)
            assert response.status_code == 200
        response = client.post("/ask", json={"question": "Hello"})
        print("/ask without key", response.status_code)
        assert response.status_code == 401
        if not key:
            print("Authenticated checks skipped: no service API key configured locally")
            return
        headers = {"X-API-Key": key, "X-User-Id": "smoke-" + uuid.uuid4().hex[:12]}
        for i in range(2):
            response = client.post("/ask", headers=headers, json={"question": "Docker la gi?"})
            print("/ask authenticated", response.status_code, json.dumps(response.json(), ensure_ascii=True))
            assert response.status_code == 200
            assert response.json()["history_length"] == i * 2


if __name__ == "__main__":
    main()
