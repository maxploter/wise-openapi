# wise-openapi
An OpenAPI specification for the Wise (TransferWise) API.


# Wise (TransferWise) OpenAPI Specification

This repository contains OpenAPI specifications for [Wise's API](https://docs.wise.com/api-docs/api-reference).

[Changelog](https://github.com/maxploter/wise-openapi/releases)

Files can be found in the openapi/ directory:

spec.yaml: OpenAPI 3.0 spec matching the public Stripe API.

The specs provided in this repository do explicity target openapi-generator.

# Development

## Testing with Schemathesis

```shell
conda create -n wise-openapi python=3.11
conda activate wise-openapi
conda install conda-forge::schemathesis

export SCHEMATHESIS_HOOKS=hooks
export WISE_API_TOKEN='{TOKEN}'

schemathesis run --url https://api.sandbox.transferwise.tech \
  --exclude-checks unsupported_method,not_a_server_error,missing_required_header,negative_data_rejection \
  --report har \
  openapi/spec.yaml
```