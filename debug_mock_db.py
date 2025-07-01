from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException
from app.db.simple_mock_db import SimpleMockDatabase
from app.models.material import MaterialStage, MaterialStatus
from app.db.material import MaterialDB

# Create a simple FastAPI app for debugging
app = FastAPI()

# Initialize mock database
mock_db = SimpleMockDatabase()

# Get the materials collection
materials_collection = mock_db.materials

# Initialize material DB
material_db = MaterialDB(materials_collection)

@app.get("/")
def read_root():
    return {"status": "Mock DB Debug API running"}

@app.get("/mock-db-state")
def get_mock_db_state():
    # Return the internal state of the mock DB
    collection_data = {}
    for name, attr in mock_db._data.items():
        collection_data[name] = {
            "count": len(attr),
            "ids": list(attr.keys())
        }
    return {
        "mock_db_state": collection_data,
        "next_id": mock_db._next_id
    }

@app.get("/create-test-material")
async def create_test_material():
    # Create a test material
    test_material = {
        "title": "Debug Test Material",
        "description": "Created for debugging the mock DB",
        "target_audience": "Developers",
        "keywords": ["test", "debug"],
        "stage": "idea",
        "status": "draft",
        "company_id": "test_company",
        "created_by": "test_user"
    }
    
    created = await material_db.create_material(
        None,  # We're not using a Pydantic model here
        "test_user",
        "test_company"
    )
    
    # After creation, get all materials
    all_materials = await list_materials()
    
    return {
        "created_material": created,
        "all_materials": all_materials,
        "mock_collection_state": list(materials_collection.data.keys()),
        "raw_data": materials_collection.data
    }

@app.get("/materials")
async def list_materials(
    stage: Optional[MaterialStage] = None,
    status: Optional[MaterialStatus] = None,
    skip: int = 0,
    limit: int = 100
):
    # List all materials with the specified filters
    materials = await material_db.get_company_materials(
        "test_company",
        stage=stage,
        status=status,
        skip=skip,
        limit=limit
    )
    
    # Return more info about the query
    return {
        "materials": materials,
        "mock_db_materials_count": len(materials_collection.data),
        "mock_db_materials_keys": list(materials_collection.data.keys()),
        "materials_count": len(materials)
    }

@app.get("/create-and-check")
async def create_and_check():
    # Create a material directly in the mock DB
    material_data = {
        "title": "Directly Created Material",
        "description": "Created directly in the mock DB",
        "target_audience": "Testers",
        "keywords": ["direct", "test"],
        "stage": "idea",
        "status": "draft",
        "company_id": "test_company",
        "created_by": "test_user",
        "generated_images": [],
        "feedback": [],
        "version_history": []
    }
    
    # Insert directly into the mock collection
    result = await materials_collection.insert_one(material_data)
    inserted_id = result.inserted_id
    
    # Now try to retrieve it in different ways
    by_id = await materials_collection.find_one({"_id": inserted_id})
    by_company = await material_db.get_company_materials("test_company")
    all_docs = list(materials_collection.data.values())
    
    # Return all the information
    return {
        "inserted_id": inserted_id,
        "by_id": by_id,
        "by_company": by_company,
        "all_docs": all_docs,
        "all_keys": list(materials_collection.data.keys())
    }

# This file can be run directly for debugging
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8099)
