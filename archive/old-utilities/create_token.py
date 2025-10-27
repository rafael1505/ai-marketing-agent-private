#!/usr/bin/env python3

import sys
sys.path.append('/mnt/c/Users/brc07274/OneDrive - Philips/Philips Files/BU - CI/Repository/AI Marketing Agent (Python)/ai-marketing-agent')

from app.core.auth import create_access_token
from datetime import timedelta

# Create a token that lasts for 24 hours
token_data = {
    "sub": "test-user-123",
    "company_id": "test-company-123"
}

token = create_access_token(
    data=token_data,
    expires_delta=timedelta(hours=24)
)

print(token)
