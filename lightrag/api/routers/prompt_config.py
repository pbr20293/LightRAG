"""
API router for managing prompt configuration (general vs engineering).
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from typing import List

router = APIRouter()

class PromptModeRequest(BaseModel):
    use_engineering_prompts: bool

class PromptModeResponse(BaseModel):
    use_engineering_prompts: bool
    entity_types: List[str]
    message: str = ""

@router.get("/prompt-mode", response_model=PromptModeResponse)
async def get_prompt_mode():
    """Get current prompt mode and entity types."""
    use_engineering = os.getenv("LIGHTRAG_USE_ENGINEERING_PROMPTS", "false").lower() in ("true", "1", "yes")
    
    # Import dynamically to get current entity types
    if use_engineering:
        try:
            from lightrag.entity_types_config import ENGINEERING_ENTITY_TYPES
            entity_types = ENGINEERING_ENTITY_TYPES
            message = "Engineering Standards prompt mode active"
        except ImportError:
            entity_types = ["Specification", "Standard", "Grade", "Material", "Other"]
            message = "Engineering mode active with fallback entity types"
    else:
        entity_types = ["person", "organization", "location", "event", "concept", "equipment", "product", "category", "other"]
        message = "General Knowledge Graph prompt mode active"
    
    return PromptModeResponse(
        use_engineering_prompts=use_engineering,
        entity_types=entity_types,
        message=message
    )

@router.post("/prompt-mode", response_model=PromptModeResponse)
async def set_prompt_mode(request: PromptModeRequest):
    """Set prompt mode (requires server restart to take effect)."""
    try:
        # Set the environment variable for the current session
        os.environ["LIGHTRAG_USE_ENGINEERING_PROMPTS"] = str(request.use_engineering_prompts).lower()
        
        # Get updated entity types
        if request.use_engineering_prompts:
            try:
                from lightrag.entity_types_config import ENGINEERING_ENTITY_TYPES
                entity_types = ENGINEERING_ENTITY_TYPES
                message = "Switched to Engineering Standards mode. Restart server for full effect."
            except ImportError:
                entity_types = ["Specification", "Standard", "Grade", "Material", "Other"]
                message = "Switched to Engineering mode with fallback types. Restart server for full effect."
        else:
            entity_types = ["person", "organization", "location", "event", "concept", "equipment", "product", "category", "other"]
            message = "Switched to General Knowledge Graph mode. Restart server for full effect."
        
        return PromptModeResponse(
            use_engineering_prompts=request.use_engineering_prompts,
            entity_types=entity_types,
            message=message
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set prompt mode: {str(e)}")

@router.get("/prompt-mode/entity-types", response_model=List[str])
async def get_entity_types():
    """Get current entity types based on active prompt mode."""
    use_engineering = os.getenv("LIGHTRAG_USE_ENGINEERING_PROMPTS", "false").lower() in ("true", "1", "yes")
    
    if use_engineering:
        try:
            from lightrag.entity_types_config import ENGINEERING_ENTITY_TYPES
            return ENGINEERING_ENTITY_TYPES
        except ImportError:
            return ["Specification", "Standard", "Grade", "Material", "Other"]
    else:
        return ["person", "organization", "location", "event", "concept", "equipment", "product", "category", "other"]

@router.get("/prompt-mode/status")
async def get_prompt_status():
    """Get detailed status of prompt configuration."""
    use_engineering = os.getenv("LIGHTRAG_USE_ENGINEERING_PROMPTS", "false").lower() in ("true", "1", "yes")
    
    status = {
        "mode": "engineering" if use_engineering else "general",
        "environment_variable": os.getenv("LIGHTRAG_USE_ENGINEERING_PROMPTS", "false"),
        "config_files_available": {},
        "active_prompts_loaded": False
    }
    
    # Check if config files exist
    try:
        from lightrag.entity_types_config import ENGINEERING_ENTITY_TYPES
        status["config_files_available"]["entity_types_config"] = True
        status["config_files_available"]["entity_types_count"] = len(ENGINEERING_ENTITY_TYPES)
    except ImportError:
        status["config_files_available"]["entity_types_config"] = False
    
    try:
        from lightrag.prompt_engineering_specs import PROMPTS as ENGINEERING_PROMPTS
        status["config_files_available"]["engineering_prompts"] = True
        status["config_files_available"]["prompt_count"] = len(ENGINEERING_PROMPTS)
        if use_engineering:
            status["active_prompts_loaded"] = True
    except ImportError:
        status["config_files_available"]["engineering_prompts"] = False
    
    return status