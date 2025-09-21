"""
AI Alias Management System

Allows users to create and maintain personalized AI assistants with custom names,
personas, and consistent personalities across sessions.
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime


class AliasManager:
    """Manages personalized AI aliases and their associated personas"""
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize alias manager with user-specific storage"""
        self.config_dir = Path(config_dir or os.path.expanduser("~/.llmswap"))
        self.aliases_file = self.config_dir / "aliases.json"
        self.config_dir.mkdir(exist_ok=True)
        self._aliases = self._load_aliases()
    
    def _load_aliases(self) -> Dict[str, Dict]:
        """Load saved aliases from disk"""
        if not self.aliases_file.exists():
            return {}
        
        try:
            with open(self.aliases_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_aliases(self):
        """Save aliases to disk"""
        with open(self.aliases_file, 'w') as f:
            json.dump(self._aliases, f, indent=2)
    
    def create_alias(self, name: str, persona: str, description: str = "", 
                    custom_prompt: str = "") -> bool:
        """
        Create a new personalized AI alias
        
        Args:
            name: Custom name for the AI (e.g., "Sarah", "CodeMentor")
            persona: Base persona type (teacher, developer, etc.)
            description: User description of this alias
            custom_prompt: Additional personality customization
            
        Returns:
            True if created successfully
        """
        if not name or not persona:
            return False
            
        self._aliases[name.lower()] = {
            "display_name": name,
            "persona": persona,
            "description": description,
            "custom_prompt": custom_prompt,
            "created_at": datetime.now().isoformat(),
            "last_used": None,
            "usage_count": 0
        }
        
        self._save_aliases()
        return True
    
    def get_alias(self, name: str) -> Optional[Dict]:
        """Get alias details by name"""
        alias_data = self._aliases.get(name.lower())
        if alias_data:
            # Update usage tracking
            alias_data["last_used"] = datetime.now().isoformat()
            alias_data["usage_count"] += 1
            self._save_aliases()
        return alias_data
    
    def list_aliases(self) -> Dict[str, Dict]:
        """List all user's aliases"""
        return self._aliases.copy()
    
    def update_alias(self, name: str, **updates) -> bool:
        """Update an existing alias"""
        if name.lower() not in self._aliases:
            return False
            
        allowed_updates = ["persona", "description", "custom_prompt", "display_name"]
        for key, value in updates.items():
            if key in allowed_updates:
                self._aliases[name.lower()][key] = value
        
        self._save_aliases()
        return True
    
    def delete_alias(self, name: str) -> bool:
        """Delete an alias"""
        if name.lower() in self._aliases:
            del self._aliases[name.lower()]
            self._save_aliases()
            return True
        return False
    
    def get_favorite_aliases(self, limit: int = 5) -> List[Dict]:
        """Get most frequently used aliases"""
        sorted_aliases = sorted(
            self._aliases.items(),
            key=lambda x: x[1].get("usage_count", 0),
            reverse=True
        )
        
        return [
            {"name": name, **data} 
            for name, data in sorted_aliases[:limit]
        ]
    
    def search_aliases(self, query: str) -> List[Dict]:
        """Search aliases by name or description"""
        query = query.lower()
        results = []
        
        for name, data in self._aliases.items():
            if (query in name.lower() or 
                query in data.get("description", "").lower() or
                query in data.get("persona", "").lower()):
                results.append({"name": name, **data})
        
        return results

    def get_alias_prompt(self, name: str) -> Optional[str]:
        """Get the complete prompt for an alias including persona and customization"""
        alias = self.get_alias(name)
        if not alias:
            return None
            
        # Import here to avoid circular dependency
        from ..eklavya.practical_personas import get_practical_persona_prompt
        
        base_prompt = get_practical_persona_prompt(
            alias["persona"], 
            alias["display_name"]
        )
        
        # Add custom personality if specified
        if alias.get("custom_prompt"):
            base_prompt += f"\n\nAdditional personality: {alias['custom_prompt']}"
            
        return base_prompt

    def export_aliases(self, file_path: str) -> bool:
        """Export aliases to a file for backup/sharing"""
        try:
            export_data = {
                "version": "1.0",
                "exported_at": datetime.now().isoformat(),
                "aliases": self._aliases
            }
            
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            return True
        except Exception:
            return False
    
    def import_aliases(self, file_path: str, overwrite: bool = False) -> int:
        """Import aliases from a file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            imported_count = 0
            aliases_to_import = data.get("aliases", {})
            
            for name, alias_data in aliases_to_import.items():
                if overwrite or name not in self._aliases:
                    self._aliases[name] = alias_data
                    imported_count += 1
            
            if imported_count > 0:
                self._save_aliases()
                
            return imported_count
        except Exception:
            return 0