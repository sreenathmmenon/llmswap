from pathlib import Path
from typing import Optional, Dict, Any
from .mentor import EklavyaMentor


class WorkspaceAwareMentor(EklavyaMentor):
    
    def __init__(self, 
                 persona: str = 'guru',
                 alias: Optional[str] = None,
                 learner_name: Optional[str] = None,
                 workspace_dir: Optional[Path] = None):
        super().__init__(persona, alias, learner_name)
        
        self.workspace_dir = workspace_dir
        self.workspace_manager = None
        
        if workspace_dir:
            from llmswap.workspace.manager import WorkspaceManager
            project_path = workspace_dir.parent.parent.parent
            
            workspace_id = workspace_dir.name
            workspaces_dir = workspace_dir.parent
            
            from llmswap.workspace.registry import WorkspaceRegistry
            registry = WorkspaceRegistry()
            all_workspaces = registry.list_workspaces()
            
            for ws in all_workspaces:
                if ws["workspace_id"] == workspace_id:
                    project_path = Path(ws["project_path"])
                    break
            
            self.workspace_manager = WorkspaceManager(project_path)
    
    def generate_system_prompt(self) -> str:
        base_prompt = super().generate_system_prompt()
        
        if not self.workspace_manager:
            return base_prompt
        
        try:
            workspace_data = self.workspace_manager.load_workspace()
            context = self.workspace_manager.load_context()
            learnings = self.workspace_manager.load_learnings(limit=5)
            decisions = self.workspace_manager.load_decisions(limit=3)
            
            enhanced_prompt = base_prompt + "\n\n"
            
            if workspace_data.get("project_name"):
                enhanced_prompt += f"\n**Project Context:**\n"
                enhanced_prompt += f"You are teaching in the context of the project: {workspace_data['project_name']}\n"
                
                if workspace_data.get("description"):
                    enhanced_prompt += f"Project Description: {workspace_data['description']}\n"
                
                if workspace_data.get("tags"):
                    enhanced_prompt += f"Tech Stack: {', '.join(workspace_data['tags'])}\n"
            
            if learnings and "Session:" in learnings:
                enhanced_prompt += f"\n**Previous Learnings (Recent):**\n"
                enhanced_prompt += "The student has previously learned:\n"
                enhanced_prompt += learnings
                enhanced_prompt += "\nBuild on these learnings when teaching new concepts.\n"
            
            if decisions and "##" in decisions:
                enhanced_prompt += f"\n**Architecture Decisions Made:**\n"
                enhanced_prompt += decisions
                enhanced_prompt += "\nConsider these decisions when providing guidance.\n"
            
            if context and len(context) > 50:
                enhanced_prompt += f"\n**Additional Project Context:**\n"
                enhanced_prompt += context + "\n"
            
            return enhanced_prompt
            
        except Exception:
            return base_prompt
    
    def get_workspace_summary(self) -> Dict[str, Any]:
        if not self.workspace_manager:
            return {}
        
        try:
            data = self.workspace_manager.load_workspace()
            return {
                "project_name": data.get("project_name", "Unknown"),
                "learnings_count": data.get("statistics", {}).get("learnings_count", 0),
                "decisions_count": data.get("statistics", {}).get("decisions_count", 0),
                "total_queries": data.get("statistics", {}).get("total_queries", 0)
            }
        except Exception:
            return {}