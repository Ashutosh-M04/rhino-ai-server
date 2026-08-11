import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Rhino AI Automation Server")

# --- 1. DATABASE FOR LICENSES (20 KEYS) ---
# Each key now tracks a machine_id. None means it is unused and ready to be claimed.
VALID_LICENSES = {
    # Core Testing Keys
    "BETA-TESTER-01": {"active": True, "tier": "pro", "machine_id": None},
    "UPSTACK-2026": {"active": True, "tier": "enterprise", "machine_id": None},
    "FDS-INTERNAL": {"active": True, "tier": "pro", "machine_id": None},
    
    # Batch 1 (Team & Research)
    "SAMAVET-PRO-01": {"active": True, "tier": "pro", "machine_id": None},
    "SAMAVET-PRO-02": {"active": True, "tier": "pro", "machine_id": None},
    "BRICK-ARCH-A1": {"active": True, "tier": "pro", "machine_id": None},
    "BRICK-ARCH-A2": {"active": True, "tier": "pro", "machine_id": None},
    "THESIS-VOXEL-99": {"active": True, "tier": "pro", "machine_id": None},
    
    # Batch 2 (Generated Keys)
    "ARCH-A7B2-C9D4": {"active": True, "tier": "pro", "machine_id": None},
    "ARCH-X3Y8-Z1W5": {"active": True, "tier": "pro", "machine_id": None},
    "ARCH-K4M9-N2P6": {"active": True, "tier": "pro", "machine_id": None},
    "ARCH-T5R1-E8Q3": {"active": True, "tier": "pro", "machine_id": None},
    "ARCH-H7V2-J5L9": {"active": True, "tier": "pro", "machine_id": None},
    "ARCH-F2D8-S4G1": {"active": True, "tier": "pro", "machine_id": None},
    "ARCH-W6U3-I9O2": {"active": True, "tier": "pro", "machine_id": None},
    "ARCH-B8N1-M4C7": {"active": True, "tier": "pro", "machine_id": None},
    "ARCH-Q2E6-Y3U9": {"active": True, "tier": "pro", "machine_id": None},
    "ARCH-P5A1-S8D4": {"active": True, "tier": "pro", "machine_id": None},
    "ARCH-L9K2-J7H3": {"active": True, "tier": "pro", "machine_id": None},
    "ARCH-G4F8-D1S6": {"active": True, "tier": "pro", "machine_id": None}
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
    previous_error: str = ""  
    dimensions: StairDimensions
    images: List[str] = [] 
    
class LicenseRequest(BaseModel):
    key: str
    machine_id: str

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
        db_entry = VALID_LICENSES[request.key]
        
        # Scenario A: Brand new key. Lock it to the user's MAC address.
        if db_entry["machine_id"] is None:
            db_entry["machine_id"] = request.machine_id
            return {"status": "valid", "message": "License permanently locked to this PC."}
            
        # Scenario B: Returning user on the same PC. Let them in.
        elif db_entry["machine_id"] == request.machine_id:
            return {"status": "valid", "message": "License verified successfully."}
            
        # Scenario C: Someone trying to share a key on a different PC. Block them.
        else:
            return {"status": "invalid", "message": "License is already registered to another machine."}
    else:
        return {"status": "invalid", "message": "Invalid or expired license key."}

@app.post("/api/generate-task")
async def generate_task(request: PayloadRequest):
    try:
        # Load the raw text file
        template_text = load_skill_template("staircase_skill.txt")
        
        # Safely construct the final prompt by appending the data
        final_instructions = f"""
{template_text}

--- CURRENT TASK PARAMETERS ---
User Prompt: {request.user_prompt}
Tread Width: {request.dimensions.tread_width}
Riser Height: {request.dimensions.riser_height}
Total Height: {request.dimensions.total_height}
Previous Python Error (if any): {request.previous_error}
"""
        return {
            "status": "success",
            "session_id": request.session_id,
            "antigravity_instructions": final_instructions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
