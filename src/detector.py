"""
Project detection system for Clyde.
Analyzes existing codebases to suggest appropriate configuration.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum


class ProjectType(Enum):
    """Supported project types."""
    PYTHON_GENERAL = "python"
    PYTHON_CLI = "python-cli"
    PYTHON_FASTAPI = "python-fastapi"
    PYTHON_DJANGO = "python-django"
    PYTHON_FLASK = "python-flask"
    JAVASCRIPT_GENERAL = "javascript"
    JAVASCRIPT_REACT = "javascript-react"
    JAVASCRIPT_NEXTJS = "javascript-nextjs"
    JAVASCRIPT_NODE = "javascript-node"
    TYPESCRIPT_GENERAL = "typescript"
    TYPESCRIPT_REACT = "typescript-react"
    TYPESCRIPT_NEXTJS = "typescript-nextjs"
    UNKNOWN = "unknown"


@dataclass
class ProjectSignature:
    """Defines how to detect a specific project type."""
    project_type: ProjectType
    name: str
    description: str
    required_files: List[str] = None  # Must have ALL of these
    optional_files: List[str] = None  # Extra points for having these
    required_content: Dict[str, List[str]] = None  # File must contain these strings
    package_indicators: Dict[str, List[str]] = None  # Dependencies that indicate this type
    directory_structure: List[str] = None  # Expected directories
    confidence_threshold: float = 0.7  # Minimum confidence to suggest this type
    
    def __post_init__(self):
        if self.required_files is None:
            self.required_files = []
        if self.optional_files is None:
            self.optional_files = []
        if self.required_content is None:
            self.required_content = {}
        if self.package_indicators is None:
            self.package_indicators = {}
        if self.directory_structure is None:
            self.directory_structure = []


@dataclass
class DetectionResult:
    """Result of project detection analysis."""
    project_type: ProjectType
    confidence: float
    evidence: List[str]
    suggested_modules: List[str]
    suggested_mcps: List[str]
    language: Optional[str] = None
    framework: Optional[str] = None
    database: Optional[str] = None


class ProjectDetector:
    """Detects project type and suggests appropriate Clyde configuration."""
    
    def __init__(self):
        self.signatures = self._load_project_signatures()
    
    def _load_project_signatures(self) -> List[ProjectSignature]:
        """Define project detection signatures."""
        return [
            # Python FastAPI
            ProjectSignature(
                project_type=ProjectType.PYTHON_FASTAPI,
                name="FastAPI Application",
                description="Python FastAPI web framework",
                required_files=["requirements.txt", "main.py"],
                optional_files=["pyproject.toml", "Dockerfile", "app/__init__.py"],
                required_content={
                    "main.py": ["from fastapi", "FastAPI"],
                    "requirements.txt": ["fastapi"]
                },
                package_indicators={
                    "requirements.txt": ["fastapi", "uvicorn", "pydantic"],
                    "pyproject.toml": ["fastapi", "uvicorn"]
                },
                directory_structure=["app/", "tests/"],
                confidence_threshold=0.8
            ),
            
            # Python Django
            ProjectSignature(
                project_type=ProjectType.PYTHON_DJANGO,
                name="Django Application",
                description="Python Django web framework",
                required_files=["manage.py", "requirements.txt"],
                optional_files=["settings.py", "urls.py", "wsgi.py"],
                required_content={
                    "manage.py": ["django"],
                    "requirements.txt": ["Django"]
                },
                package_indicators={
                    "requirements.txt": ["Django", "djangorestframework"],
                    "pyproject.toml": ["Django"]
                },
                directory_structure=["static/", "templates/", "media/"],
                confidence_threshold=0.8
            ),
            
            # Python Flask
            ProjectSignature(
                project_type=ProjectType.PYTHON_FLASK,
                name="Flask Application",
                description="Python Flask web framework",
                required_files=["app.py", "requirements.txt"],
                optional_files=["wsgi.py", "config.py"],
                required_content={
                    "app.py": ["from flask", "Flask"],
                    "requirements.txt": ["Flask"]
                },
                package_indicators={
                    "requirements.txt": ["Flask", "flask-sqlalchemy", "flask-migrate"],
                    "pyproject.toml": ["Flask"]
                },
                directory_structure=["templates/", "static/"],
                confidence_threshold=0.8
            ),
            
            # Next.js
            ProjectSignature(
                project_type=ProjectType.TYPESCRIPT_NEXTJS,
                name="Next.js Application",
                description="React-based Next.js framework",
                required_files=["package.json", "next.config.js"],
                optional_files=["next.config.ts", "tsconfig.json", "tailwind.config.js"],
                package_indicators={
                    "package.json": ["next", "react", "react-dom"]
                },
                directory_structure=["pages/", "app/", "components/", "public/"],
                confidence_threshold=0.8
            ),
            
            # React (TypeScript)
            ProjectSignature(
                project_type=ProjectType.TYPESCRIPT_REACT,
                name="React Application (TypeScript)",
                description="React application with TypeScript",
                required_files=["package.json", "tsconfig.json"],
                optional_files=["vite.config.ts", "webpack.config.js", "craco.config.js"],
                required_content={
                    "tsconfig.json": ["typescript", "jsx"]
                },
                package_indicators={
                    "package.json": ["react", "react-dom", "typescript", "@types/react"]
                },
                directory_structure=["src/", "public/", "components/"],
                confidence_threshold=0.7
            ),
            
            # React (JavaScript)
            ProjectSignature(
                project_type=ProjectType.JAVASCRIPT_REACT,
                name="React Application (JavaScript)",
                description="React application with JavaScript",
                required_files=["package.json"],
                optional_files=["vite.config.js", "webpack.config.js"],
                package_indicators={
                    "package.json": ["react", "react-dom"]
                },
                directory_structure=["src/", "public/", "components/"],
                confidence_threshold=0.6
            ),
            
            # Node.js
            ProjectSignature(
                project_type=ProjectType.JAVASCRIPT_NODE,
                name="Node.js Application",
                description="Node.js backend application",
                required_files=["package.json"],
                optional_files=["server.js", "index.js", "app.js"],
                package_indicators={
                    "package.json": ["express", "koa", "hapi", "fastify"]
                },
                directory_structure=["routes/", "middleware/", "controllers/"],
                confidence_threshold=0.6
            ),
            
            # Python CLI Tool
            ProjectSignature(
                project_type=ProjectType.PYTHON_CLI,
                name="Python CLI Tool",
                description="Python command-line interface tool",
                required_files=["setup.py"],
                optional_files=["requirements.txt", "pyproject.toml", "README.md", "MANIFEST.in"],
                required_content={
                    "setup.py": ["entry_points"]
                },
                package_indicators={
                    "setup.py": ["click"],
                    "requirements.txt": ["click", "argparse"]
                },
                directory_structure=["src/", "tests/"],
                confidence_threshold=0.58
            ),
            
            # Generic Python
            ProjectSignature(
                project_type=ProjectType.PYTHON_GENERAL,
                name="Python Project",
                description="General Python project",
                required_files=[],  # No required files - any of the optional ones will work
                optional_files=["requirements.txt", "pyproject.toml", "setup.py", "Pipfile", "poetry.lock"],
                required_content={
                    "setup.py": ["setuptools", "from setuptools"],
                    "pyproject.toml": ["[build-system]", "[project]"]
                },
                package_indicators={
                    "setup.py": ["install_requires", "setuptools"],
                    "requirements.txt": [],  # Any line with a package
                    "pyproject.toml": []
                },
                directory_structure=["src/", "tests/", "docs/"],
                confidence_threshold=0.3  # Lower threshold since this is a catch-all
            ),
            
            # Generic TypeScript
            ProjectSignature(
                project_type=ProjectType.TYPESCRIPT_GENERAL,
                name="TypeScript Project",
                description="General TypeScript project",
                required_files=["package.json", "tsconfig.json"],
                optional_files=["webpack.config.ts", "vite.config.ts"],
                confidence_threshold=0.5
            ),
            
            # Generic JavaScript
            ProjectSignature(
                project_type=ProjectType.JAVASCRIPT_GENERAL,
                name="JavaScript Project",
                description="General JavaScript project",
                required_files=["package.json"],
                confidence_threshold=0.3
            ),
        ]
    
    def detect_project(self, project_path: Path) -> List[DetectionResult]:
        """Detect project type and return sorted results by confidence."""
        results = []
        
        for signature in self.signatures:
            confidence, evidence = self._calculate_confidence(project_path, signature)
            
            if confidence >= signature.confidence_threshold:
                result = DetectionResult(
                    project_type=signature.project_type,
                    confidence=confidence,
                    evidence=evidence,
                    suggested_modules=self._suggest_modules(signature.project_type),
                    suggested_mcps=self._suggest_mcps(signature.project_type),
                    language=self._extract_language(signature.project_type),
                    framework=self._extract_framework(signature.project_type),
                    database=self._detect_database(project_path)
                )
                results.append(result)
        
        # Sort by confidence, highest first
        results.sort(key=lambda x: x.confidence, reverse=True)
        return results
    
    def _calculate_confidence(self, project_path: Path, signature: ProjectSignature) -> Tuple[float, List[str]]:
        """Calculate confidence score for a project signature."""
        score = 0.0
        max_score = 0.0
        evidence = []
        
        # Check required files (high weight)
        required_weight = 3.0
        max_score += len(signature.required_files) * required_weight
        
        for file_path in signature.required_files:
            if (project_path / file_path).exists():
                score += required_weight
                evidence.append(f"✓ Required file: {file_path}")
            else:
                evidence.append(f"✗ Missing required file: {file_path}")
        
        # Check optional files (medium weight)
        optional_weight = 1.0
        max_score += len(signature.optional_files) * optional_weight
        
        for file_path in signature.optional_files:
            if (project_path / file_path).exists():
                score += optional_weight
                evidence.append(f"✓ Optional file: {file_path}")
        
        # Check required content (high weight)
        content_weight = 2.0
        for file_path, required_strings in signature.required_content.items():
            max_score += len(required_strings) * content_weight
            file_full_path = project_path / file_path
            
            if file_full_path.exists():
                try:
                    content = file_full_path.read_text(encoding='utf-8', errors='ignore')
                    for required_string in required_strings:
                        if required_string.lower() in content.lower():
                            score += content_weight
                            evidence.append(f"✓ Found '{required_string}' in {file_path}")
                        else:
                            evidence.append(f"✗ Missing '{required_string}' in {file_path}")
                except Exception:
                    evidence.append(f"✗ Could not read {file_path}")
        
        # Check package indicators (medium weight)
        package_weight = 1.5
        for file_path, packages in signature.package_indicators.items():
            max_score += len(packages) * package_weight
            file_full_path = project_path / file_path
            
            if file_full_path.exists():
                dependencies = self._extract_dependencies(file_full_path)
                for package in packages:
                    if package.lower() in [dep.lower() for dep in dependencies]:
                        score += package_weight
                        evidence.append(f"✓ Found dependency: {package}")
                    else:
                        evidence.append(f"✗ Missing dependency: {package}")
        
        # Check directory structure (low weight)
        directory_weight = 0.5
        max_score += len(signature.directory_structure) * directory_weight
        
        for directory in signature.directory_structure:
            if (project_path / directory).is_dir():
                score += directory_weight
                evidence.append(f"✓ Found directory: {directory}")
        
        # Calculate final confidence (0-1 scale)
        confidence = score / max_score if max_score > 0 else 0.0
        return min(confidence, 1.0), evidence
    
    def _extract_dependencies(self, file_path: Path) -> List[str]:
        """Extract dependency names from package files."""
        dependencies = []
        
        try:
            if file_path.name == "package.json":
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    deps = data.get('dependencies', {})
                    dev_deps = data.get('devDependencies', {})
                    dependencies.extend(deps.keys())
                    dependencies.extend(dev_deps.keys())
            
            elif file_path.name == "requirements.txt":
                with open(file_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Extract package name (before ==, >=, etc.)
                            package = line.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0].strip()
                            dependencies.append(package)
            
            elif file_path.name == "setup.py":
                # Extract dependencies from setup.py
                with open(file_path, 'r') as f:
                    content = f.read()
                    # Look for install_requires
                    if 'install_requires' in content:
                        # Simple extraction - look for list after install_requires
                        import re
                        pattern = r'install_requires\s*=\s*\[(.*?)\]'
                        match = re.search(pattern, content, re.DOTALL)
                        if match:
                            deps_str = match.group(1)
                            # Extract quoted strings, being more careful about the content
                            dep_pattern = r'["\']([^"\']+?)["\']'
                            found_deps = re.findall(dep_pattern, deps_str)
                            # Clean up each dependency (remove version specifiers)
                            for dep in found_deps:
                                clean_dep = dep.split('>=')[0].split('==')[0].split('<=')[0].split('~=')[0].split('>')[0].split('<')[0].strip()
                                if clean_dep:
                                    dependencies.append(clean_dep)
            
            elif file_path.name == "pyproject.toml":
                # Basic TOML parsing for dependencies
                with open(file_path, 'r') as f:
                    content = f.read()
                    # Look for [tool.poetry.dependencies] or similar
                    if 'dependencies' in content:
                        # This is a simplified approach - would need proper TOML parsing for production
                        lines = content.split('\n')
                        in_deps = False
                        for line in lines:
                            if '[' in line and 'dependencies' in line:
                                in_deps = True
                                continue
                            if in_deps and line.startswith('['):
                                in_deps = False
                            if in_deps and '=' in line:
                                dep = line.split('=')[0].strip().strip('"')
                                if dep:
                                    dependencies.append(dep)
        
        except Exception:
            pass  # Ignore parsing errors
        
        return dependencies
    
    def _suggest_modules(self, project_type: ProjectType) -> List[str]:
        """Suggest Clyde modules based on project type."""
        base_modules = [
            "core.development-standards",
            "core.code-quality",
            "core.systematic-thinking"
        ]
        
        type_specific = {
            ProjectType.PYTHON_FASTAPI: [
                "python.general",
                "frameworks.fastapi",
                "core.modular-architecture",
                "core.error-handling"
            ],
            ProjectType.PYTHON_DJANGO: [
                "python.general",
                "frameworks.django",
                "core.modular-architecture"
            ],
            ProjectType.PYTHON_FLASK: [
                "python.general",
                "frameworks.flask",
                "core.error-handling"
            ],
            ProjectType.TYPESCRIPT_NEXTJS: [
                "javascript.general",
                "frameworks.nextjs",
                "frameworks.react",
                "core.modular-architecture"
            ],
            ProjectType.TYPESCRIPT_REACT: [
                "javascript.general",
                "frameworks.react",
                "core.modular-architecture"
            ],
            ProjectType.JAVASCRIPT_REACT: [
                "javascript.general",
                "frameworks.react"
            ],
            ProjectType.JAVASCRIPT_NODE: [
                "javascript.general",
                "core.error-handling"
            ],
            ProjectType.PYTHON_CLI: [
                "python.general",
                "core.modular-architecture",
                "core.error-handling"
            ],
            ProjectType.PYTHON_GENERAL: [
                "python.general"
            ],
            ProjectType.TYPESCRIPT_GENERAL: [
                "javascript.general"
            ],
            ProjectType.JAVASCRIPT_GENERAL: [
                "javascript.general"
            ]
        }
        
        modules = base_modules.copy()
        modules.extend(type_specific.get(project_type, []))
        return modules
    
    def _suggest_mcps(self, project_type: ProjectType) -> List[str]:
        """Suggest MCP servers based on project type."""
        base_mcps = [
            "sequential-thinking",
            "context7"
        ]
        
        type_specific = {
            ProjectType.PYTHON_FASTAPI: [
                "taskmaster"
            ],
            ProjectType.PYTHON_DJANGO: [
                "taskmaster"
            ],
            ProjectType.TYPESCRIPT_NEXTJS: [
                "playwright",
                "taskmaster"
            ],
            ProjectType.TYPESCRIPT_REACT: [
                "playwright"
            ],
            ProjectType.JAVASCRIPT_REACT: [
                "playwright"
            ]
        }
        
        mcps = base_mcps.copy()
        mcps.extend(type_specific.get(project_type, []))
        return mcps
    
    def _extract_language(self, project_type: ProjectType) -> Optional[str]:
        """Extract primary language from project type."""
        if project_type.value.startswith('python'):
            return 'python'
        elif project_type.value.startswith('typescript'):
            return 'typescript'
        elif project_type.value.startswith('javascript'):
            return 'javascript'
        return None
    
    def _extract_framework(self, project_type: ProjectType) -> Optional[str]:
        """Extract framework from project type."""
        framework_map = {
            ProjectType.PYTHON_FASTAPI: 'fastapi',
            ProjectType.PYTHON_DJANGO: 'django',
            ProjectType.PYTHON_FLASK: 'flask',
            ProjectType.TYPESCRIPT_NEXTJS: 'nextjs',
            ProjectType.JAVASCRIPT_NEXTJS: 'nextjs',
            ProjectType.TYPESCRIPT_REACT: 'react',
            ProjectType.JAVASCRIPT_REACT: 'react',
        }
        return framework_map.get(project_type)
    
    def _detect_database(self, project_path: Path) -> Optional[str]:
        """Detect database technology from project files."""
        database_indicators = {
            'postgres': ['psycopg2', 'pg', 'postgresql', 'postgres'],
            'mongodb': ['pymongo', 'mongodb', 'mongoose'],
            'sqlite': ['sqlite3', 'sqlite'],
            'mysql': ['mysql', 'pymysql', 'mysqlclient'],
            'redis': ['redis', 'redis-py']
        }
        
        # Check package files
        for package_file in ['requirements.txt', 'package.json', 'pyproject.toml']:
            file_path = project_path / package_file
            if file_path.exists():
                dependencies = self._extract_dependencies(file_path)
                for db, indicators in database_indicators.items():
                    if any(indicator in dep.lower() for dep in dependencies for indicator in indicators):
                        return db
        
        # Check for database config files
        db_files = {
            'postgres': ['postgresql.conf', 'pg_hba.conf'],
            'mongodb': ['mongod.conf', 'mongo.conf'],
            'mysql': ['my.cnf', 'mysql.conf'],
            'redis': ['redis.conf']
        }
        
        for db, files in db_files.items():
            if any((project_path / file).exists() for file in files):
                return db
        
        return None

    def get_best_match(self, project_path: Path) -> Optional[DetectionResult]:
        """Get the best matching project type."""
        results = self.detect_project(project_path)
        return results[0] if results else None