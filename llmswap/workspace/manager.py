import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from .registry import WorkspaceRegistry
from .templates import CONTEXT_TEMPLATE, LEARNINGS_TEMPLATE, DECISIONS_TEMPLATE


class WorkspaceManager:
    
    def __init__(self, project_path: Path):
        self.project_path = project_path.resolve()
        self.workspace_id = self._generate_workspace_id(self.project_path)
        
        self.workspace_dir = (
            Path.home() / ".llmswap" / "workspaces" / self.workspace_id
        )
        self.workspace_json = self.workspace_dir / "workspace.json"
        self.registry = WorkspaceRegistry()
    
    def _generate_workspace_id(self, project_path: Path) -> str:
        path_str = str(project_path)
        hash_hex = hashlib.md5(path_str.encode()).hexdigest()[:12]
        project_name = project_path.name.lower().replace(" ", "-").replace("_", "-")
        return f"{project_name}-{hash_hex}"
    
    def init_workspace(self, project_name: Optional[str] = None) -> Dict[str, Any]:
        if self.workspace_dir.exists():
            raise FileExistsError(f"Workspace already exists at {self.workspace_dir}")
        
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
        project_name = project_name or self.project_path.name
        now = datetime.now().isoformat()
        
        workspace_data = {
            "workspace_id": self.workspace_id,
            "project_name": project_name,
            "project_path": str(self.project_path),
            "created_at": now,
            "last_accessed": now,
            "default_provider": None,
            "default_mentor": "guru",
            "mentor_alias": None,
            "statistics": {
                "total_queries": 0,
                "total_conversations": 0,
                "learnings_count": 0,
                "decisions_count": 0
            },
            "tags": [],
            "description": ""
        }
        
        with open(self.workspace_json, 'w') as f:
            json.dump(workspace_data, f, indent=2)
        
        self._create_default_files(project_name)
        
        self.registry.add_workspace(workspace_data)
        
        return workspace_data
    
    def _create_default_files(self, project_name: str):
        context_file = self.workspace_dir / "context.md"
        with open(context_file, 'w') as f:
            f.write(CONTEXT_TEMPLATE.format(project_name=project_name))
        
        learnings_file = self.workspace_dir / "learnings.md"
        with open(learnings_file, 'w') as f:
            f.write(LEARNINGS_TEMPLATE.format(project_name=project_name))
        
        decisions_file = self.workspace_dir / "decisions.md"
        with open(decisions_file, 'w') as f:
            f.write(DECISIONS_TEMPLATE.format(project_name=project_name))
        
        conversations_dir = self.workspace_dir / "conversations"
        conversations_dir.mkdir(exist_ok=True)
    
    def load_workspace(self) -> Dict[str, Any]:
        if not self.workspace_json.exists():
            raise FileNotFoundError(f"No workspace found at {self.workspace_dir}")
        
        with open(self.workspace_json, 'r') as f:
            data = json.load(f)
        
        data["last_accessed"] = datetime.now().isoformat()
        self.save_workspace(data)
        
        return data
    
    def save_workspace(self, data: Dict[str, Any]):
        with open(self.workspace_json, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_context(self) -> str:
        context_file = self.workspace_dir / "context.md"
        if context_file.exists():
            return context_file.read_text()
        return ""
    
    def load_learnings(self, limit: Optional[int] = None) -> str:
        learnings_file = self.workspace_dir / "learnings.md"
        if learnings_file.exists():
            content = learnings_file.read_text()
            
            if limit:
                sessions = content.split("### Session:")
                if len(sessions) > limit + 1:
                    recent = sessions[-(limit):]
                    content = "### Session:".join(recent)
            
            return content
        return ""
    
    def load_decisions(self, limit: Optional[int] = None) -> str:
        decisions_file = self.workspace_dir / "decisions.md"
        if decisions_file.exists():
            content = decisions_file.read_text()
            
            if limit:
                decisions = content.split("##")
                if len(decisions) > limit + 1:
                    recent = decisions[-(limit):]
                    content = "##".join(recent)
            
            return content
        return ""
    
    def append_learning(self, query: str, learnings: str):
        learnings_file = self.workspace_dir / "learnings.md"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        entry = f"""
### Session: {timestamp}
**Question:** {query[:200]}{"..." if len(query) > 200 else ""}

**Key Learnings:**
{learnings}

---

"""
        
        with open(learnings_file, 'a') as f:
            f.write(entry)
        
        data = self.load_workspace()
        data["statistics"]["learnings_count"] += 1
        self.save_workspace(data)
    
    def increment_query_count(self):
        data = self.load_workspace()
        data["statistics"]["total_queries"] += 1
        self.save_workspace(data)