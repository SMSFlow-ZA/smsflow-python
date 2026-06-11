# SMSFlow Python SDK

Draft public Python client for the SMSFlow HTTPS API.

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

## Safety

Never commit real credentials. Use environment variables or a secret manager.
