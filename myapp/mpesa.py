import requests
import base64
from datetime import datetime
from django.conf import settings


def get_access_token():
    url = f"{settings.MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"

    credentials = f"{settings.MPESA_CONSUMER_KEY}:{settings.MPESA_CONSUMER_SECRET}"

    encoded_credentials = base64.b64encode(
        credentials.encode()
    ).decode()

    headers = {
        "Authorization": f"Basic {encoded_credentials}"
    }

    response = requests.get(url, headers=headers)

    response.raise_for_status()

    return response.json()["access_token"]
def initiate_stk_push(phone_number, amount, booking_id):
    access_token = get_access_token()

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    shortcode = settings.MPESA_SHORTCODE
    passkey = settings.MPESA_PASSKEY

    password_string = f"{shortcode}{passkey}{timestamp}"

    password = base64.b64encode(
        password_string.encode()
    ).decode()

    url = f"{settings.MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone_number,
        "PartyB": shortcode,
        "PhoneNumber": phone_number,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": "Kororio Accommodation",
        "TransactionDesc": "Accommodation Payment"  
    }

    response = requests.post(
        url,
        json=payload,
        headers=headers
    )

    response.raise_for_status()

    return response.json()