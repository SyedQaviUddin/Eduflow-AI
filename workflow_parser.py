"""Workflow JSON Parser and Converter"""
import json
from typing import Dict, List, Any, Tuple
from datetime import datetime


class WorkflowParser:
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.workflow_data = {}

    def parse_workflow_json(self, workflow_json: Dict[str, Any]) -> Tuple[List[Dict], List[Dict]]:
        """
        Convert workflow JSON to nodes and edges for visualization
        Returns: (nodes, edges)
        """
        self.workflow_data = workflow_json
        self.nodes = []
        self.edges = []

        # Create trigger node
        trigger = workflow_json.get("trigger", "unknown_trigger")
        trigger_node = {
            "id": "trigger_node",
            "label": f"📌 {trigger.upper()}",
            "type": "trigger",
            "title": f"Trigger: {trigger}",
            "color": "#00ff00",
            "size": 30
        }
        self.nodes.append(trigger_node)

        # Create action nodes
        actions = workflow_json.get("actions", [])
        action_ids = {}
        for idx, action in enumerate(actions):
            action_id = action.get("id", f"action_{idx}")
            action_type = action.get("type", "unknown")
            action_desc = action.get("description", "")
            
            action_ids[action_id] = True
            
            action_node = {
                "id": action_id,
                "label": f"⚙️ {action_type}",
                "type": "action",
                "title": f"{action_type}: {action_desc}",
                "color": "#0099ff",
                "size": 25
            }
            self.nodes.append(action_node)
            
            # Connect trigger to first action
            if idx == 0:
                edge = {
                    "from": "trigger_node",
                    "to": action_id,
                    "arrows": "to",
                    "color": "#00ff00",
                    "width": 2
                }
                self.edges.append(edge)
            else:
                # Connect previous action to current
                prev_action_id = actions[idx-1].get("id", f"action_{idx-1}")
                edge = {
                    "from": prev_action_id,
                    "to": action_id,
                    "arrows": "to",
                    "color": "#0099ff",
                    "width": 2
                }
                self.edges.append(edge)

        # Create condition nodes
        conditions = workflow_json.get("conditions", [])
        for condition in conditions:
            condition_id = condition.get("id", "unknown_condition")
            condition_text = condition.get("condition", "")
            
            condition_node = {
                "id": condition_id,
                "label": f"🔀 CONDITION",
                "type": "condition",
                "title": f"If: {condition_text}",
                "color": "#ffaa00",
                "size": 25
            }
            self.nodes.append(condition_node)
            
            # Connect to condition from last action
            if actions:
                last_action_id = actions[-1].get("id", f"action_{len(actions)-1}")
                edge = {
                    "from": last_action_id,
                    "to": condition_id,
                    "arrows": "to",
                    "color": "#ffaa00",
                    "width": 2
                }
                self.edges.append(edge)
            
            # Connect condition to then/else actions
            then_action = condition.get("then_action", "")
            else_action = condition.get("else_action", "")
            
            if then_action and then_action in action_ids:
                edge = {
                    "from": condition_id,
                    "to": then_action,
                    "label": "YES",
                    "arrows": "to",
                    "color": "#00ff00",
                    "width": 2
                }
                self.edges.append(edge)
            
            if else_action and else_action in action_ids:
                edge = {
                    "from": condition_id,
                    "to": else_action,
                    "label": "NO",
                    "arrows": "to",
                    "color": "#ff0000",
                    "width": 2
                }
                self.edges.append(edge)

        # Create notification nodes
        notifications = workflow_json.get("notifications", [])
        for idx, notif in enumerate(notifications):
            notif_type = notif.get("type", "unknown").upper()
            notif_id = f"notification_{idx}"
            
            notif_node = {
                "id": notif_id,
                "label": f"📬 {notif_type}",
                "type": "notification",
                "title": f"{notif_type} Notification",
                "color": "#ff00ff",
                "size": 20
            }
            self.nodes.append(notif_node)
            
            # Connect last action to notification
            if actions:
                last_action_id = actions[-1].get("id", f"action_{len(actions)-1}")
                edge = {
                    "from": last_action_id,
                    "to": notif_id,
                    "arrows": "to",
                    "color": "#ff00ff",
                    "width": 1
                }
                self.edges.append(edge)

        return self.nodes, self.edges

    def get_workflow_statistics(self, workflow_json: Dict[str, Any]) -> Dict[str, Any]:
        """Extract workflow statistics"""
        actions = workflow_json.get("actions", [])
        conditions = workflow_json.get("conditions", [])
        notifications = workflow_json.get("notifications", [])
        
        return {
            "total_actions": len(actions),
            "total_conditions": len(conditions),
            "total_notifications": len(notifications),
            "action_types": [a.get("type", "unknown") for a in actions],
            "notification_types": [n.get("type", "unknown") for n in notifications],
            "trigger": workflow_json.get("trigger", "unknown"),
            "workflow_name": workflow_json.get("name", "Unnamed Workflow"),
            "complexity_score": self._calculate_complexity(len(actions), len(conditions))
        }

    def _calculate_complexity(self, num_actions: int, num_conditions: int) -> float:
        """Calculate workflow complexity score"""
        return min(100, (num_actions * 15) + (num_conditions * 25))

    def validate_workflow(self, workflow_json: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate workflow structure"""
        errors = []
        
        if not workflow_json.get("trigger"):
            errors.append("Missing trigger")
        
        if not workflow_json.get("actions"):
            errors.append("No actions defined")
        
        if len(workflow_json.get("actions", [])) == 0:
            errors.append("Workflow must have at least one action")
        
        # Validate action references in conditions
        action_ids = {a.get("id") for a in workflow_json.get("actions", [])}
        for condition in workflow_json.get("conditions", []):
            if condition.get("then_action") not in action_ids and condition.get("then_action"):
                errors.append(f"Invalid action reference: {condition.get('then_action')}")
            if condition.get("else_action") not in action_ids and condition.get("else_action"):
                errors.append(f"Invalid action reference: {condition.get('else_action')}")
        
        return len(errors) == 0, errors
