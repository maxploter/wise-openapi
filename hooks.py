import schemathesis
from hypothesis import strategies as st
import numbers  # Import the numbers module

VALID_CURRENCIES = ["USD", "GBP", "EUR", "JPY", "CAD", "AUD"]
PROFILE_ID = 25
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
                        properties["sourceAmount"]["maximum"] = 1000_000
                        del properties["sourceAmount"]['exclusiveMinimum']
                    if "targetAmount" in properties:
                        properties["targetAmount"]["minimum"] = 10
                        properties["targetAmount"]["maximum"] = 1000_000
                        del properties["targetAmount"]['exclusiveMinimum']

            if schema and "properties" in schema:
                properties = schema["properties"]
                if "sourceCurrency" in properties:
                    properties["sourceCurrency"]["enum"] = VALID_CURRENCIES
                if "targetCurrency" in properties:
                    properties["targetCurrency"]["enum"] = VALID_CURRENCIES

        # This logic applies to path parameters.
        for parameter in operation.path_parameters:
            if parameter.name == "profileId":
                parameter.definition["schema"]["const"] = PROFILE_ID
                del parameter.definition["schema"]['minimum']
                del parameter.definition["schema"]['format']

    # --- Logic for "Recipients" tag ---

    elif primary_tag == TAG_RECIPIENTS:
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
                properties["currency"]["enum"] = VALID_CURRENCIES
            if 'type' in properties:
                properties["type"]["enum"] = ["IBAN"]
