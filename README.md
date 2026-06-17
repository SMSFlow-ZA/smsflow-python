# SMSFlow Python SDK

[![PyPI version](https://img.shields.io/pypi/v/smsflow.svg)](https://pypi.org/project/smsflow/)
[![CI](https://github.com/SMSFlow-ZA/smsflow-python/actions/workflows/ci.yml/badge.svg)](https://github.com/SMSFlow-ZA/smsflow-python/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

The SMSFlow Python SDK makes it easy to send SMS messages and check SMS credit balance from backend Python applications, automation scripts, scheduled jobs, CRM integrations, ERP integrations, and operational tooling.

Documentation: https://docs.smsflow.co.za/

## Install

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

## Bulk send

```python
client.send_sms(
    campaign_name="Order dispatch alerts",
    messages=[
        {"destination": "27000000000", "content": "Order 1001 has shipped."},
        {"destination": "27000000001", "content": "Order 1002 has shipped."},
    ],
)
```

## Check balance

```python
balance = client.get_balance()
print(balance["balance"])
```

## Error handling

```python
from smsflow import SmsFlowError

try:
    client.send_sms(
        campaign_name="Transactional SMS",
        messages=[{"destination": "27000000000", "content": "Hello from SMSFlow."}],
    )
except SmsFlowError as exc:
    print(exc.status_code, exc.body)
    raise
```

## Timeouts and retries

Set a timeout when constructing the client:

```python
client = SmsFlowClient(
    client_id=os.environ["SMSFLOW_CLIENT_ID"],
    client_secret=os.environ["SMSFLOW_CLIENT_SECRET"],
    timeout=30,
)
```

Retry only temporary network failures and `5xx` responses. Do not retry validation errors, authentication failures, or insufficient-balance responses until the underlying issue has been fixed. Store the returned `eventId` against your own transaction or notification record.

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
