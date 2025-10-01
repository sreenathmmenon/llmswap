from pathlib import Path
from typing import Optional
from .registry import WorkspaceRegistry


class WorkspaceDetector:
    
    @staticmethod
    def detect(start_path: Path = None) -> Optional[Path]:
        if start_path is None:
            start_path = Path.cwd()
        
        current = start_path.resolve()
        home = Path.home()
        registry = WorkspaceRegistry()
        
        while current != current.parent:
            workspace_info = registry.get_workspace_by_path(str(current))
            
            if workspace_info:
                workspace_id = workspace_info["workspace_id"]
                workspace_dir = home / ".llmswap" / "workspaces" / workspace_id
                
                if workspace_dir.exists():
                    registry.update_last_accessed(str(current))
                    return workspace_dir
            
            if current == home:
                break
            
            current = current.parent
        
        return None