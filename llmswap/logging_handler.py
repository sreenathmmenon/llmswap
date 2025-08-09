"""Logging handler for llmswap requests and responses."""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


class LLMLogger:
    """Simple logger for LLM requests and responses."""
    
    def __init__(self, log_file: Optional[str] = None, log_level: str = "info"):
        """Initialize logger.
        
        Args:
            log_file: Path to log file. If None, logs to console.
            log_level: Logging level (debug, info, warning, error)
        """
        self.log_file = log_file
        self.log_level = log_level.lower()
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        """Set up Python logger with appropriate handlers."""
        logger = logging.getLogger("llmswap")
        logger.setLevel(getattr(logging, self.log_level.upper()))
        
        # Remove existing handlers to avoid duplicates
        logger.handlers = []
        
        # Create formatter for structured logs
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        if self.log_file:
            # Create log directory if needed
            log_dir = Path(self.log_file).parent
            if log_dir != Path('.'):
                log_dir.mkdir(parents=True, exist_ok=True)
            
            # File handler for persistent logs
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        else:
            # Console handler for development
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    def log_request(self, 
                   provider: str,
                   model: str,
                   prompt: str,
                   **kwargs):
        """Log an LLM request.
        
        Args:
            provider: Provider name (openai, anthropic, etc.)
            model: Model name
            prompt: The prompt sent (only logs length for privacy)
            **kwargs: Additional metadata
        """
        log_data = {
            "type": "request",
            "timestamp": datetime.now().isoformat(),
            "provider": provider,
            "model": model,
            "prompt_length": len(prompt),
            "prompt_tokens": len(prompt.split()),  # Rough estimate
        }
        
        # Add any extra metadata
        if kwargs:
            log_data["metadata"] = kwargs
        
        # Log as JSON for easy parsing
        self.logger.info(json.dumps(log_data))
    
    def log_response(self,
                    provider: str,
                    model: str,
                    response: str,
                    latency: float,
                    **kwargs):
        """Log an LLM response.
        
        Args:
            provider: Provider name
            model: Model name
            response: The response received (only logs length for privacy)
            latency: Response time in seconds
            **kwargs: Additional metadata
        """
        log_data = {
            "type": "response",
            "timestamp": datetime.now().isoformat(),
            "provider": provider,
            "model": model,
            "response_length": len(response),
            "response_tokens": len(response.split()),  # Rough estimate
            "latency_seconds": round(latency, 3),
        }
        
        # Add any extra metadata
        if kwargs:
            log_data["metadata"] = kwargs
        
        self.logger.info(json.dumps(log_data))
    
    def log_error(self,
                 provider: str,
                 error: str,
                 **kwargs):
        """Log an error.
        
        Args:
            provider: Provider where error occurred
            error: Error message
            **kwargs: Additional context
        """
        log_data = {
            "type": "error",
            "timestamp": datetime.now().isoformat(),
            "provider": provider,
            "error": str(error),
        }
        
        if kwargs:
            log_data["metadata"] = kwargs
        
        self.logger.error(json.dumps(log_data))
    
    def log_stream_start(self, provider: str, model: str):
        """Log the start of a streaming response."""
        log_data = {
            "type": "stream_start",
            "timestamp": datetime.now().isoformat(),
            "provider": provider,
            "model": model,
        }
        self.logger.info(json.dumps(log_data))
    
    def log_stream_end(self, provider: str, model: str, total_chunks: int, latency: float):
        """Log the end of a streaming response."""
        log_data = {
            "type": "stream_end",
            "timestamp": datetime.now().isoformat(),
            "provider": provider,
            "model": model,
            "total_chunks": total_chunks,
            "latency_seconds": round(latency, 3),
        }
        self.logger.info(json.dumps(log_data))