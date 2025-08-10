"""Logging handler for llmswap requests and responses."""

import json
import logging
import os
from datetime import datetime
from typing import Optional, Dict, Any


class LLMLogger:
    """Simple logger for LLM requests and responses."""
    
    def __init__(self, log_file: str, log_level: str = "info"):
        """Initialize logger with file and level.
        
        Args:
            log_file: Path to log file
            log_level: Logging level ("debug", "info", "warning", "error")
        """
        self.log_file = log_file
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Configure logger
        self.logger = logging.getLogger("llmswap")
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Add file handler
        handler = logging.FileHandler(log_file)
        handler.setLevel(getattr(logging, log_level.upper()))
        
        # JSON formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
    
    def log_request(self, provider: str, model: str, prompt_length: int, metadata: Optional[Dict[str, Any]] = None):
        """Log an LLM request.
        
        Args:
            provider: Provider name
            model: Model name
            prompt_length: Length of the prompt (for privacy, content not logged)
            metadata: Optional additional metadata
        """
        log_data = {
            "type": "request",
            "timestamp": datetime.now().isoformat(),
            "provider": provider,
            "model": model,
            "prompt_length": prompt_length,
        }
        
        if metadata:
            log_data.update(metadata)
        
        self.logger.info(json.dumps(log_data))
    
    def log_response(self, provider: str, model: str, response_length: int, 
                    latency: float, metadata: Optional[Dict[str, Any]] = None):
        """Log an LLM response.
        
        Args:
            provider: Provider name
            model: Model name
            response_length: Length of the response (for privacy, content not logged)
            latency: Response latency in seconds
            metadata: Optional additional metadata (token counts, etc.)
        """
        log_data = {
            "type": "response",
            "timestamp": datetime.now().isoformat(),
            "provider": provider,
            "model": model,
            "response_length": response_length,
            "latency_seconds": round(latency, 3),
        }
        
        if metadata:
            log_data.update(metadata)
        
        self.logger.info(json.dumps(log_data))