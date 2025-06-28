import schemathesis
import os
from hypothesis import strategies as st
import numbers  # Import the numbers module

VALID_CURRENCIES = ["USD", "GBP", "EUR", "JPY", "CAD", "AUD"]
TARGET_CURRENCY = 'GBP'
SOURCE_CURRENCY = 'EUR'
PROFILE_ID = 25  # TODO move to env variable
TAG_QUOTES = "Quotes"
TAG_RECIPIENTS = "Recipients"

@schemathesis.hook
def before_init_operation(context, operation):
    """
    Modify the data generation strategies before any test cases are created.
    This is more efficient than mapping values after they are generated.

    This hook inspects the tags of an operation and applies specific
    constraints to the request body schema based on the tag.
    """
    if not operation.tags:
        return
    primary_tag = operation.tags[0]

    # --- Logic for "Quotes" tag ---
    if primary_tag == TAG_QUOTES:
        # This logic applies to POST/PUT/PATCH requests which have a body.
        for alternative in operation.body:
            schema = alternative.definition.get("schema", {})

            if schema and "oneOf" in schema:
                for sub_schema in schema["oneOf"]:
                    properties = sub_schema.get("properties", {})
                    if "sourceAmount" in properties:
                        properties["sourceAmount"]["minimum"] = 10
                        properties["sourceAmount"]["maximum"] = 1_000_000
                        del properties["sourceAmount"]['exclusiveMinimum']
                    if "targetAmount" in properties:
                        properties["targetAmount"]["minimum"] = 10
                        properties["targetAmount"]["maximum"] = 1_000_000
                        del properties["targetAmount"]['exclusiveMinimum']

            if schema and "properties" in schema:
                properties = schema["properties"]
                if "sourceCurrency" in properties:
                    properties["sourceCurrency"]["enum"] = [SOURCE_CURRENCY]
                    del properties["sourceCurrency"]['example']
                    del properties["sourceCurrency"]['pattern']
                    del properties["sourceCurrency"]['minLength']
                    del properties["sourceCurrency"]['maxLength']
                if "targetCurrency" in properties:
                    properties["targetCurrency"]["enum"] = [TARGET_CURRENCY]
                    del properties["targetCurrency"]['example']
                    del properties["targetCurrency"]['pattern']
                    del properties["targetCurrency"]['minLength']
                    del properties["targetCurrency"]['maxLength']

        # This logic applies to path parameters.
        for parameter in operation.path_parameters:
            if parameter.name == "profileId":
                parameter.definition["schema"]["enum"] = [str(PROFILE_ID)]
                parameter.definition["schema"]["type"] = 'string'
                del parameter.definition["schema"]['minimum']
                del parameter.definition["schema"]['format']

    # --- Logic for "Recipients" tag ---

    elif primary_tag == TAG_RECIPIENTS:
        # Set currency parameter to TARGET_CURRENCY for list recipients endpoint
        if operation.method.lower().strip() == "get" and "/v2/accounts" == operation.path.lower().strip():
            for parameter in operation.query:
                if parameter.name == "currency":
                    parameter.definition["schema"]["enum"] = [TARGET_CURRENCY]

        # This logic applies to POST/PUT/PATCH requests which have a body.
        for alternative in operation.body:
            schema = alternative.definition.get("schema", {})
            properties = schema.get("properties", {})

            if "profile" in properties:
                properties["profile"]["const"] = PROFILE_ID
                del properties["profile"]['example']
                del properties["profile"]['minimum']
                del properties["profile"]['format']
            if 'currency' in properties:
                properties["currency"]["enum"] = [TARGET_CURRENCY]
                del properties["currency"]['example']
                del properties["currency"]['pattern']
                del properties["currency"]['minLength']
                del properties["currency"]['maxLength']

            if 'type' in properties:
                properties["type"]["enum"] = ["email"]
                del properties["type"]['example']
            if 'accountHolderName' in properties:
                properties["accountHolderName"]["const"] = 'Openapi TestUser'
                del properties["accountHolderName"]['example']
            if 'ownedByCustomer' in properties:
                del properties["ownedByCustomer"]

            if operation.method.lower().strip() == "post" and "/v1/accounts" == operation.path.lower().strip():
                properties["details"] = {"type": "object", "properties": {}, "required": ['email'], 'additionalProperties': False}
                properties["details"]["properties"]["email"] = {
                    "type": "string",
                    "const": "Openapi@TestUser.ee"
                }
                # Make details required and email required within details
                required = schema.get("required", [])
                if "details" not in required:
                    required.append("details")
                if 'example' in schema:
                    del schema['example']
                if 'additionalProperties' in schema:
                    schema['additionalProperties'] = False