import os
from datetime import datetime, timezone
from uuid import uuid4

from smsflow import SmsFlowClient


def main() -> int:
    client_id = os.getenv("SMSFLOW_CLIENT_ID")
    client_secret = os.getenv("SMSFLOW_CLIENT_SECRET")
    destination = os.getenv("SMSFLOW_DESTINATION")

    if not client_id or not client_secret or not destination:
        print("Set SMSFLOW_CLIENT_ID, SMSFLOW_CLIENT_SECRET, and SMSFLOW_DESTINATION before running.")
        return 1

    base_url = os.getenv("SMSFLOW_BASE_URL", "https://portal.smsflow.co.za/")
    client = SmsFlowClient(client_id=client_id, client_secret=client_secret, base_url=base_url)
    run_id = f"{uuid4().hex[:12]}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    response = client.send_sms(
        campaign_name="Python SDK sample",
        messages=[
            {
                "destination": destination,
                "content": f"Your SMSFlow Python SDK test message was sent successfully. Run {run_id}.",
            }
        ],
    )
    print(response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
