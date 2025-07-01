from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime

class CompanyBase(BaseModel):
    name: str
    description: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    logo_url: Optional[str] = None
    brand_colors: Optional[List[str]] = []
    
    def __init__(self, **data):
        # Ensure brand_colors is always a list
        if 'brand_colors' in data:
            if data['brand_colors'] is None:
                data['brand_colors'] = []
            elif not isinstance(data['brand_colors'], list):
                try:
                    data['brand_colors'] = list(data['brand_colors'])
                except:
                    data['brand_colors'] = []
                    
        super().__init__(**data)

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(CompanyBase):
    pass

class CompanyInDB(CompanyBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    active: bool = True
    
    # Additional debugging info
    _id: Optional[str] = None
    
    def __init__(self, **data):
        # Handle missing datetime fields with defaults
        if 'created_at' not in data or data['created_at'] is None:
            data['created_at'] = datetime.utcnow()
        if 'updated_at' not in data or data['updated_at'] is None:
            data['updated_at'] = datetime.utcnow()
        super().__init__(**data)

    class Config:
        from_attributes = True
        # Allow arbitrary types for flexible validation
        arbitrary_types_allowed = True
