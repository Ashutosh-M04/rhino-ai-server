import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# ==========================================
# SECTION 1: SERVER INITIALIZATION
# ==========================================
app = FastAPI(title="Rhino AI Automation Server")


# ==========================================
# SECTION 2: INPUT DATA MODELS (Validation)
# ==========================================
class StairDimensions(BaseModel):
    tread_width: float
    riser_height: float
    total_height: float
    stair_type: str = "straight"

class PayloadRequest(BaseModel):
    session_id: str
    user_prompt: str
    dimensions: StairDimensions


# ==========================================
# SECTION 3: HELPER FUNCTIONS
# ==========================================
def load_skill_template(file_name: str) -> str:
    # This automatically looks inside your "skills" folder
    file_path = os.path.join("skills", file_name)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Skill file not found at {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


# ==========================================
# SECTION 4: API ENDPOINT (The Bridge Logic)
# ==========================================
@app.post("/api/generate-task")
async def generate_task(request: PayloadRequest):
    try:
        # 1. Load the text template from skills/staircase_skill.txt
        template_text = load_skill_template("staircase_skill.txt")

        # 2. Inject incoming request data into the template placeholders
        final_instructions = template_text.format(
            session_id=request.session_id,
            user_prompt=request.user_prompt,
            tread_width=request.dimensions.tread_width,
            riser_height=request.dimensions.riser_height,
            total_height=request.dimensions.total_height
        )

        # 3. Print the formatted result to the terminal console
        print("\n================ INSTRUCTIONS GENERATED ================")
        print(final_instructions)
        print("========================================================\n")

        # 4. Return the response payload as clean JSON
        return {
            "status": "success",
            "session_id": request.session_id,
            "antigravity_instructions": final_instructions
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))