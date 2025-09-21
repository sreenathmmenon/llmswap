"""
Prompt Template Management System

Allows users to create, save, and reuse custom prompt templates for common tasks.
Includes both user-created templates and a curated library of useful prompts.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime


class PromptTemplate:
    """Represents a single prompt template"""
    
    def __init__(self, name: str, template: str, description: str = "",
                 category: str = "general", variables: List[str] = None,
                 author: str = "user"):
        self.name = name
        self.template = template
        self.description = description
        self.category = category
        self.variables = variables or []
        self.author = author
        self.created_at = datetime.now().isoformat()
        self.usage_count = 0
        self.last_used = None
    
    def format(self, **kwargs) -> str:
        """Format template with provided variables"""
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            missing_var = str(e).strip("'")
            raise ValueError(f"Missing required variable: {missing_var}")
    
    def get_required_variables(self) -> List[str]:
        """Extract required variables from template"""
        import re
        variables = re.findall(r'\{(\w+)\}', self.template)
        return list(set(variables))
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "name": self.name,
            "template": self.template,
            "description": self.description,
            "category": self.category,
            "variables": self.variables,
            "author": self.author,
            "created_at": self.created_at,
            "usage_count": self.usage_count,
            "last_used": self.last_used
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create template from dictionary"""
        template = cls(
            name=data["name"],
            template=data["template"],
            description=data.get("description", ""),
            category=data.get("category", "general"),
            variables=data.get("variables", []),
            author=data.get("author", "user")
        )
        template.created_at = data.get("created_at", template.created_at)
        template.usage_count = data.get("usage_count", 0)
        template.last_used = data.get("last_used")
        return template


class PromptTemplateManager:
    """Manages user's custom prompt templates"""
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize template manager"""
        self.config_dir = Path(config_dir or os.path.expanduser("~/.llmswap"))
        self.templates_file = self.config_dir / "prompt_templates.json"
        self.config_dir.mkdir(exist_ok=True)
        self._templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, PromptTemplate]:
        """Load templates from disk"""
        if not self.templates_file.exists():
            return {}
        
        try:
            with open(self.templates_file, 'r') as f:
                data = json.load(f)
            
            templates = {}
            for name, template_data in data.items():
                templates[name] = PromptTemplate.from_dict(template_data)
            
            return templates
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_templates(self):
        """Save templates to disk"""
        data = {name: template.to_dict() for name, template in self._templates.items()}
        with open(self.templates_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_template(self, name: str, template: str, description: str = "",
                       category: str = "general") -> bool:
        """Create a new prompt template"""
        if not name or not template:
            return False
        
        prompt_template = PromptTemplate(
            name=name,
            template=template,
            description=description,
            category=category
        )
        
        # Auto-detect variables
        prompt_template.variables = prompt_template.get_required_variables()
        
        self._templates[name.lower()] = prompt_template
        self._save_templates()
        return True
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get template by name"""
        template = self._templates.get(name.lower())
        if template:
            # Update usage tracking
            template.usage_count += 1
            template.last_used = datetime.now().isoformat()
            self._save_templates()
        return template
    
    def list_templates(self, category: Optional[str] = None) -> List[PromptTemplate]:
        """List templates, optionally filtered by category"""
        templates = list(self._templates.values())
        if category:
            templates = [t for t in templates if t.category == category]
        return sorted(templates, key=lambda x: x.usage_count, reverse=True)
    
    def get_categories(self) -> List[str]:
        """Get all template categories"""
        categories = set(t.category for t in self._templates.values())
        return sorted(list(categories))
    
    def update_template(self, name: str, **updates) -> bool:
        """Update an existing template"""
        template = self._templates.get(name.lower())
        if not template:
            return False
        
        allowed_updates = ["template", "description", "category"]
        for key, value in updates.items():
            if key in allowed_updates:
                setattr(template, key, value)
        
        # Re-detect variables if template changed
        if "template" in updates:
            template.variables = template.get_required_variables()
        
        self._save_templates()
        return True
    
    def delete_template(self, name: str) -> bool:
        """Delete a template"""
        if name.lower() in self._templates:
            del self._templates[name.lower()]
            self._save_templates()
            return True
        return False
    
    def search_templates(self, query: str) -> List[PromptTemplate]:
        """Search templates by name, description, or content"""
        query = query.lower()
        results = []
        
        for template in self._templates.values():
            if (query in template.name.lower() or
                query in template.description.lower() or
                query in template.template.lower() or
                query in template.category.lower()):
                results.append(template)
        
        return results
    
    def get_popular_templates(self, limit: int = 10) -> List[PromptTemplate]:
        """Get most used templates"""
        sorted_templates = sorted(
            self._templates.values(),
            key=lambda x: x.usage_count,
            reverse=True
        )
        return sorted_templates[:limit]
    
    def export_templates(self, file_path: str, category: Optional[str] = None) -> bool:
        """Export templates to file"""
        try:
            templates_to_export = self.list_templates(category)
            export_data = {
                "version": "1.0",
                "exported_at": datetime.now().isoformat(),
                "category_filter": category,
                "templates": {t.name: t.to_dict() for t in templates_to_export}
            }
            
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            return True
        except Exception:
            return False
    
    def import_templates(self, file_path: str, overwrite: bool = False) -> int:
        """Import templates from file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            imported_count = 0
            templates_to_import = data.get("templates", {})
            
            for name, template_data in templates_to_import.items():
                if overwrite or name.lower() not in self._templates:
                    self._templates[name.lower()] = PromptTemplate.from_dict(template_data)
                    imported_count += 1
            
            if imported_count > 0:
                self._save_templates()
                
            return imported_count
        except Exception:
            return 0


class TemplateLibrary:
    """Curated library of useful prompt templates"""
    
    BUILT_IN_TEMPLATES = {
        "code_review": {
            "name": "Code Review",
            "template": "Please review this {language} code for:\n\n1. **Code Quality**: Best practices, readability, maintainability\n2. **Security**: Potential vulnerabilities or security issues\n3. **Performance**: Optimization opportunities\n4. **Bugs**: Logic errors or potential runtime issues\n\nCode to review:\n```{language}\n{code}\n```\n\nProvide specific feedback with examples and suggestions for improvement.",
            "description": "Comprehensive code review focusing on quality, security, and performance",
            "category": "development",
            "variables": ["language", "code"],
            "author": "llmswap"
        },
        
        "explain_like_child": {
            "name": "Explain Like a Child",
            "template": "Explain {topic} in a way that a {age}-year-old would understand. Use:\n\n- Simple words and short sentences\n- Fun analogies and examples from everyday life\n- Maybe a short story or characters\n- Visual descriptions when helpful\n\nMake it engaging and easy to remember!",
            "description": "Child-friendly explanations with analogies and stories",
            "category": "education",
            "variables": ["topic", "age"],
            "author": "llmswap"
        },
        
        "business_analysis": {
            "name": "Business Analysis",
            "template": "Analyze {topic} from a business perspective:\n\n**Market Impact**: How does this affect the market?\n**Revenue Opportunities**: Potential ways to monetize or save money\n**Risk Assessment**: What are the potential risks and mitigation strategies?\n**Implementation**: Practical steps for a {business_type} business\n**ROI Considerations**: Expected timeline and return on investment\n\nFocus on actionable insights and real-world applications.",
            "description": "Business-focused analysis with ROI and practical considerations",
            "category": "business",
            "variables": ["topic", "business_type"],
            "author": "llmswap"
        },
        
        "debug_assistant": {
            "name": "Debug Assistant",
            "template": "Help me debug this {language} error:\n\n**Error Message**: {error}\n\n**Code Context** (if available):\n```{language}\n{code}\n```\n\n**What I was trying to do**: {goal}\n\nPlease provide:\n1. **Root Cause**: What's causing this error?\n2. **Solution**: Step-by-step fix\n3. **Prevention**: How to avoid this in the future\n4. **Alternative Approaches**: Better ways to achieve the goal",
            "description": "Systematic debugging help with solutions and prevention tips",
            "category": "development",
            "variables": ["language", "error", "code", "goal"],
            "author": "llmswap"
        },
        
        "learning_path": {
            "name": "Learning Path Creator",
            "template": "Create a learning path for {topic} at {level} level:\n\n**Background**: I am a {background} looking to {goal}\n**Time Available**: {time_commitment}\n**Preferred Learning Style**: {learning_style}\n\n**Please provide**:\n1. **Prerequisites**: What I should know first\n2. **Learning Phases**: Break down into manageable chunks\n3. **Resources**: Books, courses, tutorials, projects\n4. **Milestones**: How to measure progress\n5. **Timeline**: Realistic schedule\n6. **Practice Projects**: Hands-on applications\n\nMake it practical and achievable!",
            "description": "Personalized learning path with resources and milestones",
            "category": "education",
            "variables": ["topic", "level", "background", "goal", "time_commitment", "learning_style"],
            "author": "llmswap"
        }
    }
    
    @classmethod
    def get_template(cls, name: str) -> Optional[PromptTemplate]:
        """Get a built-in template"""
        template_data = cls.BUILT_IN_TEMPLATES.get(name)
        if template_data:
            return PromptTemplate.from_dict(template_data)
        return None
    
    @classmethod
    def list_templates(cls) -> List[PromptTemplate]:
        """List all built-in templates"""
        return [
            PromptTemplate.from_dict(data) 
            for data in cls.BUILT_IN_TEMPLATES.values()
        ]
    
    @classmethod
    def get_categories(cls) -> List[str]:
        """Get all built-in categories"""
        categories = set(t["category"] for t in cls.BUILT_IN_TEMPLATES.values())
        return sorted(list(categories))
    
    @classmethod
    def search_templates(cls, query: str) -> List[PromptTemplate]:
        """Search built-in templates"""
        query = query.lower()
        results = []
        
        for template_data in cls.BUILT_IN_TEMPLATES.values():
            if (query in template_data["name"].lower() or
                query in template_data["description"].lower() or
                query in template_data["template"].lower() or
                query in template_data["category"].lower()):
                results.append(PromptTemplate.from_dict(template_data))
        
        return results