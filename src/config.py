"""
Configuration management for Clyde.
Handles loading, saving, and managing project configuration.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from jinja2 import Template


@dataclass
class ClydeConfig:
    """Configuration for a Clyde project."""
    
    project_name: str
    language: str
    project_path: Path
    framework: Optional[str] = None
    database: Optional[str] = None
    project_type: str = "application"
    includes: List[str] = field(default_factory=list)
    custom_modules: List[Dict[str, str]] = field(default_factory=list)
    options: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"
    
    def __post_init__(self):
        """Initialize default configuration after creation."""
        if not self.includes:
            self._set_default_includes()
        
        if not self.options:
            self._set_default_options()
    
    def _set_default_includes(self):
        """Set default module includes based on language and framework."""
        # Core modules (always included)
        self.includes = [
            "core.tdd",
            "core.modularity", 
            "core.dry",
            "core.general"
        ]
        
        # Language-specific modules
        if self.language == "python":
            self.includes.extend([
                "python.general",
                "python.testing"
            ])
        elif self.language in ["javascript", "typescript"]:
            self.includes.extend([
                "javascript.general",
                "javascript.testing"
            ])
        
        # Framework-specific modules
        if self.framework:
            framework_modules = self._get_framework_modules(self.framework)
            self.includes.extend(framework_modules)
        
        # Database modules
        if self.database:
            self.includes.append(self.database)
    
    def _get_framework_modules(self, framework: str) -> List[str]:
        """Get module list for a specific framework."""
        framework_map = {
            "fastapi": ["fastapi.structure", "fastapi.patterns"],
            "react": ["react.structure", "react.patterns"],
            "nextjs": ["nextjs.structure", "nextjs.patterns"],
            "django": ["python.django"],  # If we add Django modules later
        }
        
        return framework_map.get(framework, [])
    
    def _set_default_options(self):
        """Set default configuration options."""
        self.options = {
            "show_module_boundaries": True,
            "include_toc": True,
            "validation_level": "normal"
        }
    
    def add_module(self, module_id: str):
        """Add a module to the includes list."""
        if module_id not in self.includes:
            self.includes.append(module_id)
    
    def remove_module(self, module_id: str):
        """Remove a module from the includes list."""
        if module_id in self.includes:
            self.includes.remove(module_id)
    
    def expand_groups(self, includes: List[str]) -> List[str]:
        """Expand group references like 'core.*' into individual modules."""
        expanded = []
        modules_dir = self.get_modules_dir()
        
        for item in includes:
            if item.endswith('.*'):
                # This is a group reference
                group_prefix = item[:-2]  # Remove '.*'
                group_path = modules_dir / group_prefix
                
                if group_path.exists() and group_path.is_dir():
                    # Find all .md files in this directory
                    for module_file in group_path.glob('*.md'):
                        module_name = module_file.stem
                        module_id = f"{group_prefix}.{module_name}"
                        expanded.append(module_id)
                else:
                    print(f"Warning: Group directory not found: {group_path}")
            else:
                # Regular module reference
                expanded.append(item)
        
        return expanded
    
    def get_modules_dir(self) -> Path:
        """Get the path to the modules directory."""
        # Assume modules are in the same directory as this file
        return Path(__file__).parent.parent / "modules"
    
    def get_module_path(self, module_id: str) -> Path:
        """Get the file path for a specific module."""
        modules_dir = self.get_modules_dir()
        
        # Handle custom modules
        if module_id.startswith("custom."):
            custom_name = module_id.split(".", 1)[1]
            return self.project_path / ".claude" / "custom" / f"{custom_name}.md"
        
        # Handle built-in modules
        module_path = modules_dir / f"{module_id.replace('.', '/')}.md"
        return module_path
    
    def validate_modules(self) -> List[str]:
        """Validate that all included modules exist. Returns list of missing modules."""
        missing = []
        
        # Expand groups first
        expanded_includes = self.expand_groups(self.includes)
        
        for module_id in expanded_includes:
            module_path = self.get_module_path(module_id)
            if not module_path.exists():
                missing.append(module_id)
        
        return missing
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for YAML serialization."""
        return {
            "version": self.version,
            "project": {
                "name": self.project_name,
                "type": self.project_type,
                "language": self.language,
                "framework": self.framework
            },
            "includes": self.includes,
            "custom_modules": self.custom_modules,
            "options": self.options
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], project_path: Path) -> 'ClydeConfig':
        """Create configuration from dictionary."""
        project_info = data.get("project", {})
        
        return cls(
            version=data.get("version", "1.0"),
            project_name=project_info.get("name", "Unknown Project"),
            project_type=project_info.get("type", "application"),
            language=project_info.get("language", "python"),
            framework=project_info.get("framework"),
            database=data.get("database"),  # Legacy support
            includes=data.get("includes", []),
            custom_modules=data.get("custom_modules", []),
            options=data.get("options", {}),
            project_path=project_path
        )
    
    @classmethod
    def from_file(cls, config_file: Path) -> 'ClydeConfig':
        """Load configuration from YAML file."""
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        with open(config_file, 'r') as f:
            data = yaml.safe_load(f)
        
        project_path = config_file.parent.parent  # .claude/config.yaml -> project root
        return cls.from_dict(data, project_path)
    
    def save(self, config_file: Optional[Path] = None):
        """Save configuration to YAML file."""
        if config_file is None:
            config_file = self.project_path / ".claude" / "config.yaml"
        
        # Ensure directory exists
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate YAML content from template
        template_path = Path(__file__).parent.parent / "templates" / "config.yaml.template"
        
        if template_path.exists():
            with open(template_path, 'r') as f:
                template_content = f.read()
            
            template = Template(template_content)
            content = template.render(
                project_name=self.project_name,
                project_type=self.project_type,
                language=self.language,
                framework=self.framework or ""
            )
        else:
            # Fallback to direct YAML serialization
            content = yaml.dump(self.to_dict(), default_flow_style=False, sort_keys=False)
        
        with open(config_file, 'w') as f:
            f.write(content)
    
    def get_config_hash(self) -> str:
        """Generate a hash of the current configuration for change detection."""
        import hashlib
        
        config_str = yaml.dump(self.to_dict(), sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()[:8]


class ModuleResolver:
    """Resolves and loads module content."""
    
    def __init__(self, config: ClydeConfig):
        self.config = config
    
    def resolve_module(self, module_id: str) -> Optional[str]:
        """Resolve a module ID to its file content."""
        module_path = self.config.get_module_path(module_id)
        
        if not module_path.exists():
            return None
        
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Warning: Failed to read module {module_id}: {e}")
            return None
    
    def get_all_module_content(self) -> Dict[str, str]:
        """Get content for all included modules."""
        content = {}
        
        # Expand any group references first
        expanded_includes = self.config.expand_groups(self.config.includes)
        
        for module_id in expanded_includes:
            module_content = self.resolve_module(module_id)
            if module_content:
                content[module_id] = module_content
            else:
                print(f"Warning: Module not found: {module_id}")
        
        return content