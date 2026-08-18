"""
SPEC Step 2 — Database creation and schema sync (uses annex_database).
"""
from prooftest.annex_database import (  # noqa: F401
    TEMPLATE_MAP,
    generate_missing_templates,
    Database,
)
