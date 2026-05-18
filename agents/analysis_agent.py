"""Analysis Agent - Makes decisions based on data"""
import json
import time
from typing import Dict, Any, List
from utils.logger import WorkflowLogger, LogLevel


class AnalysisAgent:
    def __init__(self, logger: WorkflowLogger):
        self.logger = logger
        self.name = "Analysis Agent"

    def evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate a workflow condition"""
        self.logger.log_action_start("condition_evaluation", "analysis")
        
        start_time = time.time()
        time.sleep(0.2)
        
        # Parse and evaluate condition
        result = self._parse_condition(condition, context)
        
        duration = time.time() - start_time
        self.logger.log_condition_evaluation("condition_1", condition, result)
        self.logger.log_action_success("condition_evaluation", "analysis", duration)
        
        return result

    def _parse_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Simple condition parser"""
        condition_lower = condition.lower()
        
        # Handle sentiment checks
        if "sentiment == 'negative'" in condition or "sentiment=negative" in condition_lower:
            return context.get("sentiment") == "negative"
        
        if "sentiment == 'positive'" in condition or "sentiment=positive" in condition_lower:
            return context.get("sentiment") == "positive"
        
        # Handle score checks
        if "score >" in condition_lower or "score>" in condition_lower:
            threshold = float(condition.split(">")[1].strip()) if ">" in condition else 0.5
            return context.get("score", 0) > threshold
        
        # Handle severity checks
        if "severity" in condition_lower:
            return context.get("severity") == "high"
        
        return False

    def make_decision(self, data: Dict[str, Any], rules: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make decision based on rules"""
        self.logger.log_action_start("decision_making", "analysis")
        
        start_time = time.time()
        time.sleep(0.3)
        
        if not isinstance(data, dict):
            data = {"sentiment": data}

        if rules is None:
            rules = []

        recommended_actions = []
        confidence_score = 0.85
        
        # Apply rules
        for rule in rules:
            condition = rule.get("condition", "")
            action = rule.get("action", "")
            
            if self._parse_condition(condition, data):
                recommended_actions.append(action)
        
        if not recommended_actions:
            # Default action if no rules match
            if data.get("sentiment") == "negative":
                recommended_actions = ["escalate", "notify_admin"]
            else:
                recommended_actions = ["standard_response"]
        
        duration = time.time() - start_time
        self.logger.log_action_success("decision_making", "analysis", duration)
        
        return {
            "recommended_actions": recommended_actions,
            "confidence": confidence_score,
            "reasoning": f"Based on {len(rules)} rules and context analysis"
        }

    def assess_risk(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk level"""
        self.logger.log_action_start("risk_assessment", "analysis")
        
        start_time = time.time()
        time.sleep(0.25)
        
        risk_score = 0.0
        risk_factors = []
        
        # Evaluate risk factors
        if context.get("sentiment") == "negative":
            risk_score += 0.4
            risk_factors.append("Negative customer sentiment")
        
        if context.get("severity") == "high":
            risk_score += 0.3
            risk_factors.append("High severity issue")
        
        if context.get("score", 1.0) < 0.3:
            risk_score += 0.2
            risk_factors.append("Low confidence score")
        
        risk_level = "high" if risk_score > 0.6 else "medium" if risk_score > 0.3 else "low"
        
        duration = time.time() - start_time
        self.logger.log_action_success("risk_assessment", "analysis", duration)
        
        return {
            "risk_score": min(1.0, risk_score),
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "recommended_mitigation": ["Prioritize review", "Assign senior agent"] if risk_score > 0.6 else []
        }

    def prioritize_actions(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize actions based on urgency"""
        self.logger.log_action_start("action_prioritization", "analysis")
        
        start_time = time.time()
        time.sleep(0.2)
        
        # Sort by priority (assuming each action has a priority field)
        prioritized = sorted(actions, key=lambda x: x.get("priority", 5), reverse=True)
        
        duration = time.time() - start_time
        self.logger.log_action_success("action_prioritization", "analysis", duration)
        
        return prioritized
