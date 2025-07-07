from google.oauth2.service_account import Credentials
import time
from requests.exceptions import SSLError
import numpy as np
import os, io, requests, json
import pandas as pd
from typing import List
import gspread, time
from requests.exceptions import SSLError
from google.oauth2.service_account import Credentials
import google.auth.exceptions
import base64

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
b64_creds = os.getenv("GOOGLE_CREDS_B64")

if not b64_creds:
    raise Exception("Missing GOOGLE_CREDS_B64 in environment.")

creds_dict = json.loads(base64.b64decode(b64_creds).decode("utf-8"))



def get_credentials_with_retry(retries=3):
    for i in range(retries):
        try:
            return Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        except (google.auth.exceptions.TransportError, SSLError) as e:
            print(f"Retrying auth ({i+1}/{retries}): {e}")
            time.sleep(2 ** i)
    raise Exception("Failed to authenticate after retries.")
