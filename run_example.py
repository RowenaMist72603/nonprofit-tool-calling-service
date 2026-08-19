"""Send one concrete campaign-close request through the local service."""

import json
import urllib.request


payload = {
    "request_id": "spring-drive-close-2026-04-30",
    "instruction": (
        "Close the Spring Drive: send Jordan Lee a $125 receipt for donation D-104, "
        "remind Casey Kim by email about the 2026-05-02T09:00:00Z shift, and record "
        "that the campaign raised $8420 from 57 donors."
    ),
}
request = urllib.request.Request(
    "http://127.0.0.1:8000/automations",
    data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(request) as response:
    print(json.dumps(json.load(response), indent=2))
