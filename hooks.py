import schemathesis
from hypothesis import strategies as st
import numbers # Import the numbers module


VALID_CURRENCIES = ["USD", "GBP", "EUR", "JPY", "CAD", "AUD"]
PROFILE_ID = 25

@schemathesis.hook
def before_init_operation(context, operation):
    """Remove optional properties to focus tests on required fields only"""
    for alternative in operation.body:
        schema = alternative.definition.get("schema", {})
        if schema and "oneOf" in schema:
            for sub_schema in schema["oneOf"]:
                properties = sub_schema.get("properties", {})
                if "sourceAmount" in properties:
                    properties["sourceAmount"]["minimum"] = 10
                    properties["sourceAmount"]["maximum"] = 1000_000
                    properties["sourceAmount"].pop("exclusiveMinimum", None)
                if "targetAmount" in properties:
                    properties["targetAmount"]["minimum"] = 10
                    properties["targetAmount"]["maximum"] = 1000_000
                    properties["targetAmount"].pop("exclusiveMinimum", None)
        if schema and "properties" in schema:
            properties = schema["properties"]
            if "sourceCurrency" in properties:
                properties["sourceCurrency"]["enum"] = VALID_CURRENCIES
            if "targetCurrency" in properties:
                properties["targetCurrency"]["enum"] = VALID_CURRENCIES

# def remove_optional_properties(schema):
#     """Recursively remove non-required properties from schema"""
#     if not isinstance(schema, dict):
#         return
#
#     required = schema.get("required", [])
#     properties = schema.get("properties", {})
#
#     # Remove optional properties
#     for name in list(properties.keys()):
#         if name not in required:
#             del properties[name]
#
#     # Recurse into remaining properties
#     for subschema in properties.values():
#         remove_optional_properties(subschema)


@schemathesis.hook
def filter_body(context, body):
    if body and isinstance(body, dict) and 'targetAmount' in body:
        if body["targetAmount"] is not None and isinstance(body["targetAmount"], numbers.Number) and body["targetAmount"] < 1:
            return False

    if body and isinstance(body, dict) and 'sourceAmount' in body:
        if body["sourceAmount"] is not None and isinstance(body["sourceAmount"], numbers.Number) and body["sourceAmount"] < 1:
            return False

    return True

@schemathesis.hook
def map_body(context, body):
    if body and isinstance(body, dict) and 'sourceCurrency' in body:
        body["sourceCurrency"] = 'EUR'
    if body and isinstance(body, dict) and 'targetCurrency' in body:
        body["targetCurrency"] = 'GBP'
    if body and isinstance(body, dict) and 'sourceAmount' in body and body["sourceAmount"] is not None and isinstance(body["sourceAmount"], numbers.Number) and body["sourceAmount"] < 1:
        body['sourceAmount'] = 10
    if body and isinstance(body, dict) and 'targetAmount' in body and body["targetAmount"] is not None and isinstance(body["targetAmount"], numbers.Number) and body["targetAmount"] < 1:
        body['targetAmount'] = 10

    return body

@schemathesis.hook
def map_path_parameters(context, path_parameters):
    if path_parameters and isinstance(path_parameters, dict) and "profileId" in path_parameters:
        path_parameters["profileId"] = PROFILE_ID
    return path_parameters