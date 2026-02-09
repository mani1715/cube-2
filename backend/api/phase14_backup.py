"""
Phase 14.2 - Backup & Disaster Recovery
Automated database backup, restore, and management functionality
"""

import os
import json
import gzip
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging
from bson import json_util

logger = logging.getLogger(__name__)

# Backup configuration
BACKUP_DIR = Path("/app/backend/backups")
MAX_BACKUPS = 30  # Keep last 30 backups
BACKUP_RETENTION_DAYS = 30


class BackupManager:
    """Manages database backup and restore operations"""
    
    def __init__(self, db):
        self.db = db
        self.backup_dir = BACKUP_DIR
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"BackupManager initialized. Backup directory: {self.backup_dir}")
    
    async def create_backup(self, backup_type: str = "manual", include_collections: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create a complete database backup
        
        Args:
            backup_type: Type of backup (manual, scheduled, pre-migration)
            include_collections: List of collections to backup (None = all)
        
        Returns:
            Dict with backup metadata
        """
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_id = f"backup_{timestamp}"
            backup_path = self.backup_dir / backup_id
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Get all collections to backup
            if include_collections is None:
                collections = await self.db.list_collection_names()
            else:
                collections = include_collections
            
            backup_metadata = {
                "backup_id": backup_id,
                "timestamp": datetime.utcnow(),
                "backup_type": backup_type,
                "collections": [],
                "total_documents": 0,
                "status": "in_progress",
                "error": None
            }
            
            # Backup each collection
            for collection_name in collections:
                try:
                    collection = self.db[collection_name]
                    documents = await collection.find().to_list(length=None)
                    
                    # Save collection data
                    collection_file = backup_path / f"{collection_name}.json.gz"
                    collection_data = json.dumps(documents, default=json_util.default, indent=2)
                    
                    with gzip.open(collection_file, 'wt', encoding='utf-8') as f:
                        f.write(collection_data)
                    
                    doc_count = len(documents)
                    backup_metadata["collections"].append({
                        "name": collection_name,
                        "document_count": doc_count,
                        "file_size_bytes": collection_file.stat().st_size
                    })
                    backup_metadata["total_documents"] += doc_count
                    
                    logger.info(f"Backed up collection '{collection_name}': {doc_count} documents")
                
                except Exception as e:
                    logger.error(f"Error backing up collection '{collection_name}': {e}")
                    backup_metadata["collections"].append({
                        "name": collection_name,
                        "error": str(e)
                    })
            
            # Save metadata
            backup_metadata["status"] = "completed"
            backup_metadata["completed_at"] = datetime.utcnow()
            
            metadata_file = backup_path / "metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(backup_metadata, f, default=json_util.default, indent=2)
            
            # Calculate total backup size
            total_size = sum(f.stat().st_size for f in backup_path.glob("*.json.gz"))
            backup_metadata["total_size_bytes"] = total_size
            backup_metadata["total_size_mb"] = round(total_size / (1024 * 1024), 2)
            
            logger.info(f"✅ Backup completed: {backup_id} ({backup_metadata['total_size_mb']} MB)")
            
            # Cleanup old backups
            await self.cleanup_old_backups()
            
            return backup_metadata
        
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return {
                "backup_id": None,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow()
            }
    
    async def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups"""
        backups = []
        
        for backup_path in sorted(self.backup_dir.glob("backup_*"), reverse=True):
            metadata_file = backup_path / "metadata.json"
            
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    # Calculate backup size
                    total_size = sum(f.stat().st_size for f in backup_path.glob("*.json.gz"))
                    metadata["total_size_mb"] = round(total_size / (1024 * 1024), 2)
                    metadata["backup_path"] = str(backup_path)
                    
                    backups.append(metadata)
                except Exception as e:
                    logger.error(f"Error reading backup metadata from {backup_path}: {e}")
        
        return backups
    
    async def get_backup_details(self, backup_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific backup"""
        backup_path = self.backup_dir / backup_id
        metadata_file = backup_path / "metadata.json"
        
        if not metadata_file.exists():
            return None
        
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Add file listing
            metadata["files"] = []
            for file in backup_path.glob("*.json.gz"):
                metadata["files"].append({
                    "name": file.name,
                    "size_bytes": file.stat().st_size,
                    "size_mb": round(file.stat().st_size / (1024 * 1024), 2)
                })
            
            return metadata
        except Exception as e:
            logger.error(f"Error reading backup details: {e}")
            return None
    
    async def restore_backup(self, backup_id: str, collections: Optional[List[str]] = None, 
                           mode: str = "replace") -> Dict[str, Any]:
        """
        Restore database from backup
        
        Args:
            backup_id: ID of backup to restore
            collections: Specific collections to restore (None = all)
            mode: 'replace' (drop existing), 'merge' (keep existing), 'preview' (dry run)
        
        Returns:
            Dict with restore results
        """
        backup_path = self.backup_dir / backup_id
        metadata_file = backup_path / "metadata.json"
        
        if not metadata_file.exists():
            return {
                "status": "failed",
                "error": f"Backup '{backup_id}' not found"
            }
        
        try:
            with open(metadata_file, 'r') as f:
                backup_metadata = json.load(f)
            
            restore_results = {
                "backup_id": backup_id,
                "restore_mode": mode,
                "started_at": datetime.utcnow(),
                "collections": [],
                "total_documents_restored": 0,
                "status": "in_progress"
            }
            
            # Filter collections if specified
            collections_to_restore = collections if collections else [
                c["name"] for c in backup_metadata["collections"] if "error" not in c
            ]
            
            for collection_name in collections_to_restore:
                collection_file = backup_path / f"{collection_name}.json.gz"
                
                if not collection_file.exists():
                    restore_results["collections"].append({
                        "name": collection_name,
                        "status": "skipped",
                        "error": "Backup file not found"
                    })
                    continue
                
                try:
                    # Read backup data
                    with gzip.open(collection_file, 'rt', encoding='utf-8') as f:
                        documents = json.loads(f.read(), object_hook=json_util.object_hook)
                    
                    if mode == "preview":
                        # Preview mode - don't actually restore
                        restore_results["collections"].append({
                            "name": collection_name,
                            "status": "preview",
                            "document_count": len(documents)
                        })
                        restore_results["total_documents_restored"] += len(documents)
                    else:
                        collection = self.db[collection_name]
                        
                        if mode == "replace":
                            # Drop existing collection
                            await collection.drop()
                            logger.info(f"Dropped collection '{collection_name}'")
                        
                        if documents:
                            # Insert documents
                            result = await collection.insert_many(documents)
                            docs_inserted = len(result.inserted_ids)
                        else:
                            docs_inserted = 0
                        
                        restore_results["collections"].append({
                            "name": collection_name,
                            "status": "success",
                            "documents_restored": docs_inserted
                        })
                        restore_results["total_documents_restored"] += docs_inserted
                        
                        logger.info(f"Restored collection '{collection_name}': {docs_inserted} documents")
                
                except Exception as e:
                    logger.error(f"Error restoring collection '{collection_name}': {e}")
                    restore_results["collections"].append({
                        "name": collection_name,
                        "status": "failed",
                        "error": str(e)
                    })
            
            restore_results["status"] = "completed"
            restore_results["completed_at"] = datetime.utcnow()
            
            logger.info(f"✅ Restore completed: {backup_id} ({restore_results['total_documents_restored']} documents)")
            
            return restore_results
        
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "backup_id": backup_id
            }
    
    async def delete_backup(self, backup_id: str) -> Dict[str, Any]:
        """Delete a specific backup"""
        backup_path = self.backup_dir / backup_id
        
        if not backup_path.exists():
            return {
                "status": "failed",
                "error": f"Backup '{backup_id}' not found"
            }
        
        try:
            shutil.rmtree(backup_path)
            logger.info(f"Deleted backup: {backup_id}")
            
            return {
                "status": "success",
                "backup_id": backup_id,
                "deleted_at": datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Error deleting backup '{backup_id}': {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def cleanup_old_backups(self) -> Dict[str, Any]:
        """Remove old backups based on retention policy"""
        try:
            backups = await self.list_backups()
            deleted = []
            
            # Delete backups older than retention period
            cutoff_date = datetime.utcnow() - timedelta(days=BACKUP_RETENTION_DAYS)
            
            for backup in backups:
                backup_date = datetime.fromisoformat(backup["timestamp"].replace('Z', '+00:00'))
                
                if backup_date < cutoff_date:
                    result = await self.delete_backup(backup["backup_id"])
                    if result["status"] == "success":
                        deleted.append(backup["backup_id"])
            
            # Also enforce max backup count
            if len(backups) > MAX_BACKUPS:
                backups_to_delete = backups[MAX_BACKUPS:]
                for backup in backups_to_delete:
                    result = await self.delete_backup(backup["backup_id"])
                    if result["status"] == "success" and backup["backup_id"] not in deleted:
                        deleted.append(backup["backup_id"])
            
            logger.info(f"Cleanup: Deleted {len(deleted)} old backups")
            
            return {
                "status": "success",
                "deleted_count": len(deleted),
                "deleted_backups": deleted
            }
        
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def get_backup_statistics(self) -> Dict[str, Any]:
        """Get backup system statistics"""
        try:
            backup_dirs = list(self.backup_dir.glob("backup_*"))
            total_size = sum(
                sum(f.stat().st_size for f in backup_path.glob("*.json.gz"))
                for backup_path in backup_dirs
            )
            
            return {
                "total_backups": len(backup_dirs),
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "total_size_gb": round(total_size / (1024 * 1024 * 1024), 2),
                "backup_directory": str(self.backup_dir),
                "retention_days": BACKUP_RETENTION_DAYS,
                "max_backups": MAX_BACKUPS
            }
        except Exception as e:
            logger.error(f"Error getting backup statistics: {e}")
            return {
                "error": str(e)
            }
