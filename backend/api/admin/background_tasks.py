"""Background task utilities for async operations."""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import os
import io
import csv
import sys
sys.path.append('/app/backend')

logger = logging.getLogger(__name__)


# ============= EMAIL SERVICE (REAL + FALLBACK) =============

class EmailService:
    """Email service with real implementation and fallback to mock."""
    
    @staticmethod
    async def send_welcome_email(to_email: str, admin_name: str):
        """Send welcome email to new admin."""
        try:
            from api.phase12_email import send_email_async, create_welcome_email
            
            html_content = create_welcome_email(user_name=admin_name)
            result = await send_email_async(
                to_email=to_email,
                subject="Welcome to A-Cube Admin Panel",
                html_content=html_content
            )
            
            if result["status"] == "mocked":
                logger.info(f"[MOCK EMAIL] Welcome email to {to_email} (email service not configured)")
            else:
                logger.info(f"[REAL EMAIL] Welcome email sent to {to_email}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to send welcome email: {str(e)}")
            logger.info(f"[MOCK EMAIL] Fallback - Welcome email to {to_email}")
            return True
    
    @staticmethod
    async def send_session_confirmation(to_email: str, session_data: Dict[str, Any]):
        """Send session confirmation email."""
        try:
            from api.phase12_email import send_email_async, create_session_confirmation_email
            
            html_content = create_session_confirmation_email(
                user_name=session_data.get('name', 'User'),
                session_date=session_data.get('preferred_date', 'TBD'),
                session_time=session_data.get('preferred_time', 'TBD'),
                psychologist_name=session_data.get('psychologist', 'TBD')
            )
            
            result = await send_email_async(
                to_email=to_email,
                subject="Session Booking Confirmed - A-Cube",
                html_content=html_content
            )
            
            if result["status"] == "mocked":
                logger.info(f"[MOCK EMAIL] Session confirmation to {to_email} (email service not configured)")
            else:
                logger.info(f"[REAL EMAIL] Session confirmation sent to {to_email}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to send session confirmation: {str(e)}")
            logger.info(f"[MOCK EMAIL] Fallback - Session confirmation to {to_email}, ID: {session_data.get('id')}")
            return True
    
    @staticmethod
    async def send_event_registration(to_email: str, event_data: Dict[str, Any]):
        """Send event registration email."""
        try:
            from api.phase12_email import send_email_async, create_event_registration_email
            
            html_content = create_event_registration_email(
                user_name=event_data.get('name', 'User'),
                event_name=event_data.get('title', 'Event'),
                event_date=event_data.get('date', 'TBD'),
                event_time=event_data.get('time', 'TBD'),
                event_location=event_data.get('location', 'Online')
            )
            
            result = await send_email_async(
                to_email=to_email,
                subject=f"Event Registration Confirmed - {event_data.get('title', 'A-Cube Event')}",
                html_content=html_content
            )
            
            if result["status"] == "mocked":
                logger.info(f"[MOCK EMAIL] Event registration to {to_email} (email service not configured)")
            else:
                logger.info(f"[REAL EMAIL] Event registration sent to {to_email}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to send event registration: {str(e)}")
            logger.info(f"[MOCK EMAIL] Fallback - Event registration to {to_email}: {event_data.get('title')}")
            return True
    
    @staticmethod
    async def send_volunteer_application_received(to_email: str, volunteer_data: Dict[str, Any]):
        """Send volunteer application confirmation."""
        try:
            from api.phase12_email import send_email_async
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head><meta charset="UTF-8"><style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
                .container {{ max-width: 600px; margin: 20px auto; background: #ffffff; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
                .content {{ padding: 30px; }}
            </style></head>
            <body>
                <div class="container">
                    <div class="header"><h1>Application Received</h1></div>
                    <div class="content">
                        <p>Dear {volunteer_data.get('name', 'Volunteer')},</p>
                        <p>Thank you for your interest in volunteering with A-Cube Mental Health Platform.</p>
                        <p>We have received your application and our team will review it shortly.</p>
                        <p>Best regards,<br>The A-Cube Team</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            result = await send_email_async(
                to_email=to_email,
                subject="Volunteer Application Received - A-Cube",
                html_content=html_content
            )
            
            if result["status"] == "mocked":
                logger.info(f"[MOCK EMAIL] Volunteer application to {to_email} (email service not configured)")
            else:
                logger.info(f"[REAL EMAIL] Volunteer application sent to {to_email}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to send volunteer application email: {str(e)}")
            logger.info(f"[MOCK EMAIL] Fallback - Volunteer application to {to_email}")
            return True
    
    @staticmethod
    async def send_contact_form_acknowledgment(to_email: str, contact_data: Dict[str, Any]):
        """Send contact form acknowledgment."""
        try:
            from api.phase12_email import send_email_async, create_contact_acknowledgment_email
            
            message_preview = contact_data.get('message', '')[:100] + '...' if len(contact_data.get('message', '')) > 100 else contact_data.get('message', '')
            
            html_content = create_contact_acknowledgment_email(
                user_name=contact_data.get('name', 'User'),
                message_preview=message_preview
            )
            
            result = await send_email_async(
                to_email=to_email,
                subject="We've received your message - A-Cube",
                html_content=html_content
            )
            
            if result["status"] == "mocked":
                logger.info(f"[MOCK EMAIL] Contact acknowledgment to {to_email} (email service not configured)")
            else:
                logger.info(f"[REAL EMAIL] Contact acknowledgment sent to {to_email}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to send contact acknowledgment: {str(e)}")
            logger.info(f"[MOCK EMAIL] Fallback - Contact acknowledgment to {to_email}")
            return True
    
    @staticmethod
    async def send_bulk_operation_report(to_email: str, operation_type: str, result: Dict[str, Any]):
        """Send bulk operation completion report to admin."""
        logger.info(f"[MOCK EMAIL] Sending bulk operation report to {to_email}")
        logger.info(f"[MOCK EMAIL] Subject: Bulk {operation_type} Operation Complete")
        logger.info(f"[MOCK EMAIL] Success: {result.get('success_count')}, Failed: {result.get('failed_count')}")
        return True


# ============= AUDIT EXPORT SERVICE =============

class AuditExportService:
    """Service for exporting audit logs to CSV."""
    
    @staticmethod
    async def export_audit_logs(
        admin_email: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10000
    ) -> str:
        """Export audit logs to CSV and return file path."""
        logger.info(f"[BACKGROUND JOB] Starting audit log export for {admin_email}")
        
        try:
            mongo_url = os.environ['MONGO_URL']
            client = AsyncIOMotorClient(mongo_url)
            db = client[os.environ['DB_NAME']]
            
            # Build query
            query = filters or {}
            
            # Fetch logs
            logs = await db.admin_logs.find(query).limit(limit).to_list(limit)
            
            logger.info(f"[BACKGROUND JOB] Fetched {len(logs)} audit logs")
            
            # Generate CSV content
            if not logs:
                logger.warning(f"[BACKGROUND JOB] No logs found for export")
                return None
            
            # Create CSV in memory
            output = io.StringIO()
            fieldnames = ['timestamp', 'admin_email', 'action', 'entity', 'entity_id', 'details']
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            
            writer.writeheader()
            for log in logs:
                writer.writerow({
                    'timestamp': log.get('timestamp', ''),
                    'admin_email': log.get('admin_email', ''),
                    'action': log.get('action', ''),
                    'entity': log.get('entity', ''),
                    'entity_id': log.get('entity_id', ''),
                    'details': str(log.get('details', ''))
                })
            
            csv_content = output.getvalue()
            output.close()
            
            # Save to file (in production, would upload to S3 or similar)
            export_dir = "/app/backend/static/exports"
            os.makedirs(export_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"audit_logs_{timestamp}.csv"
            filepath = os.path.join(export_dir, filename)
            
            with open(filepath, 'w') as f:
                f.write(csv_content)
            
            logger.info(f"[BACKGROUND JOB] Audit log export complete: {filename}")
            
            # Send email notification (mocked)
            await EmailService.send_bulk_operation_report(
                to_email=admin_email,
                operation_type="Audit Export",
                result={
                    "success_count": len(logs),
                    "failed_count": 0,
                    "file": filename
                }
            )
            
            return filename
            
        except Exception as e:
            logger.error(f"[BACKGROUND JOB] Error exporting audit logs: {str(e)}")
            raise


# ============= BULK OPERATIONS SERVICE =============

class BulkOperationsService:
    """Service for executing bulk operations in background."""
    
    @staticmethod
    async def bulk_delete(
        collection: str,
        ids: List[str],
        admin_email: str
    ) -> Dict[str, Any]:
        """Delete multiple records in background."""
        logger.info(f"[BACKGROUND JOB] Starting bulk delete: {len(ids)} items from {collection}")
        
        try:
            mongo_url = os.environ['MONGO_URL']
            client = AsyncIOMotorClient(mongo_url)
            db = client[os.environ['DB_NAME']]
            
            collection_ref = db[collection]
            
            success_count = 0
            failed_count = 0
            failed_ids = []
            
            for item_id in ids:
                try:
                    result = await collection_ref.delete_one({"id": item_id})
                    if result.deleted_count > 0:
                        success_count += 1
                    else:
                        failed_count += 1
                        failed_ids.append(item_id)
                except Exception as e:
                    logger.error(f"[BACKGROUND JOB] Failed to delete {item_id}: {str(e)}")
                    failed_count += 1
                    failed_ids.append(item_id)
            
            result = {
                "success_count": success_count,
                "failed_count": failed_count,
                "failed_ids": failed_ids
            }
            
            logger.info(f"[BACKGROUND JOB] Bulk delete complete: {success_count} success, {failed_count} failed")
            
            # Send completion email
            await EmailService.send_bulk_operation_report(
                to_email=admin_email,
                operation_type="Delete",
                result=result
            )
            
            return result
            
        except Exception as e:
            logger.error(f"[BACKGROUND JOB] Error in bulk delete: {str(e)}")
            raise
    
    @staticmethod
    async def bulk_status_update(
        collection: str,
        ids: List[str],
        new_status: str,
        admin_email: str
    ) -> Dict[str, Any]:
        """Update status of multiple records in background."""
        logger.info(f"[BACKGROUND JOB] Starting bulk status update: {len(ids)} items to '{new_status}'")
        
        try:
            mongo_url = os.environ['MONGO_URL']
            client = AsyncIOMotorClient(mongo_url)
            db = client[os.environ['DB_NAME']]
            
            collection_ref = db[collection]
            
            success_count = 0
            failed_count = 0
            failed_ids = []
            
            for item_id in ids:
                try:
                    result = await collection_ref.update_one(
                        {"id": item_id},
                        {"$set": {"status": new_status}}
                    )
                    if result.matched_count > 0:
                        success_count += 1
                    else:
                        failed_count += 1
                        failed_ids.append(item_id)
                except Exception as e:
                    logger.error(f"[BACKGROUND JOB] Failed to update {item_id}: {str(e)}")
                    failed_count += 1
                    failed_ids.append(item_id)
            
            result = {
                "success_count": success_count,
                "failed_count": failed_count,
                "failed_ids": failed_ids,
                "new_status": new_status
            }
            
            logger.info(f"[BACKGROUND JOB] Bulk status update complete: {success_count} success, {failed_count} failed")
            
            # Send completion email
            await EmailService.send_bulk_operation_report(
                to_email=admin_email,
                operation_type="Status Update",
                result=result
            )
            
            return result
            
        except Exception as e:
            logger.error(f"[BACKGROUND JOB] Error in bulk status update: {str(e)}")
            raise
