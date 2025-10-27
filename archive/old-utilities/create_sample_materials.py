#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.simple_mock_db import SimpleMockDatabase
from app.models.material import MaterialStage, MaterialStatus
from datetime import datetime

async def create_sample_materials():
    """Create some sample materials for testing"""
    
    # Initialize the mock database
    db = SimpleMockDatabase()
    
    # Sample materials data
    sample_materials = [
        {
            "id": "sample-1",
            "title": "Product Launch Campaign",
            "description": "A comprehensive marketing campaign for our new product launch",
            "target_audience": "Tech-savvy millennials",
            "campaign_objective": "Generate awareness and drive pre-orders",
            "keywords": ["innovation", "technology", "launch", "exclusive"],
            "stage": MaterialStage.REFINEMENT,
            "status": MaterialStatus.IN_PROGRESS,
            "company_id": "demo_company_123",
            "created_by": "user_123",
            "user_id": "user_123",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "generated_images": [],
            "selected_image": None,
            "feedback": [],
            "version_history": []
        },
        {
            "id": "sample-2", 
            "title": "Social Media Content Series",
            "description": "Weekly social media posts highlighting our brand values",
            "target_audience": "Young professionals",
            "campaign_objective": "Build brand engagement and community",
            "keywords": ["social", "engagement", "community", "values"],
            "stage": MaterialStage.IDEA,
            "status": MaterialStatus.DRAFT,
            "company_id": "demo_company_123", 
            "created_by": "user_123",
            "user_id": "user_123",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "generated_images": [],
            "selected_image": None,
            "feedback": [],
            "version_history": []
        },
        {
            "id": "sample-3",
            "title": "Email Newsletter Campaign",
            "description": "Monthly newsletter highlighting company updates and insights",
            "target_audience": "Existing customers and prospects",
            "campaign_objective": "Maintain customer engagement and nurture leads",
            "keywords": ["newsletter", "insights", "updates", "engagement"],
            "stage": MaterialStage.FINALIZATION,
            "status": MaterialStatus.READY_FOR_REVIEW,
            "company_id": "demo_company_123",
            "created_by": "user_123", 
            "user_id": "user_123",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "generated_images": [],
            "selected_image": None,
            "feedback": [],
            "version_history": []
        }
    ]
    
    # Add materials to the database
    for material_data in sample_materials:
        try:
            # Store in the materials collection
            db.materials.insert_one(material_data)
            print(f"✓ Created material: {material_data['title']}")
        except Exception as e:
            print(f"✗ Error creating material {material_data['title']}: {e}")
    
    print(f"\n📊 Total materials in database: {len(db.materials.find({}))}")
    
    # List all materials
    print("\n📋 All materials:")
    for material in db.materials.find({}):
        print(f"  - {material['title']} ({material['stage']} - {material['status']})")

if __name__ == "__main__":
    asyncio.run(create_sample_materials())
