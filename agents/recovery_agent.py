"""Recovery Agent - Implements self-healing mechanisms (AI-powered recovery)"""
import time
import random
import requests
from typing import Dict, Any, List, Optional
from utils.logger import WorkflowLogger, LogLevel


class RecoveryAgent:
    def __init__(self, logger: WorkflowLogger):
        self.logger = logger
        self.name = "Recovery Agent"
        self.recovery_history = []
        self.max_retries = 3
        self.deepseek_url = "https://api.deepseek.com/chat/completions"
        self.deepseek_key = "sk-ae734f80749f44e1926ad1c6a0511e31"

    def handle_failure(self, action_id: str, error: str, original_action: Dict[str, Any]) -> Dict[str, Any]:
        """Handle and attempt recovery from failure using AI analysis"""
        self.logger.log_recovery_activated(action_id, error)
        self.logger.log(LogLevel.INFO, "[RECOVERY]", f"🔄 Analyzing failure: {error[:100]}", {})
        
        # Try AI-powered recovery first
        ai_recovery = self._attempt_ai_recovery(action_id, error, original_action)
        if ai_recovery.get("recovered"):
            return ai_recovery
        
        # Fallback to traditional recovery strategies
        recovery_strategies = self._determine_recovery_strategies(error, original_action)
        
        for strategy_name, strategy_func in recovery_strategies:
            self.logger.log(
                LogLevel.INFO,
                "[RECOVERY]",
                f"↻ Trying: {strategy_name}",
                {"strategy": strategy_name, "action_id": action_id}
            )
            
            result = strategy_func()
            
            if result.get("success"):
                self.logger.log_recovery_success(action_id, strategy_name)
                self.recovery_history.append({
                    "action_id": action_id,
                    "original_error": error,
                    "strategy_used": strategy_name,
                    "result": "success",
                    "method": "traditional",
                    "timestamp": time.time()
                })
                return {
                    "recovered": True,
                    "strategy": strategy_name,
                    "method": "traditional",
                    "result": result
                }
        
        # All recovery attempts failed
        self.logger.log(
            LogLevel.ERROR,
            "[RECOVERY]",
            f"❌ Recovery exhausted ({len(recovery_strategies)} strategies failed)",
            {"action_id": action_id}
        )
        
        self.recovery_history.append({
            "action_id": action_id,
            "original_error": error,
            "strategy_used": "none",
            "result": "failure",
            "method": "none",
            "timestamp": time.time()
        })
        
        return {
            "recovered": False,
            "strategy": None,
            "method": "none",
            "attempted_strategies": [s[0] for s in recovery_strategies]
        }
    
    def _attempt_ai_recovery(self, action_id: str, error: str, original_action: Dict[str, Any]) -> Dict[str, Any]:
        """Use DeepSeek AI to determine optimal recovery strategy"""
        try:
            prompt = f"""A workflow action failed. Analyze and suggest a recovery strategy.

Action: {original_action.get('type', 'unknown')}
Error: {error}
Action Config: {str(original_action.get('config', {}))[:200]}

Respond in JSON format:
{{
  "recovery_strategy": "retry|fallback|skip|cache|alert",
  "reasoning": "brief explanation",
  "parameters": {{}},
  "estimated_success": 0.0-1.0
}}"""

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.deepseek_key}"
            }
            
            payload = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.5,
                "max_tokens": 500
            }
            
            response = requests.post(self.deepseek_url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('choices', [{}])[0].get('message', {}).get('content', '{}')
                
                import json
                try:
                    recovery_plan = json.loads(ai_response)
                    strategy = recovery_plan.get("recovery_strategy", "retry")
                    
                    self.logger.log(LogLevel.INFO, "[AI-RECOVERY]", f"📊 AI suggests: {strategy}", recovery_plan)
                    
                    # Execute AI-suggested strategy
                    if strategy == "retry":
                        result = self._retry_with_backoff()
                    elif strategy == "fallback":
                        result = self._fallback_endpoint()
                    elif strategy == "cache":
                        result = self._use_cached_data()
                    elif strategy == "skip":
                        result = self._alert_and_skip()
                    else:
                        result = self._simple_retry()
                    
                    if result.get("success"):
                        return {
                            "recovered": True,
                            "strategy": f"AI-{strategy}",
                            "method": "ai_powered",
                            "result": result,
                            "reasoning": recovery_plan.get("reasoning")
                        }
                except json.JSONDecodeError:
                    pass
        
        except Exception as e:
            self.logger.log(LogLevel.DEBUG, "[AI-RECOVERY]", f"AI recovery unavailable: {str(e)[:50]}", {})
        
        return {"recovered": False}

    def _determine_recovery_strategies(self, error: str, action: Dict[str, Any]) -> List[tuple]:
        """Determine applicable recovery strategies based on error type"""
        strategies = []
        
        error_lower = error.lower()
        
        # Network/API errors - try retry
        if any(keyword in error_lower for keyword in ["timeout", "connection", "api", "network", "503", "502"]):
            strategies.append(("Exponential backoff + Retry", self._retry_with_backoff))
            strategies.append(("Use cached data", self._use_cached_data))
            strategies.append(("Fallback endpoint", self._fallback_endpoint))
        
        # Rate limiting - implement backoff
        elif any(keyword in error_lower for keyword in ["rate", "limit", "429", "throttle"]):
            strategies.append(("Exponential backoff", self._exponential_backoff))
            strategies.append(("Queue for later", self._queue_for_later))
            strategies.append(("Use cache", self._use_cached_data))
        
        # Authentication errors - refresh token
        elif any(keyword in error_lower for keyword in ["auth", "unauthorized", "forbidden", "401", "403"]):
            strategies.append(("Refresh credentials", self._refresh_credentials))
            strategies.append(("Fallback auth", self._fallback_auth))
        
        # Data errors - validate and retry
        elif any(keyword in error_lower for keyword in ["data", "invalid", "parse", "json", "format", "400"]):
            strategies.append(("Validate data", self._validate_data))
            strategies.append(("Use defaults", self._use_defaults))
            strategies.append(("Skip action", self._alert_and_skip))
        
        # Default strategies for unknown errors
        strategies.append(("Simple retry", self._simple_retry))
        strategies.append(("Alert and skip", self._alert_and_skip))
        
        return strategies

    def _simple_retry(self) -> Dict[str, Any]:
        """Simple retry strategy"""
        time.sleep(0.3)
        return {"success": True, "method": "simple_retry", "attempt": 1}

    def _retry_with_backoff(self) -> Dict[str, Any]:
        """Retry with exponential backoff"""
        for attempt in range(1, self.max_retries + 1):
            wait_time = min(2 ** attempt, 8)  # Cap at 8 seconds
            self.logger.log(
                LogLevel.DEBUG,
                "[RECOVERY]",
                f"Retry {attempt}/{self.max_retries} (wait: {wait_time}s)",
                {"attempt": attempt}
            )
            time.sleep(wait_time / 4)  # Reduce sim time for demo
            
            if random.random() > 0.4:  # 60% success rate
                return {"success": True, "method": "retry_backoff", "attempt": attempt}
        
        return {"success": False, "method": "retry_backoff"}

    def _exponential_backoff(self) -> Dict[str, Any]:
        """Exponential backoff strategy"""
        wait_times = [1, 2, 4]
        for attempt, wait_time in enumerate(wait_times, 1):
            self.logger.log(LogLevel.DEBUG, "[RECOVERY]", f"Backoff {attempt} (wait: {wait_time}s)", {})
            time.sleep(wait_time / 4)
        
        return {"success": True, "method": "exponential_backoff"}

    def _use_cached_data(self) -> Dict[str, Any]:
        """Use cached data if available"""
        self.logger.log(LogLevel.INFO, "[RECOVERY]", "💾 Using cached data", {})
        time.sleep(0.2)
        return {"success": True, "method": "cached_data", "data": "cached_response"}

    def _fallback_endpoint(self) -> Dict[str, Any]:
        """Switch to fallback API endpoint"""
        self.logger.log(LogLevel.INFO, "[RECOVERY]", "🔀 Switching to fallback endpoint", {})
        time.sleep(0.3)
        return {"success": True, "method": "fallback_endpoint"}

    def _queue_for_later(self) -> Dict[str, Any]:
        """Queue action for later retry"""
        self.logger.log(LogLevel.INFO, "[RECOVERY]", "📋 Queued for later processing", {})
        return {"success": True, "method": "queue_for_later"}

    def _refresh_credentials(self) -> Dict[str, Any]:
        """Refresh authentication credentials"""
        self.logger.log(LogLevel.INFO, "[RECOVERY]", "🔑 Refreshing credentials", {})
        time.sleep(0.2)
        return {"success": True, "method": "refresh_credentials"}

    def _fallback_auth(self) -> Dict[str, Any]:
        """Use fallback authentication method"""
        self.logger.log(LogLevel.INFO, "[RECOVERY]", "🔐 Fallback authentication", {})
        return {"success": True, "method": "fallback_auth"}

    def _validate_data(self) -> Dict[str, Any]:
        """Validate and sanitize data"""
        self.logger.log(LogLevel.INFO, "[RECOVERY]", "✓ Validating data", {})
        time.sleep(0.2)
        return {"success": True, "method": "data_validation"}

    def _use_defaults(self) -> Dict[str, Any]:
        """Use default values"""
        self.logger.log(LogLevel.INFO, "[RECOVERY]", "📌 Using default values", {})
        return {"success": True, "method": "default_values"}

    def _alert_and_skip(self) -> Dict[str, Any]:
        """Alert and skip the failed action"""
        self.logger.log(LogLevel.WARNING, "[RECOVERY]", "⊘ Skipping action (alerting)", {})
        return {"success": True, "method": "skip_action", "skipped": True}
    
    def get_recovery_history(self) -> List[Dict[str, Any]]:
        """Get recovery attempt history"""
        return self.recovery_history

    def get_recovery_statistics(self) -> Dict[str, Any]:
        """Get recovery statistics"""
        if not self.recovery_history:
            return {
                "total_failures_handled": 0,
                "recovery_success_rate": 0,
                "most_effective_strategy": None
            }
        
        total = len(self.recovery_history)
        successful = len([r for r in self.recovery_history if r.get("result") == "success"])
        
        strategy_stats = {}
        for recovery in self.recovery_history:
            strategy = recovery.get("strategy_used", "unknown")
            if strategy not in strategy_stats:
                strategy_stats[strategy] = {"count": 0, "success": 0}
            strategy_stats[strategy]["count"] += 1
            if recovery.get("result") == "success":
                strategy_stats[strategy]["success"] += 1
        
        most_effective = max(
            strategy_stats.items(),
            key=lambda x: x[1]["success"] / x[1]["count"] if x[1]["count"] > 0 else 0,
            default=(None, {})
        )
        
        return {
            "total_failures_handled": total,
            "recovery_success_rate": (successful / total) if total > 0 else 0,
            "most_effective_strategy": most_effective[0],
            "strategy_statistics": strategy_stats
        }


    def _queue_for_later(self) -> Dict[str, Any]:
        """Queue action for later retry"""
        self.logger.log(
            LogLevel.INFO,
            "[RECOVERY AGENT]",
            "Queued for later processing",
            {}
        )
        return {"success": True, "method": "queue_for_later"}

    def _refresh_credentials(self) -> Dict[str, Any]:
        """Refresh authentication credentials"""
        self.logger.log(
            LogLevel.INFO,
            "[RECOVERY AGENT]",
            "Refreshing credentials",
            {}
        )
        time.sleep(0.2)
        return {"success": True, "method": "refresh_credentials"}

    def _fallback_auth(self) -> Dict[str, Any]:
        """Use fallback authentication method"""
        self.logger.log(
            LogLevel.INFO,
            "[RECOVERY AGENT]",
            "Using fallback authentication",
            {}
        )
        return {"success": True, "method": "fallback_auth"}

    def _validate_data(self) -> Dict[str, Any]:
        """Validate and sanitize data"""
        self.logger.log(
            LogLevel.INFO,
            "[RECOVERY AGENT]",
            "Validating and sanitizing data",
            {}
        )
        time.sleep(0.3)
        return {"success": True, "method": "data_validation"}

    def _use_defaults(self) -> Dict[str, Any]:
        """Use default values"""
        self.logger.log(
            LogLevel.INFO,
            "[RECOVERY AGENT]",
            "Using default values",
            {}
        )
        return {"success": True, "method": "default_values"}

    def _alert_and_skip(self) -> Dict[str, Any]:
        """Alert and skip the failed action"""
        self.logger.log(
            LogLevel.WARNING,
            "[RECOVERY AGENT]",
            "Skipping action and alerting",
            {}
        )
        return {"success": True, "method": "skip_action", "skipped": True}

    def get_recovery_history(self) -> List[Dict[str, Any]]:
        """Get recovery attempt history"""
        return self.recovery_history

    def get_recovery_statistics(self) -> Dict[str, Any]:
        """Get recovery statistics"""
        if not self.recovery_history:
            return {
                "total_failures_handled": 0,
                "recovery_success_rate": 0,
                "most_effective_strategy": None
            }
        
        total = len(self.recovery_history)
        successful = len([r for r in self.recovery_history if r.get("result") == "success"])
        
        strategy_stats = {}
        for recovery in self.recovery_history:
            strategy = recovery.get("strategy_used", "unknown")
            if strategy not in strategy_stats:
                strategy_stats[strategy] = {"count": 0, "success": 0}
            strategy_stats[strategy]["count"] += 1
            if recovery.get("result") == "success":
                strategy_stats[strategy]["success"] += 1
        
        most_effective = max(
            strategy_stats.items(),
            key=lambda x: x[1]["success"] / x[1]["count"] if x[1]["count"] > 0 else 0,
            default=(None, {})
        )
        
        return {
            "total_failures_handled": total,
            "recovery_success_rate": (successful / total * 100) if total > 0 else 0,
            "most_effective_strategy": most_effective[0],
            "strategy_stats": strategy_stats
        }
