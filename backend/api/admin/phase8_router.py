"""
Phase 8.1A - AI-Assisted Admin Tools Router
Endpoints for AI blog assistance, notifications, and workflow automation
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from .permissions import get_current_admin, require_admin_or_above
from .phase8_ai import ai_assistant
from .phase8_notifications import notification_engine
from .phase8_workflows import workflow_engine
from .phase8_analytics import analytics_engine
from .utils import log_admin_action
import os
from pymongo import MongoClient
from fastapi.responses import Response

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = MongoClient(MONGO_URL)
db = client[os.environ.get('DB_NAME', 'test_database')]

router = APIRouter(prefix="/api/admin/phase8", tags=["Phase 8 - Intelligence & Automation"])

# ==========================================
# PYDANTIC MODELS
# ==========================================

class BlogDraftRequest(BaseModel):
    topic: str = Field(..., description="Main topic for the blog")
    keywords: Optional[List[str]] = Field(None, description="Keywords to include")
    tone: str = Field("professional", description="Tone: professional, casual, friendly")
    length: str = Field("medium", description="Length: short, medium, long")

class ContentImprovementRequest(BaseModel):
    content: str = Field(..., description="Content to improve")
    improvement_type: str = Field("general", description="Type: general, clarity, engagement, tone")

class TagSuggestionRequest(BaseModel):
    title: str = Field(..., description="Blog title")
    content: str = Field(..., description="Blog content")

class TitleSuggestionRequest(BaseModel):
    content: str = Field(..., description="Blog content")
    count: int = Field(5, ge=1, le=10, description="Number of title suggestions")

class SummaryRequest(BaseModel):
    content: str = Field(..., description="Content to summarize")
    max_length: int = Field(150, ge=50, le=300, description="Maximum summary length in words")

class QualityCheckRequest(BaseModel):
    title: str = Field(..., description="Blog title")
    content: str = Field(..., description="Blog content")


# Notification Rule Models
class NotificationRuleCreate(BaseModel):
    name: str = Field(..., description="Rule name")
    description: str = Field(..., description="Rule description")
    rule_type: str = Field(..., description="Rule type: event_based, threshold_based, scheduled")
    trigger_event: str = Field(..., description="Trigger event type")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="Rule conditions")
    actions: List[Dict[str, Any]] = Field(..., description="Actions to execute")
    enabled: bool = Field(True, description="Whether rule is enabled")


class NotificationRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None
    conditions: Optional[Dict[str, Any]] = None
    actions: Optional[List[Dict[str, Any]]] = None


# ==========================================
# AI BLOG ASSISTANT ENDPOINTS
# ==========================================

@router.post("/ai/blog/draft")
async def generate_blog_draft(
    request: BlogDraftRequest,
    admin: dict = Depends(require_admin_or_above)
):
    """
    Generate a complete blog draft from topic and keywords (AI-assisted)
    
    - **topic**: Main topic for the blog
    - **keywords**: Optional keywords to include
    - **tone**: Writing tone (professional, casual, friendly)
    - **length**: Content length (short, medium, long)
    
    Returns AI-generated title, content, and suggested tags
    """
    try:
        result = await ai_assistant.generate_draft(
            topic=request.topic,
            keywords=request.keywords,
            tone=request.tone,
            length=request.length
        )
        
        # Log AI usage
        await log_admin_action(
            admin_id=admin["id"],
            admin_email=admin["email"],
            action="ai_blog_draft_generated",
            entity="blog",
            entity_id=None,
            details={
                "topic": request.topic,
                "tone": request.tone,
                "length": request.length
            }
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Blog draft generated successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")


@router.post("/ai/blog/improve")
async def improve_blog_content(
    request: ContentImprovementRequest,
    admin: dict = Depends(require_admin_or_above)
):
    """
    Improve existing blog content with AI suggestions
    
    - **content**: Content to improve
    - **improvement_type**: Focus area (general, clarity, engagement, tone)
    
    Returns improved version of the content
    """
    try:
        result = await ai_assistant.improve_content(
            content=request.content,
            improvement_type=request.improvement_type
        )
        
        await log_admin_action(
            admin_id=admin["id"],
            admin_email=admin["email"],
            action="ai_content_improved",
            entity="blog",
            entity_id=None,
            details={"improvement_type": request.improvement_type}
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Content improved successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI improvement failed: {str(e)}")


@router.post("/ai/blog/suggest-tags")
async def suggest_blog_tags(
    request: TagSuggestionRequest,
    admin: dict = Depends(require_admin_or_above)
):
    """
    Get AI-suggested tags for a blog post
    
    - **title**: Blog title
    - **content**: Blog content
    
    Returns list of relevant tags
    """
    try:
        tags = await ai_assistant.suggest_tags(
            title=request.title,
            content=request.content
        )
        
        await log_admin_action(
            admin_id=admin["id"],
            admin_email=admin["email"],
            action="ai_tags_suggested",
            entity="blog",
            entity_id=None,
            details={"tag_count": len(tags)}
        )
        
        return {
            "success": True,
            "data": {"tags": tags},
            "message": f"Generated {len(tags)} tag suggestions"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tag suggestion failed: {str(e)}")


@router.post("/ai/blog/suggest-titles")
async def suggest_blog_titles(
    request: TitleSuggestionRequest,
    admin: dict = Depends(require_admin_or_above)
):
    """
    Get AI-suggested titles for blog content
    
    - **content**: Blog content
    - **count**: Number of title suggestions (1-10)
    
    Returns list of suggested titles
    """
    try:
        titles = await ai_assistant.suggest_titles(
            content=request.content,
            count=request.count
        )
        
        await log_admin_action(
            admin_id=admin["id"],
            admin_email=admin["email"],
            action="ai_titles_suggested",
            entity="blog",
            entity_id=None,
            details={"title_count": len(titles)}
        )
        
        return {
            "success": True,
            "data": {"titles": titles},
            "message": f"Generated {len(titles)} title suggestions"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Title suggestion failed: {str(e)}")


@router.post("/ai/blog/generate-summary")
async def generate_blog_summary(
    request: SummaryRequest,
    admin: dict = Depends(require_admin_or_above)
):
    """
    Generate a concise summary of blog content
    
    - **content**: Content to summarize
    - **max_length**: Maximum length in words (50-300)
    
    Returns AI-generated summary
    """
    try:
        summary = await ai_assistant.generate_summary(
            content=request.content,
            max_length=request.max_length
        )
        
        await log_admin_action(
            admin_id=admin["id"],
            admin_email=admin["email"],
            action="ai_summary_generated",
            entity="blog",
            entity_id=None,
            details={"max_length": request.max_length}
        )
        
        return {
            "success": True,
            "data": {"summary": summary},
            "message": "Summary generated successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")


@router.post("/ai/blog/quality-check")
async def check_blog_quality(
    request: QualityCheckRequest,
    admin: dict = Depends(require_admin_or_above)
):
    """
    Analyze blog content quality with AI
    
    - **title**: Blog title
    - **content**: Blog content
    
    Returns quality analysis with scores and suggestions
    """
    try:
        result = await ai_assistant.quality_check(
            title=request.title,
            content=request.content
        )
        
        await log_admin_action(
            admin_id=admin["id"],
            admin_email=admin["email"],
            action="ai_quality_check",
            entity="blog",
            entity_id=None,
            details={"word_count": result["word_count"]}
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Quality check completed"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quality check failed: {str(e)}")


# ==========================================
# AI FEATURE STATUS
# ==========================================

@router.get("/ai/status")
async def get_ai_status(admin: dict = Depends(get_current_admin)):
    """
    Get AI feature status and availability
    
    Returns information about AI capabilities and configuration
    """
    try:
        # Check if AI key is configured
        ai_key = os.getenv("EMERGENT_LLM_KEY")
        is_configured = bool(ai_key)
        
        # Get AI feature toggle status from database
        feature_toggle = db.feature_toggles.find_one({"name": "ai_assistance"})
        is_enabled = feature_toggle["enabled"] if feature_toggle else True
        
        return {
            "success": True,
            "data": {
                "ai_configured": is_configured,
                "ai_enabled": is_enabled,
                "provider": "OpenAI",
                "model": "gpt-4o-mini",
                "features": [
                    "blog_draft_generation",
                    "content_improvement",
                    "tag_suggestion",
                    "title_suggestion",
                    "summary_generation",
                    "quality_check"
                ]
            },
            "message": "AI status retrieved successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get AI status: {str(e)}")


# ==========================================
# NOTIFICATION RULE ENGINE ENDPOINTS
# ==========================================

@router.get("/notifications/rules")
async def get_notification_rules(
    rule_type: Optional[str] = None,
    enabled: Optional[bool] = None,
    page: int = 1,
    limit: int = 50,
    admin: dict = Depends(require_admin_or_above)
):
    """
    Get all notification rules with optional filters
    
    - **rule_type**: Filter by rule type (event_based, threshold_based, scheduled)
    - **enabled**: Filter by enabled status
    - **page**: Page number
    - **limit**: Items per page
    """
    try:
        skip = (page - 1) * limit
        result = await notification_engine.get_rules(
            rule_type=rule_type,
            enabled=enabled,
            skip=skip,
            limit=limit
        )
        
        return {
            "success": True,
            "data": result["rules"],
            "pagination": {
                "total": result["total"],
                "page": page,
                "limit": limit,
                "pages": (result["total"] + limit - 1) // limit
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch rules: {str(e)}")


@router.post("/notifications/rules")
async def create_notification_rule(
    request: NotificationRuleCreate,
    admin: dict = Depends(require_admin_or_above)
):
    """
    Create a new notification rule
    
    - **name**: Rule name
    - **description**: Rule description
    - **rule_type**: event_based, threshold_based, or scheduled
    - **trigger_event**: Event that triggers the rule
    - **conditions**: Conditions that must be met
    - **actions**: Actions to execute when triggered
    - **enabled**: Whether rule is active
    """
    try:
        rule = await notification_engine.create_rule(
            name=request.name,
            description=request.description,
            rule_type=request.rule_type,
            trigger_event=request.trigger_event,
            conditions=request.conditions,
            actions=request.actions,
            enabled=request.enabled,
            created_by=admin["id"]
        )
        
        await log_admin_action(
            admin_id=admin["id"],
            admin_email=admin["email"],
            action="notification_rule_created",
            entity="notification_rule",
            entity_id=rule["id"],
            details={"name": rule["name"]}
        )
        
        return {
            "success": True,
            "data": rule,
            "message": "Notification rule created successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create rule: {str(e)}")


@router.put("/notifications/rules/{rule_id}")
async def update_notification_rule(
    rule_id: str,
    request: NotificationRuleUpdate,
    admin: dict = Depends(require_admin_or_above)
):
    """
    Update an existing notification rule
    
    - **rule_id**: ID of the rule to update
    """
    try:
        # Build updates dict from non-None fields
        updates = {k: v for k, v in request.dict().items() if v is not None}
        
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        updated_rule = await notification_engine.update_rule(rule_id, updates)
        
        await log_admin_action(
            admin_id=admin["id"],
            admin_email=admin["email"],
            action="notification_rule_updated",
            entity="notification_rule",
            entity_id=rule_id,
            details=updates
        )
        
        return {
            "success": True,
            "data": updated_rule,
            "message": "Notification rule updated successfully"
        }
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update rule: {str(e)}")


@router.delete("/notifications/rules/{rule_id}")
async def delete_notification_rule(
    rule_id: str,
    admin: dict = Depends(require_admin_or_above)
):
    """
    Delete a notification rule
    
    - **rule_id**: ID of the rule to delete
    """
    try:
        deleted = await notification_engine.delete_rule(rule_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        await log_admin_action(
            admin_id=admin["id"],
            admin_email=admin["email"],
            action="notification_rule_deleted",
            entity="notification_rule",
            entity_id=rule_id,
            details={}
        )
        
        return {
            "success": True,
            "message": "Notification rule deleted successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete rule: {str(e)}")


@router.get("/notifications")
async def get_notifications(
    read: Optional[bool] = None,
    severity: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    admin: dict = Depends(require_admin_or_above)
):
    """
    Get admin notifications/alerts
    
    - **read**: Filter by read status
    - **severity**: Filter by severity (info, warning, error)
    - **page**: Page number
    - **limit**: Items per page
    """
    try:
        skip = (page - 1) * limit
        result = await notification_engine.get_notifications(
            read=read,
            severity=severity,
            skip=skip,
            limit=limit
        )
        
        return {
            "success": True,
            "data": result["notifications"],
            "unread_count": result["unread_count"],
            "pagination": {
                "total": result["total"],
                "page": page,
                "limit": limit,
                "pages": (result["total"] + limit - 1) // limit
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch notifications: {str(e)}")


@router.patch("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    admin: dict = Depends(require_admin_or_above)
):
    """
    Mark a notification as read
    
    - **notification_id**: ID of the notification
    """
    try:
        success = await notification_engine.mark_notification_read(notification_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        return {
            "success": True,
            "message": "Notification marked as read"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark notification as read: {str(e)}")


@router.post("/notifications/mark-all-read")
async def mark_all_notifications_read(
    admin: dict = Depends(require_admin_or_above)
):
    """
    Mark all notifications as read
    """
    try:
        count = await notification_engine.mark_all_notifications_read()
        
        return {
            "success": True,
            "message": f"{count} notifications marked as read"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark notifications as read: {str(e)}")


@router.get("/notifications/trigger-events")
async def get_trigger_events(admin: dict = Depends(require_admin_or_above)):
    """
    Get list of available trigger events for notification rules
    """
    return {
        "success": True,
        "data": {
            "events": notification_engine.TRIGGER_EVENTS,
            "action_types": notification_engine.ACTION_TYPES,
            "rule_types": notification_engine.RULE_TYPES
        }
    }


# ==========================================
# WORKFLOW AUTOMATION ENDPOINTS
# ==========================================

class WorkflowCreate(BaseModel):
    name: str = Field(..., description="Workflow name")
    description: str = Field(..., description="Workflow description")
    workflow_type: str = Field(..., description="Workflow type")
    steps: List[Dict[str, Any]] = Field(..., description="Workflow steps")
    config: Dict[str, Any] = Field(default_factory=dict, description="Workflow configuration")


class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None
    steps: Optional[List[Dict[str, Any]]] = None
    config: Optional[Dict[str, Any]] = None


class WorkflowExecuteRequest(BaseModel):
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Input data for workflow")


@router.get("/workflows")
async def get_workflows(
    workflow_type: Optional[str] = None,
    enabled: Optional[bool] = None,
    page: int = 1,
    limit: int = 50,
    admin: dict = Depends(require_admin_or_above)
):
    """
    Get all workflow templates
    
    - **workflow_type**: Filter by type (content_review, bulk_approval, data_cleanup, etc.)
    - **enabled**: Filter by enabled status
    - **page**: Page number
    - **limit**: Items per page
    """
    try:
        skip = (page - 1) * limit
        result = await workflow_engine.get_workflows(
            workflow_type=workflow_type,
            enabled=enabled,
            skip=skip,
            limit=limit
        )
        
        return {
            "success": True,
            "data": result["workflows"],
            "pagination": {
                "total": result["total"],
                "page": page,
                "limit": limit,
                "pages": (result["total"] + limit - 1) // limit
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch workflows: {str(e)}")


@router.post("/workflows")
async def create_workflow(
    request: WorkflowCreate,
    admin: dict = Depends(require_admin_or_above)
):
    """
    Create a new workflow template
    
    - **name**: Workflow name
    - **description**: Workflow description
    - **workflow_type**: Type of workflow
    - **steps**: List of workflow steps
    - **config**: Workflow configuration
    """
    try:
        workflow = await workflow_engine.create_workflow(
            name=request.name,
            description=request.description,
            workflow_type=request.workflow_type,
            steps=request.steps,
            config=request.config,
            created_by=admin["id"]
        )
        
        await log_admin_action(
            admin_id=admin["id"],
            admin_email=admin["email"],
            action="workflow_created",
            entity="workflow",
            entity_id=workflow["id"],
            details={"name": workflow["name"], "type": workflow["workflow_type"]}
        )
        
        return {
            "success": True,
            "data": workflow,
            "message": "Workflow created successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create workflow: {str(e)}")


@router.put("/workflows/{workflow_id}")
async def update_workflow(
    workflow_id: str,
    request: WorkflowUpdate,
    admin: dict = Depends(require_admin_or_above)
):
    """
    Update a workflow template
    
    - **workflow_id**: ID of the workflow to update
    """
    try:
        updates = {k: v for k, v in request.dict().items() if v is not None}
        
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        updated_workflow = await workflow_engine.update_workflow(workflow_id, updates)
        
        await log_admin_action(
            admin_id=admin["id"],
            admin_email=admin["email"],
            action="workflow_updated",
            entity="workflow",
            entity_id=workflow_id,
            details=updates
        )
        
        return {
            "success": True,
            "data": updated_workflow,
            "message": "Workflow updated successfully"
        }
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update workflow: {str(e)}")


@router.delete("/workflows/{workflow_id}")
async def delete_workflow(
    workflow_id: str,
    admin: dict = Depends(require_admin_or_above)
):
    """
    Delete a workflow template
    
    - **workflow_id**: ID of the workflow to delete
    """
    try:
        deleted = await workflow_engine.delete_workflow(workflow_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        await log_admin_action(
            admin_id=admin["id"],
            admin_email=admin["email"],
            action="workflow_deleted",
            entity="workflow",
            entity_id=workflow_id,
            details={}
        )
        
        return {
            "success": True,
            "message": "Workflow deleted successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete workflow: {str(e)}")


@router.post("/workflows/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: str,
    request: WorkflowExecuteRequest,
    admin: dict = Depends(require_admin_or_above)
):
    """
    Execute a workflow manually
    
    - **workflow_id**: ID of the workflow to execute
    - **input_data**: Optional input data for the workflow
    """
    try:
        execution = await workflow_engine.execute_workflow(
            workflow_id=workflow_id,
            triggered_by=admin["id"],
            input_data=request.input_data
        )
        
        await log_admin_action(
            admin_id=admin["id"],
            admin_email=admin["email"],
            action="workflow_executed",
            entity="workflow",
            entity_id=workflow_id,
            details={
                "execution_id": execution["id"],
                "status": execution["status"],
                "steps_completed": execution["steps_completed"]
            }
        )
        
        return {
            "success": True,
            "data": execution,
            "message": f"Workflow execution {execution['status']}"
        }
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute workflow: {str(e)}")


@router.get("/workflows/{workflow_id}/executions")
async def get_workflow_executions(
    workflow_id: str,
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    admin: dict = Depends(require_admin_or_above)
):
    """
    Get execution history for a specific workflow
    
    - **workflow_id**: ID of the workflow
    - **status**: Filter by status (pending, in_progress, completed, failed, cancelled)
    - **page**: Page number
    - **limit**: Items per page
    """
    try:
        skip = (page - 1) * limit
        result = await workflow_engine.get_executions(
            workflow_id=workflow_id,
            status=status,
            skip=skip,
            limit=limit
        )
        
        return {
            "success": True,
            "data": result["executions"],
            "pagination": {
                "total": result["total"],
                "page": page,
                "limit": limit,
                "pages": (result["total"] + limit - 1) // limit
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch executions: {str(e)}")


@router.get("/workflows/executions/all")
async def get_all_executions(
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    admin: dict = Depends(require_admin_or_above)
):
    """
    Get all workflow executions across all workflows
    
    - **status**: Filter by status
    - **page**: Page number
    - **limit**: Items per page
    """
    try:
        skip = (page - 1) * limit
        result = await workflow_engine.get_executions(
            status=status,
            skip=skip,
            limit=limit
        )
        
        return {
            "success": True,
            "data": result["executions"],
            "pagination": {
                "total": result["total"],
                "page": page,
                "limit": limit,
                "pages": (result["total"] + limit - 1) // limit
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch executions: {str(e)}")


@router.get("/workflows/executions/{execution_id}")
async def get_execution_details(
    execution_id: str,
    admin: dict = Depends(require_admin_or_above)
):
    """
    Get detailed information about a workflow execution
    
    - **execution_id**: ID of the execution
    """
    try:
        execution = await workflow_engine.get_execution_details(execution_id)
        
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        return {
            "success": True,
            "data": execution
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch execution details: {str(e)}")


@router.post("/workflows/executions/{execution_id}/cancel")
async def cancel_execution(
    execution_id: str,
    admin: dict = Depends(require_admin_or_above)
):
    """
    Cancel a running workflow execution
    
    - **execution_id**: ID of the execution to cancel
    """
    try:
        cancelled = await workflow_engine.cancel_execution(execution_id)
        
        if not cancelled:
            raise HTTPException(status_code=404, detail="Execution not found or not in progress")
        
        await log_admin_action(
            admin_id=admin["id"],
            admin_email=admin["email"],
            action="workflow_execution_cancelled",
            entity="workflow_execution",
            entity_id=execution_id,
            details={}
        )
        
        return {
            "success": True,
            "message": "Workflow execution cancelled successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel execution: {str(e)}")


@router.get("/workflows/types")
async def get_workflow_types(admin: dict = Depends(require_admin_or_above)):
    """
    Get list of available workflow types and their descriptions
    """
    return {
        "success": True,
        "data": {
            "workflow_types": workflow_engine.WORKFLOW_TYPES,
            "workflow_status": workflow_engine.WORKFLOW_STATUS,
            "step_status": workflow_engine.STEP_STATUS
        }
    }



# ==========================================
# ANALYTICS ENDPOINTS (Phase 8.1B)
# ==========================================

@router.get("/analytics/dashboard")
async def get_analytics_dashboard(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    admin: dict = Depends(require_admin_or_above)
):
    """
    Get comprehensive analytics dashboard
    
    - **start_date**: Start date (ISO format, optional)
    - **end_date**: End date (ISO format, optional)
    
    Returns overview of all key metrics
    """
    try:
        from datetime import datetime
        
        # Parse dates if provided
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        dashboard = await analytics_engine.get_dashboard_overview(start, end)
        
        return {
            "success": True,
            "data": dashboard
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard: {str(e)}")


@router.get("/analytics/sessions")
async def get_session_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    admin: dict = Depends(require_admin_or_above)
):
    """
    Get session booking analytics
    
    - **start_date**: Start date (ISO format, optional)
    - **end_date**: End date (ISO format, optional)
    
    Returns session trends, status breakdown, and key metrics
    """
    try:
        from datetime import datetime
        
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        analytics = await analytics_engine.get_session_analytics(start, end)
        
        return {
            "success": True,
            "data": analytics
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch session analytics: {str(e)}")


@router.get("/analytics/events")
async def get_event_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    admin: dict = Depends(require_admin_or_above)
):
    """
    Get event analytics
    
    - **start_date**: Start date (ISO format, optional)
    - **end_date**: End date (ISO format, optional)
    
    Returns event trends, registrations, and top events
    """
    try:
        from datetime import datetime
        
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        analytics = await analytics_engine.get_event_analytics(start, end)
        
        return {
            "success": True,
            "data": analytics
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch event analytics: {str(e)}")


@router.get("/analytics/blogs")
async def get_blog_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    admin: dict = Depends(require_admin_or_above)
):
    """
    Get blog engagement analytics
    
    - **start_date**: Start date (ISO format, optional)
    - **end_date**: End date (ISO format, optional)
    
    Returns blog metrics, category breakdown, and recent posts
    """
    try:
        from datetime import datetime
        
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        analytics = await analytics_engine.get_blog_analytics(start, end)
        
        return {
            "success": True,
            "data": analytics
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch blog analytics: {str(e)}")


@router.get("/analytics/volunteers")
async def get_volunteer_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    admin: dict = Depends(require_admin_or_above)
):
    """
    Get volunteer application analytics
    
    - **start_date**: Start date (ISO format, optional)
    - **end_date**: End date (ISO format, optional)
    
    Returns volunteer application trends and status breakdown
    """
    try:
        from datetime import datetime
        
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        analytics = await analytics_engine.get_volunteer_analytics(start, end)
        
        return {
            "success": True,
            "data": analytics
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch volunteer analytics: {str(e)}")


@router.get("/analytics/contacts")
async def get_contact_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    admin: dict = Depends(require_admin_or_above)
):
    """
    Get contact form analytics
    
    - **start_date**: Start date (ISO format, optional)
    - **end_date**: End date (ISO format, optional)
    
    Returns contact metrics and response rate
    """
    try:
        from datetime import datetime
        
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        analytics = await analytics_engine.get_contact_analytics(start, end)
        
        return {
            "success": True,
            "data": analytics
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch contact analytics: {str(e)}")


@router.get("/analytics/export/{data_type}")
async def export_analytics_csv(
    data_type: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    admin: dict = Depends(require_admin_or_above)
):
    """
    Export analytics data as CSV
    
    - **data_type**: Type of data to export (sessions, events, blogs, volunteers, contacts)
    - **start_date**: Start date (ISO format, optional)
    - **end_date**: End date (ISO format, optional)
    
    Returns CSV file for download
    """
    try:
        from datetime import datetime
        
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
        
        csv_content = await analytics_engine.export_analytics_csv(data_type, start, end)
        
        await log_admin_action(
            admin_id=admin["id"],
            admin_email=admin["email"],
            action="analytics_export",
            entity="analytics",
            entity_id=None,
            details={"data_type": data_type}
        )
        
        # Return CSV file
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={data_type}_export.csv"
            }
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export analytics: {str(e)}")

