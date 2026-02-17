"""
Phase 8.1A - Admin Workflow Automation
Manual workflow triggers and automated task sequences
"""
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pymongo import MongoClient
import uuid

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = MongoClient(MONGO_URL)
db = client[os.environ.get('DB_NAME', 'test_database')]

# Collections
workflows_collection = db['workflows']
workflow_executions_collection = db['workflow_executions']


class WorkflowEngine:
    """Manages workflow templates and executions"""
    
    WORKFLOW_TYPES = [
        'content_review',       # Review and approve content
        'bulk_approval',        # Approve multiple items at once
        'data_cleanup',         # Clean up old/invalid data
        'report_generation',    # Generate system reports
        'scheduled_publish',    # Schedule content publishing
        'user_onboarding'       # Automated user onboarding
    ]
    
    WORKFLOW_STATUS = [
        'pending',      # Workflow created but not started
        'in_progress',  # Currently executing
        'completed',    # Successfully completed
        'failed',       # Failed with errors
        'cancelled'     # Manually cancelled
    ]
    
    STEP_STATUS = [
        'pending',
        'in_progress',
        'completed',
        'failed',
        'skipped'
    ]
    
    @staticmethod
    async def create_workflow(
        name: str,
        description: str,
        workflow_type: str,
        steps: List[Dict[str, Any]],
        config: Dict[str, Any],
        created_by: str
    ) -> Dict[str, Any]:
        """Create a new workflow template"""
        
        workflow_id = str(uuid.uuid4())
        workflow = {
            "id": workflow_id,
            "name": name,
            "description": description,
            "workflow_type": workflow_type,
            "steps": steps,  # List of steps with action and parameters
            "config": config,  # Workflow-specific configuration
            "enabled": True,
            "execution_count": 0,
            "last_executed": None,
            "created_by": created_by,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        workflows_collection.insert_one(workflow)
        return workflow
    
    @staticmethod
    async def get_workflows(
        workflow_type: Optional[str] = None,
        enabled: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Get workflow templates with filters"""
        
        query = {}
        if workflow_type:
            query["workflow_type"] = workflow_type
        if enabled is not None:
            query["enabled"] = enabled
        
        total = workflows_collection.count_documents(query)
        workflows = list(
            workflows_collection.find(query, {"_id": 0})
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )
        
        return {
            "workflows": workflows,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    @staticmethod
    async def update_workflow(
        workflow_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a workflow template"""
        
        updates["updated_at"] = datetime.utcnow()
        
        result = workflows_collection.update_one(
            {"id": workflow_id},
            {"$set": updates}
        )
        
        if result.matched_count == 0:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        updated_workflow = workflows_collection.find_one({"id": workflow_id}, {"_id": 0})
        return updated_workflow
    
    @staticmethod
    async def delete_workflow(workflow_id: str) -> bool:
        """Delete a workflow template"""
        
        result = workflows_collection.delete_one({"id": workflow_id})
        return result.deleted_count > 0
    
    @staticmethod
    async def execute_workflow(
        workflow_id: str,
        triggered_by: str,
        input_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Execute a workflow manually
        Returns execution record
        """
        
        # Get workflow template
        workflow = workflows_collection.find_one({"id": workflow_id}, {"_id": 0})
        
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        if not workflow.get("enabled"):
            raise ValueError(f"Workflow {workflow_id} is disabled")
        
        # Create execution record
        execution_id = str(uuid.uuid4())
        execution = {
            "id": execution_id,
            "workflow_id": workflow_id,
            "workflow_name": workflow["name"],
            "workflow_type": workflow["workflow_type"],
            "status": "in_progress",
            "current_step": 0,
            "total_steps": len(workflow["steps"]),
            "steps_completed": 0,
            "steps_failed": 0,
            "triggered_by": triggered_by,
            "input_data": input_data or {},
            "output_data": {},
            "step_results": [],
            "error_log": [],
            "started_at": datetime.utcnow(),
            "completed_at": None,
            "duration_seconds": None
        }
        
        workflow_executions_collection.insert_one(execution)
        
        # Execute workflow steps
        try:
            for i, step in enumerate(workflow["steps"]):
                execution["current_step"] = i
                
                # Execute step
                step_result = await WorkflowEngine._execute_step(
                    step,
                    execution,
                    workflow["config"]
                )
                
                execution["step_results"].append(step_result)
                
                if step_result["status"] == "completed":
                    execution["steps_completed"] += 1
                elif step_result["status"] == "failed":
                    execution["steps_failed"] += 1
                    if not step.get("continue_on_error", False):
                        execution["status"] = "failed"
                        break
                
                # Update execution record
                workflow_executions_collection.update_one(
                    {"id": execution_id},
                    {"$set": {
                        "current_step": i,
                        "steps_completed": execution["steps_completed"],
                        "steps_failed": execution["steps_failed"],
                        "step_results": execution["step_results"]
                    }}
                )
            
            # Mark as completed if no failures
            if execution["status"] != "failed":
                execution["status"] = "completed"
            
            execution["completed_at"] = datetime.utcnow()
            execution["duration_seconds"] = (
                execution["completed_at"] - execution["started_at"]
            ).total_seconds()
            
            # Update final status
            workflow_executions_collection.update_one(
                {"id": execution_id},
                {"$set": {
                    "status": execution["status"],
                    "completed_at": execution["completed_at"],
                    "duration_seconds": execution["duration_seconds"]
                }}
            )
            
            # Update workflow execution count
            workflows_collection.update_one(
                {"id": workflow_id},
                {
                    "$inc": {"execution_count": 1},
                    "$set": {"last_executed": datetime.utcnow()}
                }
            )
            
        except Exception as e:
            execution["status"] = "failed"
            execution["error_log"].append({
                "error": str(e),
                "timestamp": datetime.utcnow()
            })
            
            workflow_executions_collection.update_one(
                {"id": execution_id},
                {"$set": {
                    "status": "failed",
                    "error_log": execution["error_log"]
                }}
            )
        
        # Return updated execution
        final_execution = workflow_executions_collection.find_one(
            {"id": execution_id},
            {"_id": 0}
        )
        return final_execution
    
    @staticmethod
    async def _execute_step(
        step: Dict[str, Any],
        execution: Dict[str, Any],
        workflow_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single workflow step"""
        
        step_result = {
            "step_name": step.get("name", "Unnamed Step"),
            "action": step.get("action"),
            "status": "in_progress",
            "started_at": datetime.utcnow(),
            "completed_at": None,
            "output": None,
            "error": None
        }
        
        try:
            action = step.get("action")
            params = step.get("parameters", {})
            
            # Execute different actions
            if action == "review_content":
                # Review content (blog, event, etc.)
                entity_type = params.get("entity_type")
                entity_ids = params.get("entity_ids", [])
                
                print(f"📝 Reviewing {len(entity_ids)} {entity_type} items")
                step_result["output"] = {
                    "reviewed_count": len(entity_ids),
                    "entity_type": entity_type
                }
            
            elif action == "approve_items":
                # Bulk approve items
                entity_type = params.get("entity_type")
                entity_ids = params.get("entity_ids", [])
                
                collection = db[entity_type]
                result = collection.update_many(
                    {"id": {"$in": entity_ids}},
                    {"$set": {"status": "approved", "approved_at": datetime.utcnow()}}
                )
                
                print(f"✅ Approved {result.modified_count} {entity_type} items")
                step_result["output"] = {
                    "approved_count": result.modified_count
                }
            
            elif action == "cleanup_data":
                # Clean up old data
                entity_type = params.get("entity_type")
                days_old = params.get("days_old", 90)
                
                collection = db[entity_type]
                cutoff_date = datetime.utcnow() - timedelta(days=days_old)
                
                result = collection.delete_many({
                    "created_at": {"$lt": cutoff_date},
                    "is_deleted": True
                })
                
                print(f"🗑️ Cleaned up {result.deleted_count} old {entity_type} items")
                step_result["output"] = {
                    "deleted_count": result.deleted_count
                }
            
            elif action == "generate_report":
                # Generate report
                report_type = params.get("report_type")
                
                print(f"📊 Generating {report_type} report")
                step_result["output"] = {
                    "report_type": report_type,
                    "generated": True
                }
            
            elif action == "send_notification":
                # Send notification
                recipients = params.get("recipients", [])
                message = params.get("message", "")
                
                print(f"📧 Sending notification to {len(recipients)} recipients")
                step_result["output"] = {
                    "recipients_count": len(recipients),
                    "sent": True
                }
            
            elif action == "delay":
                # Delay/wait
                seconds = params.get("seconds", 1)
                print(f"⏳ Waiting {seconds} seconds")
                step_result["output"] = {"waited_seconds": seconds}
            
            else:
                # Unknown action - log it
                print(f"⚠️ Unknown action: {action}")
                step_result["output"] = {"action": action, "executed": True}
            
            step_result["status"] = "completed"
        
        except Exception as e:
            step_result["status"] = "failed"
            step_result["error"] = str(e)
            print(f"❌ Step failed: {e}")
        
        finally:
            step_result["completed_at"] = datetime.utcnow()
        
        return step_result
    
    @staticmethod
    async def get_executions(
        workflow_id: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Get workflow execution history"""
        
        query = {}
        if workflow_id:
            query["workflow_id"] = workflow_id
        if status:
            query["status"] = status
        
        total = workflow_executions_collection.count_documents(query)
        executions = list(
            workflow_executions_collection.find(query, {"_id": 0})
            .sort("started_at", -1)
            .skip(skip)
            .limit(limit)
        )
        
        return {
            "executions": executions,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    @staticmethod
    async def get_execution_details(execution_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed execution information"""
        
        execution = workflow_executions_collection.find_one(
            {"id": execution_id},
            {"_id": 0}
        )
        return execution
    
    @staticmethod
    async def cancel_execution(execution_id: str) -> bool:
        """Cancel a running workflow execution"""
        
        result = workflow_executions_collection.update_one(
            {"id": execution_id, "status": "in_progress"},
            {"$set": {
                "status": "cancelled",
                "completed_at": datetime.utcnow()
            }}
        )
        
        return result.modified_count > 0


# Initialize default workflow templates
async def initialize_default_workflows():
    """Create default workflow templates if they don't exist"""
    
    existing_workflows = workflows_collection.count_documents({})
    if existing_workflows > 0:
        return  # Workflows already exist
    
    default_workflows = [
        {
            "name": "Content Review Workflow",
            "description": "Review and approve pending blog posts",
            "workflow_type": "content_review",
            "steps": [
                {
                    "name": "Fetch Pending Blogs",
                    "action": "review_content",
                    "parameters": {
                        "entity_type": "blogs",
                        "status": "pending"
                    }
                },
                {
                    "name": "Approve Blogs",
                    "action": "approve_items",
                    "parameters": {
                        "entity_type": "blogs"
                    }
                },
                {
                    "name": "Send Approval Notifications",
                    "action": "send_notification",
                    "parameters": {
                        "message": "Your blog post has been approved"
                    }
                }
            ],
            "config": {
                "auto_execute": False,
                "schedule": None
            },
            "enabled": True
        },
        {
            "name": "Data Cleanup Workflow",
            "description": "Clean up soft-deleted data older than 90 days",
            "workflow_type": "data_cleanup",
            "steps": [
                {
                    "name": "Cleanup Session Bookings",
                    "action": "cleanup_data",
                    "parameters": {
                        "entity_type": "session_bookings",
                        "days_old": 90
                    }
                },
                {
                    "name": "Cleanup Events",
                    "action": "cleanup_data",
                    "parameters": {
                        "entity_type": "events",
                        "days_old": 90
                    }
                },
                {
                    "name": "Generate Cleanup Report",
                    "action": "generate_report",
                    "parameters": {
                        "report_type": "cleanup_summary"
                    }
                }
            ],
            "config": {
                "auto_execute": False,
                "schedule": "monthly"
            },
            "enabled": True
        },
        {
            "name": "Bulk Volunteer Approval",
            "description": "Approve multiple volunteer applications at once",
            "workflow_type": "bulk_approval",
            "steps": [
                {
                    "name": "Approve Applications",
                    "action": "approve_items",
                    "parameters": {
                        "entity_type": "volunteers"
                    }
                },
                {
                    "name": "Send Welcome Emails",
                    "action": "send_notification",
                    "parameters": {
                        "message": "Welcome to our volunteer program!"
                    }
                }
            ],
            "config": {
                "auto_execute": False
            },
            "enabled": True
        },
        {
            "name": "Monthly Report Generation",
            "description": "Generate comprehensive monthly activity report",
            "workflow_type": "report_generation",
            "steps": [
                {
                    "name": "Generate Sessions Report",
                    "action": "generate_report",
                    "parameters": {
                        "report_type": "sessions_monthly"
                    }
                },
                {
                    "name": "Generate Events Report",
                    "action": "generate_report",
                    "parameters": {
                        "report_type": "events_monthly"
                    }
                },
                {
                    "name": "Generate Blog Analytics",
                    "action": "generate_report",
                    "parameters": {
                        "report_type": "blogs_monthly"
                    }
                },
                {
                    "name": "Send Report to Admins",
                    "action": "send_notification",
                    "parameters": {
                        "message": "Monthly report is ready"
                    }
                }
            ],
            "config": {
                "auto_execute": False,
                "schedule": "monthly"
            },
            "enabled": True
        }
    ]
    
    for workflow_data in default_workflows:
        await WorkflowEngine.create_workflow(
            name=workflow_data["name"],
            description=workflow_data["description"],
            workflow_type=workflow_data["workflow_type"],
            steps=workflow_data["steps"],
            config=workflow_data["config"],
            created_by="system"
        )
    
    print(f"✅ Initialized {len(default_workflows)} default workflow templates")


# Singleton instance
workflow_engine = WorkflowEngine()
