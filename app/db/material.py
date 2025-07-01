from typing import List, Optional
from datetime import datetime
from app.db.base import BaseDB
from app.models.material import MaterialCreate, MaterialUpdate, MaterialStage, MaterialStatus

class MaterialDB(BaseDB):
    async def create_material(self, material: MaterialCreate, user_id: str, company_id: str) -> dict:
        material_data = material.model_dump()
        material_data.update({
            "company_id": company_id,
            "created_by": user_id,
            "generated_images": [],
            "feedback": [],
            "version_history": []
        })
        return await self.create(material_data)

    async def get_company_materials(
        self,
        company_id: str,
        stage: Optional[MaterialStage] = None,
        status: Optional[MaterialStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[dict]:
        """
        Get materials for a specific company, with optional filtering by stage and status.
        This method handles both MongoDB and SimpleMockDatabase differences.
        
        For testing the frontend with mock data, if no materials are found for test_company,
        this method will create a sample material.
        """
        query = {"company_id": company_id}
        if stage:
            query["stage"] = stage
        if status:
            query["status"] = status
            
        print(f"Getting materials for company_id: {company_id}")
        print(f"Query: {query}")
        
        # For the test company, check if we need to create sample materials
        if company_id == "test_company":
            # Get total count of materials for this company
            all_materials = []
            try:
                # Try to get all materials to check if any exist
                print("Checking for existing test_company materials")
                
                # Check if we're dealing with SimpleMockCollection
                if hasattr(self.collection, '_find_internal'):
                    # Directly use the internal method for mock DB
                    print("Using _find_internal for mock DB")
                    all_materials = self.collection._find_internal({"company_id": company_id})
                else:
                    # For real MongoDB
                    print("Using MongoDB cursor for real DB")
                    cursor = self.collection.find({"company_id": company_id})
                    
                    # Try various methods to get the cursor data
                    if hasattr(cursor, 'to_list'):
                        all_materials = await cursor.to_list(length=100)
                    elif hasattr(cursor, '__await__'):
                        all_materials = await cursor
                    else:
                        all_materials = list(cursor)
                
                # Make sure we actually have a list, not a cursor or other object
                if not isinstance(all_materials, list):
                    print(f"Warning: all_materials is not a list, it's {type(all_materials).__name__}")
                    # Try to convert to a list if possible
                    try:
                        all_materials = list(all_materials)
                    except:
                        all_materials = []
                
                material_count = len(all_materials) if all_materials else 0
                print(f"Found {material_count} existing materials for test_company")
            except Exception as e:
                print(f"Error checking for existing materials: {str(e)}")
                all_materials = []
            
            # If no materials exist, create some sample materials
            if not all_materials or len(all_materials) == 0:
                print("Creating sample materials for test_company")
                
                # Sample data
                sample_materials = [
                    {
                        "title": "Sample Marketing Email",
                        "description": "A sample email marketing campaign for product launch",
                        "target_audience": "Small business owners",
                        "campaign_objective": "Product awareness",
                        "keywords": ["email", "marketing", "launch"],
                        "stage": "idea",
                        "status": "draft",
                        "company_id": "test_company",
                        "created_by": "test_user",
                        "generated_images": [],
                        "feedback": [],
                        "version_history": []
                    },
                    {
                        "title": "Social Media Campaign",
                        "description": "Social media posts for the new product features",
                        "target_audience": "Tech enthusiasts",
                        "campaign_objective": "Feature showcase",
                        "keywords": ["social media", "features", "tech"],
                        "stage": "refinement",
                        "status": "in_progress",
                        "company_id": "test_company",
                        "created_by": "test_user",
                        "generated_images": [],
                        "feedback": [],
                        "version_history": []
                    },
                    {
                        "title": "Healthcare Brochure",
                        "description": "Brochure for healthcare professionals",
                        "target_audience": "Doctors and healthcare providers",
                        "campaign_objective": "Professional outreach",
                        "keywords": ["healthcare", "brochure", "professional"],
                        "stage": "finalization",
                        "status": "ready_for_review",
                        "company_id": "test_company",
                        "created_by": "test_user",
                        "generated_images": [],
                        "feedback": [],
                        "version_history": []
                    }
                ]
                
                # Create the sample materials
                for material in sample_materials:
                    try:
                        await self.create(material)
                    except Exception as e:
                        print(f"Error creating sample material: {str(e)}")
        
        # Now try to get the materials with proper pagination
        try:
            # Get cursor
            cursor = self.collection.find(query)
            
            # Apply skip and limit if the cursor supports these operations
            if hasattr(cursor, 'skip'):
                cursor = cursor.skip(skip).limit(limit)
            
            # Handle different types of cursors
            if hasattr(cursor, 'to_list'):
                # MongoDB AsyncIOMotorCursor has to_list
                try:
                    return await cursor.to_list(length=limit)
                except Exception as e:
                    print(f"Error using to_list: {str(e)}")
                    # Fall through to other methods
            
            # Try to await the cursor directly
            if hasattr(cursor, '__await__'):
                try:
                    results = await cursor
                    # If results is already a list, return it
                    if isinstance(results, list):
                        return results
                    # Otherwise, convert to list if possible
                    return list(results)
                except Exception as e:
                    print(f"Error awaiting cursor: {str(e)}")
                    # Fall through to other methods
            
            # Try to use as a list directly
            try:
                results = list(cursor)
                print(f"Converted cursor to list with {len(results)} items")
                return results
            except Exception as e:
                print(f"Error converting cursor to list: {str(e)}")
            
            # If nothing works, try to get all documents and filter manually
            try:
                print("Trying manual document filtering")
                all_docs = []
                # Get all documents from the collection
                cursor = self.collection.find({})
                if hasattr(cursor, 'to_list'):
                    all_docs = await cursor.to_list(length=1000)
                elif hasattr(cursor, '__await__'):
                    all_docs = await cursor
                else:
                    all_docs = list(cursor)
                
                # Print the raw documents for debugging
                print(f"All documents in the collection: {len(all_docs)}")
                for doc in all_docs:
                    print(f"  Doc ID: {doc.get('_id')} - Company: {doc.get('company_id')} - Title: {doc.get('title')}")
                
                # Filter them manually
                filtered_docs = []
                for doc in all_docs:
                    if doc.get("company_id") == company_id:
                        if stage and doc.get("stage") != stage:
                            continue
                        if status and doc.get("status") != status:
                            continue
                        filtered_docs.append(doc)
                
                # Apply pagination
                results = filtered_docs[skip:skip+limit]
                print(f"Manual filtering found {len(results)} items")
                return results
            except Exception as e:
                print(f"Error in manual filtering: {str(e)}")
            
            # If nothing works, return an empty list
            return []
        except Exception as e:
            # For testing/debugging - if materials API fails, return empty list
            print(f"Error in get_company_materials: {str(e)}")
            return []

    async def add_generated_image(
        self,
        material_id: str,
        url: str,
        prompt: str,
        ai_provider: str,
        generation_params: dict
    ) -> Optional[dict]:
        image_data = {
            "url": url,
            "prompt": prompt,
            "ai_provider": ai_provider,
            "generation_params": generation_params,
            "created_at": datetime.utcnow()
        }
        
        result = await self.collection.update_one(
            {"_id": material_id},
            {"$push": {"generated_images": image_data}}
        )
        return await self.get(material_id) if result.modified_count > 0 else None

    async def select_image(self, material_id: str, image_url: str) -> Optional[dict]:
        return await self.update(material_id, {"selected_image": image_url})

    async def add_feedback(
        self,
        material_id: str,
        user_id: str,
        comment: str
    ) -> Optional[dict]:
        feedback_data = {
            "user_id": user_id,
            "comment": comment,
            "created_at": datetime.utcnow()
        }
        
        result = await self.collection.update_one(
            {"_id": material_id},
            {"$push": {"feedback": feedback_data}}
        )
        return await self.get(material_id) if result.modified_count > 0 else None

    async def update_stage(
        self,
        material_id: str,
        stage: MaterialStage,
        status: MaterialStatus = MaterialStatus.IN_PROGRESS
    ) -> Optional[dict]:
        return await self.update(material_id, {
            "stage": stage,
            "status": status
        })
