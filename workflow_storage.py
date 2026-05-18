"""Workflow Storage and Management"""
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime


class WorkflowStorage:
    def __init__(self, storage_dir: str = "data/workflows"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

    def save_workflow(self, workflow_id: str, workflow_data: Dict[str, Any], name: str = "") -> bool:
        """Save workflow to JSON storage"""
        try:
            filepath = os.path.join(self.storage_dir, f"{workflow_id}.json")
            workflow_with_metadata = {
                "id": workflow_id,
                "name": name or workflow_data.get("name", f"Workflow-{workflow_id[:8]}"),
                "created_at": datetime.now().isoformat(),
                "enabled": True,
                "execution_count": 0,
                "last_execution": None,
                "executions": [],
                "workflow": workflow_data
            }
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(workflow_with_metadata, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving workflow: {e}")
            return False

    def load_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Load workflow from JSON storage"""
        try:
            filepath = os.path.join(self.storage_dir, f"{workflow_id}.json")
            if not os.path.exists(filepath):
                return None
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading workflow: {e}")
            return None

    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all saved workflows"""
        workflows = []
        os.makedirs(self.storage_dir, exist_ok=True)
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.json'):
                workflow_id = filename.replace('.json', '')
                workflow = self.load_workflow(workflow_id)
                if workflow:
                    workflows.append({
                        "id": workflow_id,
                        "name": workflow.get("name", f"Workflow-{workflow_id[:8]}"),
                        "created_at": workflow.get("created_at", ""),
                        "enabled": workflow.get("enabled", True),
                        "execution_count": workflow.get("execution_count", 0),
                        "last_execution": workflow.get("last_execution", None)
                    })
        
        return sorted(workflows, key=lambda x: x.get('created_at', ''), reverse=True)

    def update_workflow(self, workflow_id: str, updates: Dict[str, Any]) -> bool:
        """Update workflow metadata"""
        try:
            workflow = self.load_workflow(workflow_id)
            if not workflow:
                return False
            
            workflow.update(updates)
            workflow["updated_at"] = datetime.now().isoformat()
            
            filepath = os.path.join(self.storage_dir, f"{workflow_id}.json")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(workflow, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error updating workflow: {e}")
            return False

    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete workflow from storage"""
        try:
            filepath = os.path.join(self.storage_dir, f"{workflow_id}.json")
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception as e:
            print(f"Error deleting workflow: {e}")
            return False

    def duplicate_workflow(self, source_id: str, new_id: str) -> bool:
        """Duplicate a workflow"""
        try:
            source = self.load_workflow(source_id)
            if not source:
                return False
            
            # Get the workflow data (nested under "workflow" key)
            workflow_data = source.get("workflow", {})
            workflow_data["name"] = f"{workflow_data.get('name', 'Workflow')} (Copy)"
            
            # Create new workflow with fresh ID and timestamp
            return self.save_workflow(new_id, workflow_data, name=workflow_data["name"])
        except Exception as e:
            print(f"Error duplicating workflow: {e}")
            return False

    def toggle_workflow_enabled(self, workflow_id: str) -> Optional[bool]:
        """Toggle workflow enabled status"""
        try:
            workflow = self.load_workflow(workflow_id)
            if not workflow:
                return None
            
            new_status = not workflow.get("enabled", False)
            workflow["enabled"] = new_status
            
            filepath = os.path.join(self.storage_dir, f"{workflow_id}.json")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(workflow, f, indent=2, ensure_ascii=False)
            
            return new_status
        except Exception as e:
            print(f"Error toggling workflow: {e}")
            return None

    def increment_execution_count(self, workflow_id: str) -> bool:
        """Increment workflow execution count"""
        try:
            workflow = self.load_workflow(workflow_id)
            if not workflow:
                return False
            
            workflow["execution_count"] = workflow.get("execution_count", 0) + 1
            workflow["last_execution"] = datetime.now().isoformat()
            
            filepath = os.path.join(self.storage_dir, f"{workflow_id}.json")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(workflow, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error incrementing execution count: {e}")
            return False
