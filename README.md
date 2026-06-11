# SMSFlow Python SDK

The SMSFlow Python SDK makes it easy to send SMS messages and check SMS credit balance from backend Python applications, automation scripts, scheduled jobs, CRM integrations, ERP integrations, and operational tooling.

Documentation: https://docs.smsflow.co.za/

## Install

Package publishing is not enabled yet. During development, install locally:

```bash
pip install smsflow
```

## Configuration

Store credentials in environment variables or your platform's secret manager.

```bash
export SMSFLOW_CLIENT_ID="YOUR_CLIENT_ID"
export SMSFLOW_CLIENT_SECRET="YOUR_CLIENT_SECRET"
```

Do not put SMSFlow Client Secrets in source code, logs, notebooks, screenshots, or public issues.

## Usage

```python
import os
from smsflow import SmsFlowClient

client = SmsFlowClient(
    client_id=os.environ["SMSFLOW_CLIENT_ID"],
    client_secret=os.environ["SMSFLOW_CLIENT_SECRET"],
)

response = client.send_sms(
    campaign_name="Python SDK example",
    messages=[
        {
            "destination": "27000000000",
            "content": "Your SMSFlow Python test message was sent successfully.",
        }
    ],
)

print(response["sendResponse"]["eventId"])
```

## Features

- Get and cache SMSFlow login tokens.
- Send one or more SMS messages.
- Schedule SMS messages using UTC delivery time.
- Respect opt-out checks by default.
- Check account balance.
- Raise structured exceptions when the API returns an error.

## Local test send

This command sends a real SMS and may consume test credits:

```bash
export SMSFLOW_CLIENT_ID="YOUR_CLIENT_ID"
export SMSFLOW_CLIENT_SECRET="YOUR_CLIENT_SECRET"
export SMSFLOW_DESTINATION="27000000000"
PYTHONPATH=src python examples/send_sms.py
```

## Security

Never commit real credentials. Use environment variables or a secret manager.

## License

MIT
