"""Research Agent - Analyzes data and extracts insights (REAL sentiment analysis)"""
import json
import time
from typing import Dict, Any
from utils.logger import WorkflowLogger, LogLevel

try:
    from textblob import TextBlob
    HAS_TEXTBLOB = True
except ImportError:
    HAS_TEXTBLOB = False


class ResearchAgent:
    def __init__(self, logger: WorkflowLogger):
        self.logger = logger
        self.name = "Research Agent"

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """REAL sentiment analysis using TextBlob"""
        self.logger.log_action_start("sentiment_analysis", "research_analysis")
        
        start_time = time.time()
        
        if not text or not text.strip():
            return {
                "sentiment": "neutral",
                "score": 0.5,
                "confidence": 0.0,
                "text": text,
                "analysis_type": "sentiment"
            }
        
        try:
            if HAS_TEXTBLOB:
                # REAL sentiment analysis using TextBlob
                blob = TextBlob(text)
                polarity = blob.sentiment.polarity  # -1 to 1
                subjectivity = blob.sentiment.subjectivity  # 0 to 1
                
                # Convert polarity to sentiment label
                if polarity > 0.1:
                    sentiment = "positive"
                    confidence = abs(polarity)
                elif polarity < -0.1:
                    sentiment = "negative"
                    confidence = abs(polarity)
                else:
                    sentiment = "neutral"
                    confidence = 1 - subjectivity
                
                # Extract keywords
                keywords = [phrase for phrase in blob.noun_phrases][:5]
                
                result = {
                    "sentiment": sentiment,
                    "score": (polarity + 1) / 2,  # Normalize to 0-1
                    "confidence": min(confidence, 1.0),
                    "polarity_raw": polarity,
                    "subjectivity": subjectivity,
                    "keywords": keywords,
                    "text": text[:100],
                    "analysis_type": "sentiment",
                    "method": "textblob_real"
                }
            else:
                # Fallback: keyword-based
                result = self._fallback_sentiment(text)
        
        except Exception as e:
            self.logger.log(LogLevel.ERROR, "ResearchAgent", f"Error: {str(e)}", {})
            result = self._fallback_sentiment(text)
        
        duration = time.time() - start_time
        self.logger.log_action_success("sentiment_analysis", "research_analysis", duration)
        self.logger.log(LogLevel.SUCCESS, "[SENTIMENT]", f"✅ {result['sentiment'].upper()} ({result['confidence']:.0%})", result)
        
        return result
    
    def _fallback_sentiment(self, text: str) -> Dict[str, Any]:
        """Fallback sentiment analysis"""
        text_lower = text.lower()
        
        negative_keywords = ["bad", "terrible", "awful", "hate", "worst", "poor", "horrible", "hate", "broken", "fail"]
        positive_keywords = ["good", "great", "excellent", "amazing", "love", "best", "awesome", "perfect"]
        
        negative_count = sum(1 for word in negative_keywords if word in text_lower)
        positive_count = sum(1 for word in positive_keywords if word in text_lower)
        
        if negative_count > positive_count:
            sentiment = "negative"
            score = 0.2
        elif positive_count > negative_count:
            sentiment = "positive"
            score = 0.8
        else:
            sentiment = "neutral"
            score = 0.5
        
        return {
            "sentiment": sentiment,
            "score": score,
            "confidence": 0.6,
            "text": text[:100],
            "analysis_type": "sentiment",
            "method": "keyword_fallback"
        }

    def extract_key_information(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key information from data"""
        self.logger.log_action_start("data_extraction", "research_analysis")
        
        start_time = time.time()
        time.sleep(0.3)
        
        extracted = {
            "customer_name": data.get("name", "Unknown"),
            "customer_id": data.get("id", "N/A"),
            "issue_type": data.get("issue", "General Complaint"),
            "severity": "high" if "critical" in str(data).lower() else "medium",
            "timestamp": data.get("timestamp", ""),
        }
        
        duration = time.time() - start_time
        self.logger.log_action_success("data_extraction", "research_analysis", duration)
        
        return extracted

    def analyze_patterns(self, historical_data: list) -> Dict[str, Any]:
        """Analyze patterns in historical data"""
        self.logger.log_action_start("pattern_analysis", "research_analysis")
        
        start_time = time.time()
        time.sleep(0.4)
        
        if not historical_data:
            return {"patterns": [], "trend": "insufficient_data"}
        
        # Simulate pattern detection
        negative_count = sum(1 for item in historical_data if item.get("sentiment") == "negative")
        pattern_frequency = len(historical_data)
        
        patterns = []
        if negative_count > pattern_frequency * 0.5:
            patterns.append("High complaint rate")
            patterns.append("Potential systemic issue")
        
        duration = time.time() - start_time
        self.logger.log_action_success("pattern_analysis", "research_analysis", duration)
        
        return {
            "patterns_detected": patterns,
            "trend": "increasing" if negative_count > 0 else "stable",
            "recommendation": "Escalate to senior team" if negative_count > 0 else "Standard handling"
        }
