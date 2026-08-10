import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Rhino AI Automation Server")

# --- 1. MOCK DATABASE FOR LICENSES ---
# You can issue these to your users. 
VALID_LICENSES = {
    "BETA-TESTER-01": {"active": True, "tier": "pro"},
    "UPSTACK-2026": {"active": True, "tier": "enterprise"},
    "FDS-INTERNAL": {"active": True, "tier": "pro"}
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
    dimensions: StairDimensions
    
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

# NEW: License Validation Endpoint
@app.post("/api/validate-license")
async def validate_license(request: LicenseRequest):
    if request.key in VALID_LICENSES and VALID_LICENSES[request.key]["active"]:
        return {"status": "valid", "message": "License verified successfully."}
    else:
        return {"status": "invalid", "message": "Invalid or expired license key."}

# EXISTING: Generator Endpoint
@app.post("/api/generate-task")
async def generate_task(request: PayloadRequest):
    try:
        template_text = load_skill_template("staircase_skill.txt")
        final_instructions = template_text.format(
            session_id=request.session_id,
            user_prompt=request.user_prompt,
            tread_width=request.dimensions.tread_width,
            riser_height=request.dimensions.riser_height,
            total_height=request.dimensions.total_height
        )
        return {
            "status": "success",
            "session_id": request.session_id,
            "antigravity_instructions": final_instructions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
