import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


class WorkspaceRegistry:
    
    def __init__(self):
        self.registry_file = Path.home() / ".llmswap" / "registry.json"
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.registry_file.exists():
            self._init_registry()
    
    def _init_registry(self):
        data = {
            "workspaces": {},
            "last_updated": datetime.now().isoformat()
        }
        with open(self.registry_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_registry(self) -> Dict[str, Any]:
        with open(self.registry_file, 'r') as f:
            return json.load(f)
    
    def save_registry(self, data: Dict[str, Any]):
        data["last_updated"] = datetime.now().isoformat()
        with open(self.registry_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_workspace(self, workspace_data: Dict[str, Any]):
        registry = self.load_registry()
        
        project_path = str(workspace_data["project_path"])
        workspace_id = workspace_data["workspace_id"]
        
        registry["workspaces"][project_path] = {
            "workspace_id": workspace_id,
            "project_name": workspace_data["project_name"],
            "last_accessed": workspace_data.get("last_accessed", datetime.now().isoformat())
        }
        
        self.save_registry(registry)
    
    def get_workspace_by_path(self, project_path: str) -> Dict[str, Any]:
        registry = self.load_registry()
        return registry["workspaces"].get(str(project_path))
    
    def list_workspaces(self) -> List[Dict[str, Any]]:
        registry = self.load_registry()
        workspaces = []
        
        for path, data in registry["workspaces"].items():
            workspaces.append({
                "project_path": path,
                **data
            })
        
        workspaces.sort(key=lambda x: x.get("last_accessed", ""), reverse=True)
        return workspaces
    
    def remove_workspace(self, project_path: str):
        registry = self.load_registry()
        if str(project_path) in registry["workspaces"]:
            del registry["workspaces"][str(project_path)]
            self.save_registry(registry)
    
    def update_last_accessed(self, project_path: str):
        registry = self.load_registry()
        if str(project_path) in registry["workspaces"]:
            registry["workspaces"][str(project_path)]["last_accessed"] = datetime.now().isoformat()
            self.save_registry(registry)