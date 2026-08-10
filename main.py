import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Rhino AI Automation Server")

# --- 1. DATABASE FOR LICENSES (20 KEYS) ---
VALID_LICENSES = {
    # Core Testing Keys
    "BETA-TESTER-01": {"active": True, "tier": "pro"},
    "UPSTACK-2026": {"active": True, "tier": "enterprise"},
    "FDS-INTERNAL": {"active": True, "tier": "pro"},
    
    # Batch 1 (Team & Research)
    "SAMAVET-PRO-01": {"active": True, "tier": "pro"},
    "SAMAVET-PRO-02": {"active": True, "tier": "pro"},
    "BRICK-ARCH-A1": {"active": True, "tier": "pro"},
    "BRICK-ARCH-A2": {"active": True, "tier": "pro"},
    "THESIS-VOXEL-99": {"active": True, "tier": "pro"},
    
    # Batch 2 (Generated Keys)
    "ARCH-A7B2-C9D4": {"active": True, "tier": "pro"},
    "ARCH-X3Y8-Z1W5": {"active": True, "tier": "pro"},
    "ARCH-K4M9-N2P6": {"active": True, "tier": "pro"},
    "ARCH-T5R1-E8Q3": {"active": True, "tier": "pro"},
    "ARCH-H7V2-J5L9": {"active": True, "tier": "pro"},
    "ARCH-F2D8-S4G1": {"active": True, "tier": "pro"},
    "ARCH-W6U3-I9O2": {"active": True, "tier": "pro"},
    "ARCH-B8N1-M4C7": {"active": True, "tier": "pro"},
    "ARCH-Q2E6-Y3U9": {"active": True, "tier": "pro"},
    "ARCH-P5A1-S8D4": {"active": True, "tier": "pro"},
    "ARCH-L9K2-J7H3": {"active": True, "tier": "pro"},
    "ARCH-G4F8-D1S6": {"active": True, "tier": "pro"}
}

# --- 2. DATA MODELS ---
class StairDimensions(BaseModel):
    tread_width: float
    riser_height: float
    total_height: float
    stair_type: str = "straight"

class PayloadRequest(BaseModel):
    session_id: str
    user_prompt: str
    previous_error: str = ""  # Added to match Rhino UI payload
    dimensions: StairDimensions
    images: List[str] = [] 
    
class LicenseRequest(BaseModel):
    key: str

# --- 3. HELPER FUNCTIONS ---
def load_skill_template(file_name: str) -> str:
    file_path = os.path.join("skills", file_name)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Skill file not found at {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

# --- 4. API ENDPOINTS ---
@app.post("/api/validate-license")
async def validate_license(request: LicenseRequest):
    if request.key in VALID_LICENSES and VALID_LICENSES[request.key]["active"]:
        return {"status": "valid", "message": "License verified successfully."}
    else:
        return {"status": "invalid", "message": "Invalid or expired license key."}

@app.post("/api/generate-task")
async def generate_task(request: PayloadRequest):
    try:
        # 1. Load the raw text file (No .format() so it doesn't break on Python brackets)
        template_text = load_skill_template("staircase_skill.txt")
        
        # 2. Safely construct the final prompt by appending the data
        final_instructions = f"""
{template_text}

--- CURRENT TASK PARAMETERS ---
User Prompt: {request.user_prompt}
Tread Width: {request.dimensions.tread_width}
Riser Height: {request.dimensions.riser_height}
Total Height: {request.dimensions.total_height}
Previous Error (if any): {request.previous_error}
"""
        return {
            "status": "success",
            "session_id": request.session_id,
            "antigravity_instructions": final_instructions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
