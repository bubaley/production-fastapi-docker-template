"""Product identity on the backend: rename the product here and nowhere else (`make init` rewrites it).

The frontend counterpart is `frontend/app/app.config.ts`. Infrastructure names (image, compose project, database)
are separate and also written by `make init`.
"""

PRODUCT_NAME = 'FastAPI + Nuxt Template'
"""Human-readable product name: the API title in OpenAPI and the interactive docs."""

PRODUCT_DESCRIPTION = 'REST API of the product.'
"""One-line API description shown in OpenAPI."""
