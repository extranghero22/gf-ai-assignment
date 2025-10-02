"""
Comprehensive AI Error Logging System
"""

import logging
import json
import time
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories for AI system"""
    API_ERROR = "api_error"
    CONTEXT_LOSS = "context_loss"
    RESPONSE_QUALITY = "response_quality"
    SAFETY_VIOLATION = "safety_violation"
    CONVERSATION_DISCONNECT = "conversation_disconnect"
    ENERGY_ANALYSIS_ERROR = "energy_analysis_error"
    FALLBACK_USED = "fallback_used"
    TIMEOUT = "timeout"
    VALIDATION_ERROR = "validation_error"

@dataclass
class AIError:
    """Structured AI error information"""
    timestamp: float
    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    context: Dict[str, Any]
    user_message: Optional[str] = None
    ai_response: Optional[str] = None
    conversation_history: Optional[List[Dict[str, Any]]] = None
    energy_signature: Optional[Dict[str, Any]] = None
    safety_status: Optional[str] = None
    model_used: Optional[str] = None
    fallback_used: bool = False
    stack_trace: Optional[str] = None

class AIErrorLogger:
    """Comprehensive AI error logging system"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        self._ensure_log_directory()
        
        # Setup structured logging
        self.logger = logging.getLogger('ai_error_logger')
        self.logger.setLevel(logging.DEBUG)
        
        # File handler for detailed logs
        file_handler = logging.FileHandler(
            os.path.join(log_dir, f'ai_errors_{datetime.now().strftime("%Y%m%d")}.log')
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler for immediate feedback
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # JSON formatter for structured logs
        json_formatter = logging.Formatter('%(message)s')
        file_handler.setFormatter(json_formatter)
        
        # Simple formatter for console
        simple_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(simple_formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Error statistics
        self.error_stats = {
            'total_errors': 0,
            'errors_by_category': {},
            'errors_by_severity': {},
            'recent_errors': []
        }
    
    def _ensure_log_directory(self):
        """Ensure log directory exists"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def _generate_error_id(self) -> str:
        """Generate unique error ID"""
        return f"ERR_{int(time.time() * 1000)}_{hash(time.time()) % 10000:04d}"
    
    def log_ai_error(self, 
                    category: ErrorCategory,
                    severity: ErrorSeverity,
                    message: str,
                    context: Dict[str, Any] = None,
                    user_message: str = None,
                    ai_response: str = None,
                    conversation_history: List[Dict[str, Any]] = None,
                    energy_signature: Dict[str, Any] = None,
                    safety_status: str = None,
                    model_used: str = None,
                    fallback_used: bool = False,
                    exception: Exception = None) -> str:
        """
        Log an AI error with comprehensive context
        
        Returns:
            str: Error ID for tracking
        """
        error_id = self._generate_error_id()
        
        # Prepare error data
        error_data = AIError(
            timestamp=time.time(),
            error_id=error_id,
            category=category,
            severity=severity,
            message=message,
            context=context or {},
            user_message=user_message,
            ai_response=ai_response,
            conversation_history=conversation_history,
            energy_signature=energy_signature,
            safety_status=safety_status,
            model_used=model_used,
            fallback_used=fallback_used,
            stack_trace=str(exception) if exception else None
        )
        
        # Log as JSON for structured analysis
        log_entry = {
            'error_id': error_id,
            'timestamp': error_data.timestamp,
            'datetime': datetime.fromtimestamp(error_data.timestamp).isoformat(),
            'category': category.value,
            'severity': severity.value,
            'message': message,
            'context': context or {},
            'user_message': user_message,
            'ai_response': ai_response,
            'conversation_history': conversation_history,
            'energy_signature': energy_signature,
            'safety_status': safety_status,
            'model_used': model_used,
            'fallback_used': fallback_used,
            'stack_trace': str(exception) if exception else None
        }
        
        # Log to file
        self.logger.info(json.dumps(log_entry, default=str))
        
        # Log to console for immediate feedback
        if severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            self.logger.error(f"[CRITICAL] {severity.value.upper()} AI ERROR [{category.value}]: {message}")
            if user_message:
                self.logger.error(f"   User message: {user_message[:100]}...")
            if ai_response:
                self.logger.error(f"   AI response: {ai_response[:100]}...")
        elif severity == ErrorSeverity.MEDIUM:
            self.logger.warning(f"[WARNING] {severity.value.upper()} AI ERROR [{category.value}]: {message}")
        else:
            self.logger.info(f"[INFO] {severity.value.upper()} AI ERROR [{category.value}]: {message}")
        
        # Update statistics
        self._update_error_stats(error_data)
        
        return error_id
    
    def _update_error_stats(self, error: AIError):
        """Update error statistics"""
        self.error_stats['total_errors'] += 1
        
        # Update category stats
        category = error.category.value
        if category not in self.error_stats['errors_by_category']:
            self.error_stats['errors_by_category'][category] = 0
        self.error_stats['errors_by_category'][category] += 1
        
        # Update severity stats
        severity = error.severity.value
        if severity not in self.error_stats['errors_by_severity']:
            self.error_stats['errors_by_severity'][severity] = 0
        self.error_stats['errors_by_severity'][severity] += 1
        
        # Keep recent errors (last 50)
        self.error_stats['recent_errors'].append({
            'error_id': error.error_id,
            'timestamp': error.timestamp,
            'category': error.category.value,
            'severity': error.severity.value,
            'message': error.message
        })
        
        if len(self.error_stats['recent_errors']) > 50:
            self.error_stats['recent_errors'] = self.error_stats['recent_errors'][-50:]
    
    def log_conversation_disconnect(self, 
                                  user_message: str,
                                  ai_response: str,
                                  conversation_history: List[Dict[str, Any]],
                                  context: Dict[str, Any] = None) -> str:
        """
        Log conversation disconnect errors specifically
        
        Returns:
            str: Error ID for tracking
        """
        return self.log_ai_error(
            category=ErrorCategory.CONVERSATION_DISCONNECT,
            severity=ErrorSeverity.HIGH,
            message="AI response does not maintain conversation context",
            context=context or {},
            user_message=user_message,
            ai_response=ai_response,
            conversation_history=conversation_history
        )
    
    def log_api_error(self, 
                     model: str,
                     error: Exception,
                     user_message: str = None,
                     context: Dict[str, Any] = None) -> str:
        """
        Log API errors
        
        Returns:
            str: Error ID for tracking
        """
        return self.log_ai_error(
            category=ErrorCategory.API_ERROR,
            severity=ErrorSeverity.MEDIUM,
            message=f"API error with {model}: {str(error)}",
            context=context or {},
            user_message=user_message,
            model_used=model,
            exception=error
        )
    
    def log_fallback_used(self, 
                         reason: str,
                         user_message: str = None,
                         context: Dict[str, Any] = None) -> str:
        """
        Log when fallback responses are used
        
        Returns:
            str: Error ID for tracking
        """
        return self.log_ai_error(
            category=ErrorCategory.FALLBACK_USED,
            severity=ErrorSeverity.LOW,
            message=f"Fallback response used: {reason}",
            context=context or {},
            user_message=user_message,
            fallback_used=True
        )
    
    def log_response_quality_issue(self, 
                                 user_message: str,
                                 ai_response: str,
                                 issue_description: str,
                                 conversation_history: List[Dict[str, Any]] = None,
                                 context: Dict[str, Any] = None) -> str:
        """
        Log response quality issues
        
        Returns:
            str: Error ID for tracking
        """
        return self.log_ai_error(
            category=ErrorCategory.RESPONSE_QUALITY,
            severity=ErrorSeverity.MEDIUM,
            message=f"Response quality issue: {issue_description}",
            context=context or {},
            user_message=user_message,
            ai_response=ai_response,
            conversation_history=conversation_history
        )
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics"""
        return self.error_stats.copy()
    
    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent errors"""
        return self.error_stats['recent_errors'][-limit:]
    
    def save_error_report(self, filename: str = None) -> str:
        """Save comprehensive error report"""
        if filename is None:
            filename = f"ai_error_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = os.path.join(self.log_dir, filename)
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'statistics': self.error_stats,
            'summary': {
                'total_errors': self.error_stats['total_errors'],
                'most_common_category': max(self.error_stats['errors_by_category'].items(), 
                                          key=lambda x: x[1])[0] if self.error_stats['errors_by_category'] else None,
                'highest_severity': max(self.error_stats['errors_by_severity'].items(), 
                                      key=lambda x: x[1])[0] if self.error_stats['errors_by_severity'] else None
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return filepath

# Global error logger instance
error_logger = AIErrorLogger()

# Convenience functions for easy access
def log_ai_error(category: ErrorCategory, severity: ErrorSeverity, message: str, **kwargs) -> str:
    """Log an AI error"""
    return error_logger.log_ai_error(category, severity, message, **kwargs)

def log_conversation_disconnect(user_message: str, ai_response: str, conversation_history: List[Dict[str, Any]], **kwargs) -> str:
    """Log conversation disconnect"""
    return error_logger.log_conversation_disconnect(user_message, ai_response, conversation_history, **kwargs)

def log_api_error(model: str, error: Exception, **kwargs) -> str:
    """Log API error"""
    return error_logger.log_api_error(model, error, **kwargs)

def log_fallback_used(reason: str, **kwargs) -> str:
    """Log fallback usage"""
    return error_logger.log_fallback_used(reason, **kwargs)

def log_response_quality_issue(user_message: str, ai_response: str, issue_description: str, **kwargs) -> str:
    """Log response quality issue"""
    return error_logger.log_response_quality_issue(user_message, ai_response, issue_description, **kwargs)

def get_error_statistics() -> Dict[str, Any]:
    """Get error statistics"""
    return error_logger.get_error_statistics()

def get_recent_errors(limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent errors"""
    return error_logger.get_recent_errors(limit)
