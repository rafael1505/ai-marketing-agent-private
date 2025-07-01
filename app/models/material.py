from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class MaterialStage(str, Enum):
    IDEA = "idea"
    REFINEMENT = "refinement"
    FINALIZATION = "finalization"

class MaterialStatus(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    READY_FOR_REVIEW = "ready_for_review"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class GeneratedImage(BaseModel):
    url: str
    prompt: str
    ai_provider: str
    generation_params: dict
    created_at: datetime

class MaterialBase(BaseModel):
    title: str
    description: Optional[str] = None
    target_audience: Optional[str] = None
    campaign_objective: Optional[str] = None
    keywords: List[str] = []
    stage: MaterialStage
    status: MaterialStatus

class MaterialCreate(MaterialBase):
    pass

class MaterialUpdate(MaterialBase):
    pass

class MaterialInDB(MaterialBase):
    id: str
    company_id: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    generated_images: List[dict] = []  # Using dict instead of GeneratedImage for more flexibility
    selected_image: Optional[str] = None
    feedback: List[dict] = []
    version_history: List[dict] = []
    content: Optional[str] = None  # Add content field
    marketing_goal: Optional[str] = None  # Add marketing goal

    # Special fields for compatibility
    _id: Optional[str] = None  # MongoDB uses _id

    class Config:
        from_attributes = True
        populate_by_name = True  # Allow populating from aliases
        # Allow extra fields from the database
        extra = "ignore"
