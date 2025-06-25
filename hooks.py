import schemathesis
from hypothesis import strategies as st

VALID_CURRENCIES = ["USD", "GBP", "EUR", "JPY", "CAD", "AUD"]
PROFILE_ID = 25

@schemathesis.hook
def map_body(context, body):
    if body and isinstance(body, dict) and 'sourceCurrency' in body:
        body["sourceCurrency"] = 'EUR'
    if body and isinstance(body, dict) and 'targetCurrency' in body:
        body["targetCurrency"] = 'GBP'
    if body and isinstance(body, dict) and 'sourceAmount' in body and body["sourceAmount"] and body["sourceAmount"] < 1:
        body['sourceAmount'] = 10
    if body and isinstance(body, dict) and 'targetAmount' in body and body["targetAmount"] and body["targetAmount"] < 1:
        body['targetAmount'] = 10

    return body

@schemathesis.hook
def map_path_parameters(context, path_parameters):
    if path_parameters and isinstance(path_parameters, dict) and "profileId" in path_parameters:
        path_parameters["profileId"] = PROFILE_ID
    return path_parameters