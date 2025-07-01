#!/usr/bin/env python3
"""
Custom JSON utilities for handling datetime serialization
"""

import json
from datetime import datetime, date
from typing import Any, Dict, List, Union, Optional

class DateTimeEncoder(json.JSONEncoder):
    """
    Custom JSON encoder that handles datetime and date objects by converting them to ISO format strings.
    """
    def default(self, obj: Any) -> Any:
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)


def convert_datetime_to_isoformat(obj: Any) -> Any:
    """
    Recursively convert datetime objects in a dictionary or list to ISO format strings
    """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: convert_datetime_to_isoformat(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_datetime_to_isoformat(item) for item in obj]
    else:
        return obj
