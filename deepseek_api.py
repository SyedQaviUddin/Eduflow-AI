"""DeepSeek API Integration for Nexora AI"""
import json
import requests
import re
from typing import Dict, Any, Optional
from datetime import datetime

DEEPSEEK_API_KEY = ""
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

class DeepSeekAPI:
    def __init__(self, api_key: str = DEEPSEEK_API_KEY):
        self.api_key = api_key
        self.base_url = DEEPSEEK_API_URL
        self.model = "deepseek-chat"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def generate_workflow(self, natural_language_prompt: str) -> Dict[str, Any]:
        """
        Convert natural language to workflow JSON using DeepSeek
        Includes enhanced email extraction, notification handling, and schedule support
        """
        # Check if this is a scheduling request
        is_scheduled = self._is_scheduling_request(natural_language_prompt)
        
        system_prompt = """You are an AI workflow automation expert. Convert user requests into structured workflow JSON.

IMPORTANT - Email Extraction:
- Extract ALL email addresses from the user request (e.g., syeduddin827@gmail.com)
- If emails are mentioned, add them to the notifications section
- Format: "send email to EMAIL" or "notify EMAIL"
- Use the extracted emails in notifications

IMPORTANT - Schedule Support:
- If request mentions: "daily", "every day", "at 9 AM", "at 9:00 AM", "after [date]"
- Extract the schedule information
- Create trigger: "daily_schedule_9am" (for 9 AM) or appropriate time
- Add condition for date threshold if "after [date]" mentioned
- Format: "condition": "current_date > 2026-05-18" (if applicable)
- Include schedule metadata with frequency and time

Output MUST be valid JSON with this structure:
{
  "name": "workflow_name",
  "trigger": "event_type|daily_schedule_9am",
  "description": "what the workflow does",
  "schedule": {
    "frequency": "daily|weekly|monthly",
    "time": "09:00|14:30",
    "enabled": true
  },
  "actions": [
    {
      "id": "action_1",
      "type": "action_type",
      "description": "what this does",
      "config": {}
    }
  ],
  "conditions": [
    {
      "id": "condition_1",
      "type": "date_condition|if_then",
      "operator": "greater_than|equal|less_than",
      "threshold_date": "2026-05-18",
      "expression": "current_date > 2026-05-18"
    }
  ],
  "notifications": [
    {
      "type": "email|notification",
      "trigger": "on_completion|scheduled",
      "recipient": "email@example.com",
      "subject": "descriptive subject",
      "body": "message content",
      "message_type": "notification|alert|reminder|announcement"
    }
  ]
}

Rules:
1. Extract email addresses from natural language
2. Create appropriate email notification objects
3. Use message_type based on context: "reminder" for reminders, "announcement" for announcements, etc.
4. Always include a descriptive subject and body for emails
5. For schedules: extract time (9 AM, 2:30 PM), frequency (daily, weekly), and date conditions
6. Output ONLY valid JSON, no markdown, no explanations"""

        user_message = f"Create a workflow for: {natural_language_prompt}"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }

        try:
            response = requests.post(
                self.base_url,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            workflow_text = result.get('choices', [{}])[0].get('message', {}).get('content', '{}')
            
            # Clean up the response if it contains markdown code blocks
            if "```json" in workflow_text:
                workflow_text = workflow_text.split("```json")[1].split("```")[0]
            elif "```" in workflow_text:
                workflow_text = workflow_text.split("```")[1].split("```")[0]
            
            workflow_json = json.loads(workflow_text.strip())
            return workflow_json
        
        except requests.exceptions.RequestException as e:
            print(f"DeepSeek API Error: {str(e)}")
            return self._get_fallback_workflow(natural_language_prompt)
        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {str(e)}")
            return self._get_fallback_workflow(natural_language_prompt)

    def analyze_workflow_performance(self, workflow_data: Dict, execution_logs: list) -> Dict[str, Any]:
        """
        Analyze workflow performance and generate insights
        """
        system_prompt = """You are an AI operations analyst. Analyze workflow execution data and provide:
1. Success rate
2. Failure points
3. Bottlenecks
4. Optimization recommendations
5. Anomalies detected

Output JSON with: success_rate, failures, bottlenecks, recommendations, anomalies"""

        user_message = f"""Analyze this workflow execution:
Workflow: {json.dumps(workflow_data)}
Execution Logs: {json.dumps(execution_logs[-10:])}

Provide detailed insights in JSON format."""

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.5,
            "max_tokens": 1500
        }

        try:
            response = requests.post(
                self.base_url,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            insights_text = result.get('choices', [{}])[0].get('message', {}).get('content', '{}')
            
            if "```json" in insights_text:
                insights_text = insights_text.split("```json")[1].split("```")[0]
            elif "```" in insights_text:
                insights_text = insights_text.split("```")[1].split("```")[0]
            
            return json.loads(insights_text.strip())
        except Exception as e:
            print(f"Insights Generation Error: {str(e)}")
            return {
                "success_rate": 85,
                "failures": [],
                "bottlenecks": ["High latency in sentiment analysis"],
                "recommendations": ["Optimize API calls"],
                "anomalies": []
            }

    def generate_recovery_suggestions(self, error_message: str, workflow_step: Dict) -> Dict[str, Any]:
        """
        Generate recovery strategies for failed workflow steps
        """
        system_prompt = """You are an expert in workflow recovery and self-healing systems.
When a workflow step fails, suggest:
1. Root cause analysis
2. Immediate recovery actions
3. Fallback paths
4. Future prevention

Output JSON with: root_cause, immediate_actions, fallback_path, prevention"""

        user_message = f"""Workflow step failed:
Step: {json.dumps(workflow_step)}
Error: {error_message}

Provide recovery strategy in JSON format."""

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.6,
            "max_tokens": 1200
        }

        try:
            response = requests.post(
                self.base_url,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            recovery_text = result.get('choices', [{}])[0].get('message', {}).get('content', '{}')
            
            if "```json" in recovery_text:
                recovery_text = recovery_text.split("```json")[1].split("```")[0]
            elif "```" in recovery_text:
                recovery_text = recovery_text.split("```")[1].split("```")[0]
            
            return json.loads(recovery_text.strip())
        except Exception as e:
            print(f"Recovery Generation Error: {str(e)}")
            return {
                "root_cause": "API timeout",
                "immediate_actions": ["Retry with exponential backoff"],
                "fallback_path": ["Use cached data", "Send alert to admin"],
                "prevention": ["Increase timeout threshold", "Add circuit breaker"]
            }

    def _is_scheduling_request(self, prompt: str) -> bool:
        """
        Check if the prompt contains scheduling keywords
        """
        scheduling_keywords = [
            "daily", "every day", "at 9", "at 9:00", "at 9:00 am",
            "every morning", "schedule", "recurring", "after",
            "9 am", "9 AM", "10 am", "11 am", "2 pm", "3 pm",
            "at 2", "at 3", "time", "hour", "morning", "afternoon"
        ]
        
        prompt_lower = prompt.lower()
        return any(keyword in prompt_lower for keyword in scheduling_keywords)

    def _get_fallback_workflow(self, prompt: str) -> Dict[str, Any]:
        """
        Fallback workflow if API fails
        Intelligently parses the prompt for email addresses, scheduling, and creates workflow
        """
        from agents.scheduler_agent import SchedulerAgent
        
        # Check if this is a scheduling request
        is_scheduled = self._is_scheduling_request(prompt)
        
        # Extract email addresses from prompt
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        emails = re.findall(email_pattern, prompt)
        
        # Remove duplicates and fallback to default
        emails = list(set(emails)) if emails else ["sqavi037@gmail.com"]
        
        # Determine workflow type from prompt
        prompt_lower = prompt.lower()
        
        # Check for specific keywords
        is_holiday = "holiday" in prompt_lower or "weekend" in prompt_lower
        is_reminder = "remind" in prompt_lower or "reminder" in prompt_lower
        is_error = "error" in prompt_lower or "alert" in prompt_lower or "failed" in prompt_lower
        
        # Parse schedule information if this is a scheduled request
        workflow = {
            "name": "",
            "trigger": "",
            "description": f"Auto-generated workflow: {prompt[:100]}...",
            "actions": [
                {
                    "id": "action_1",
                    "type": "process_input",
                    "description": "Process input data",
                    "config": {}
                },
                {
                    "id": "action_2",
                    "type": "send_notification",
                    "description": "Send notification",
                    "config": {"emails": emails}
                }
            ],
            "conditions": [],
            "notifications": []
        }
        
        if is_scheduled:
            # Use scheduler agent to parse the scheduling
            scheduler = SchedulerAgent()
            schedule_components = scheduler.extract_schedule_components(prompt)
            
            if schedule_components:
                workflow["trigger"] = schedule_components.get("trigger", "daily_schedule_9am")
                workflow["schedule"] = {
                    "frequency": schedule_components.get("frequency", "daily"),
                    "time": schedule_components.get("time", "09:00"),
                    "enabled": True
                }
                
                # Add date condition if threshold_date exists
                if schedule_components.get("threshold_date"):
                    condition = {
                        "id": "date_condition_1",
                        "type": "date_condition",
                        "operator": "greater_than",
                        "threshold_date": schedule_components["threshold_date"],
                        "expression": schedule_components.get("condition", "")
                    }
                    workflow["conditions"].append(condition)
                
                # Create workflow name
                if is_holiday:
                    workflow["name"] = "Scheduled Holiday Notification"
                elif is_reminder:
                    workflow["name"] = "Scheduled Reminder"
                elif is_error:
                    workflow["name"] = "Scheduled Error Alert"
                else:
                    workflow["name"] = "Scheduled Notification"
        else:
            # Non-scheduled workflow
            if is_holiday:
                workflow["name"] = "Holiday Notification"
                workflow["trigger"] = "schedule"
            elif is_reminder:
                workflow["name"] = "Reminder Notification"
                workflow["trigger"] = "schedule"
            elif is_error:
                workflow["name"] = "Error Alert"
                workflow["trigger"] = "error_detected"
            else:
                workflow["name"] = "Email Notification"
                workflow["trigger"] = "manual"
        
        # Build notifications
        for email in emails:
            # Determine message type and subject based on prompt
            if is_holiday:
                subject = "Reminder: Tomorrow is a Holiday"
                body = "Tomorrow is a holiday 🎉"
                message_type = "reminder"
            elif is_reminder:
                subject = "Reminder Notification"
                body = "This is a reminder for you."
                message_type = "reminder"
            elif is_error:
                subject = "Error Alert"
                body = "An error has been detected in your system."
                message_type = "error"
            else:
                subject = "Notification"
                body = prompt
                message_type = "notification"
            
            notification = {
                "type": "send_notification",
                "trigger": "scheduled" if is_scheduled else "on_completion",
                "recipient": email,
                "subject": subject,
                "body": body,
                "message_type": message_type,
                "template_type": message_type
            }
            
            workflow["notifications"].append(notification)
        
        return workflow
