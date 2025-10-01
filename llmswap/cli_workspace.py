import click
from pathlib import Path
from tabulate import tabulate


@click.group()
def workspace():
    pass


@workspace.command()
@click.option('--name', '-n', help='Project name (defaults to directory name)')
def init(name):
    from llmswap.workspace.manager import WorkspaceManager
    
    project_path = Path.cwd()
    manager = WorkspaceManager(project_path)
    
    try:
        workspace_data = manager.init_workspace(project_name=name)
        
        click.echo(f"✅ Workspace initialized: {workspace_data['project_name']}")
        click.echo(f"📁 Workspace ID: {workspace_data['workspace_id']}")
        click.echo(f"💾 Location: ~/.llmswap/workspaces/{workspace_data['workspace_id']}/")
        click.echo(f"\nCreated files:")
        click.echo(f"  - workspace.json (metadata)")
        click.echo(f"  - context.md (project description)")
        click.echo(f"  - learnings.md (learning journal)")
        click.echo(f"  - decisions.md (architecture decisions)")
        click.echo(f"\n💡 Tip: Edit context.md to add project-specific information:")
        click.echo(f"   llmswap workspace context")
        
    except FileExistsError:
        click.echo("❌ Workspace already exists for this project")
        click.echo(f"   Workspace ID: {manager.workspace_id}")
        return 1


@workspace.command()
def info():
    from llmswap.workspace.detector import WorkspaceDetector
    from llmswap.workspace.manager import WorkspaceManager
    from llmswap.workspace.registry import WorkspaceRegistry
    
    workspace_dir = WorkspaceDetector.detect()
    
    if not workspace_dir:
        click.echo("❌ No workspace found in current directory or parents")
        click.echo("   Run 'llmswap workspace init' to create one")
        return 1
    
    workspace_id = workspace_dir.name
    registry = WorkspaceRegistry()
    all_workspaces = registry.list_workspaces()
    
    project_path = None
    for ws in all_workspaces:
        if ws["workspace_id"] == workspace_id:
            project_path = Path(ws["project_path"])
            break
    
    if not project_path:
        click.echo("❌ Workspace found but not in registry")
        return 1
    
    manager = WorkspaceManager(project_path)
    
    try:
        data = manager.load_workspace()
        
        click.echo(f"📊 Workspace: {data['project_name']}")
        click.echo(f"📁 Project Path: {project_path}")
        click.echo(f"💾 Workspace Location: ~/.llmswap/workspaces/{workspace_id}/")
        click.echo(f"🆔 Workspace ID: {data['workspace_id']}")
        click.echo(f"\n📈 Statistics:")
        click.echo(f"  Total queries: {data['statistics']['total_queries']}")
        click.echo(f"  Learnings tracked: {data['statistics']['learnings_count']}")
        click.echo(f"  Decisions recorded: {data['statistics']['decisions_count']}")
        click.echo(f"\n⚙️  Settings:")
        click.echo(f"  Default mentor: {data.get('default_mentor', 'guru')}")
        if data.get('mentor_alias'):
            click.echo(f"  Mentor alias: {data['mentor_alias']}")
        if data.get('tags'):
            click.echo(f"  Tags: {', '.join(data['tags'])}")
        
    except Exception as e:
        click.echo(f"❌ Error loading workspace: {e}")
        return 1


@workspace.command(name='list')
def list_workspaces():
    from llmswap.workspace.registry import WorkspaceRegistry
    
    registry = WorkspaceRegistry()
    workspaces = registry.list_workspaces()
    
    if not workspaces:
        click.echo("No workspaces found.")
        click.echo("Run 'llmswap workspace init' in a project directory to create one.")
        return
    
    table_data = []
    for ws in workspaces:
        table_data.append([
            ws['project_name'],
            ws['project_path'],
            ws['last_accessed'][:10]
        ])
    
    headers = ["Project", "Path", "Last Used"]
    click.echo(tabulate(table_data, headers=headers, tablefmt="grid"))


@workspace.command()
def journal():
    from llmswap.workspace.detector import WorkspaceDetector
    
    workspace_dir = WorkspaceDetector.detect()
    
    if not workspace_dir:
        click.echo("❌ No workspace found")
        return 1
    
    learnings_file = workspace_dir / "learnings.md"
    
    if not learnings_file.exists():
        click.echo("No learnings recorded yet.")
        return
    
    content = learnings_file.read_text()
    click.echo(content)


@workspace.command()
def decisions():
    from llmswap.workspace.detector import WorkspaceDetector
    
    workspace_dir = WorkspaceDetector.detect()
    
    if not workspace_dir:
        click.echo("❌ No workspace found")
        return 1
    
    decisions_file = workspace_dir / "decisions.md"
    
    if not decisions_file.exists():
        click.echo("No decisions recorded yet.")
        return
    
    content = decisions_file.read_text()
    click.echo(content)


@workspace.command()
def context():
    from llmswap.workspace.detector import WorkspaceDetector
    
    workspace_dir = WorkspaceDetector.detect()
    
    if not workspace_dir:
        click.echo("❌ No workspace found")
        return 1
    
    context_file = workspace_dir / "context.md"
    
    click.edit(filename=str(context_file))