# Mail-N-Message API (mnm-api)

Mail-N-message API is REST API using which someone can schedule tasks to send mail and sms through computer programs. The API makes use of way2sms API to send text messages and Flask_mail module to send emails.

## Usage

```python

import requests, json

request = {
    'datetime':{
        'year': 2019 #int,
        'month': 11 #int,
        'day': 29 #int,
        'hour': 19 #int - 24 hour format,
        'minute': 12 #int,
        'second': 0 #int,
    },
    'message': 'Hello' #str,
    'mail':{
        'to': ['abc@gmail.com', 'xyz@gmail.com'], # list of strings
        'from': 'pqr@gmail.com', #str
        'subject': 'test mail', #str
    },
    'sms':{
        'to': '<recipient mobile number with country code eg: +911234567890>', #str
        'from': '<sender mobile number with country code eg: +911234567890>', #str
        'apikey': '<your-way2sms-apikey>', #str
        'secret': '<your-way2sms-secret>' #str
    }
}

api_url = ' https://mnm-api-v1.herokuapp.com/v1/mail'
r = requests.post(api_url, data = json.dumps(request), headers = {'Content-Type': 'application/json'})
print(r.status_code)
print(r.json())

```

Credits

Created and Developed by: [Gagan Talreja](https://gagantalreja.github.io/)
Contact: gtcms1@gmail.com
