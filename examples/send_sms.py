import os

from smsflow import SmsFlowClient


def main() -> int:
    client_id = os.getenv("SMSFLOW_CLIENT_ID")
    client_secret = os.getenv("SMSFLOW_CLIENT_SECRET")
    destination = os.getenv("SMSFLOW_DESTINATION")

    if not client_id or not client_secret or not destination:
        print("Set SMSFLOW_CLIENT_ID, SMSFLOW_CLIENT_SECRET, and SMSFLOW_DESTINATION before running.")
        return 1

    client = SmsFlowClient(client_id=client_id, client_secret=client_secret)
    response = client.send_sms(
        campaign_name="Python SDK sample",
        messages=[
            {
                "destination": destination,
                "content": "Your SMSFlow Python SDK test message was sent successfully.",
            }
        ],
    )
    print(response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
