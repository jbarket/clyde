"""
Tests for Clyde configuration management.
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, mock_open

from clyde.src.config import ClydeConfig, ModuleResolver


class TestClydeConfig:
    """Test the ClydeConfig class."""
    
    def test_init_with_defaults(self):
        """Test configuration initialization with default values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            config = ClydeConfig(
                project_name="test-project",
                language="python",
                project_path=project_path
            )
            
            assert config.project_name == "test-project"
            assert config.language == "python"
            assert config.framework is None
            assert config.project_type == "application"
            assert "core.tdd" in config.includes
            assert "python.general" in config.includes
    
    def test_init_with_framework(self):
        """Test configuration initialization with framework."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            config = ClydeConfig(
                project_name="test-project",
                language="python",
                framework="fastapi",
                project_path=project_path
            )
            
            assert config.framework == "fastapi"
            assert "fastapi.structure" in config.includes
            assert "fastapi.patterns" in config.includes
    
    def test_add_remove_modules(self):
        """Test adding and removing modules."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            config = ClydeConfig(
                project_name="test-project",
                language="python",
                project_path=project_path
            )
            
            initial_count = len(config.includes)
            
            # Add a module
            config.add_module("docker")
            assert "docker" in config.includes
            assert len(config.includes) == initial_count + 1
            
            # Remove a module
            config.remove_module("docker")
            assert "docker" not in config.includes
            assert len(config.includes) == initial_count
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            config = ClydeConfig(
                project_name="test-project",
                language="python",
                framework="fastapi",
                project_path=project_path
            )
            
            config_dict = config.to_dict()
            
            assert config_dict["version"] == "1.0"
            assert config_dict["project"]["name"] == "test-project"
            assert config_dict["project"]["language"] == "python"
            assert config_dict["project"]["framework"] == "fastapi"
            assert isinstance(config_dict["includes"], list)
            assert isinstance(config_dict["options"], dict)
    
    def test_from_dict(self):
        """Test creation from dictionary."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            config_data = {
                "version": "1.0",
                "project": {
                    "name": "test-project",
                    "language": "python",
                    "framework": "fastapi"
                },
                "includes": ["core.tdd", "python.general"],
                "options": {"show_module_boundaries": True}
            }
            
            config = ClydeConfig.from_dict(config_data, project_path)
            
            assert config.project_name == "test-project"
            assert config.language == "python"
            assert config.framework == "fastapi"
            assert "core.tdd" in config.includes
            assert config.options["show_module_boundaries"] is True
    
    def test_save_and_load(self):
        """Test saving and loading configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            config_dir = project_path / ".claude"
            config_dir.mkdir()
            
            # Create original config
            config = ClydeConfig(
                project_name="test-project",
                language="python",
                framework="fastapi",
                project_path=project_path
            )
            
            # Save config
            config.save()
            
            # Load config
            loaded_config = ClydeConfig.from_file(config_dir / "config.yaml")
            
            assert loaded_config.project_name == config.project_name
            assert loaded_config.language == config.language
            assert loaded_config.framework == config.framework
    
    def test_get_config_hash(self):
        """Test configuration hash generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            config1 = ClydeConfig(
                project_name="test-project",
                language="python",
                project_path=project_path
            )
            
            config2 = ClydeConfig(
                project_name="test-project",
                language="python",
                project_path=project_path
            )
            
            # Same configuration should have same hash
            assert config1.get_config_hash() == config2.get_config_hash()
            
            # Different configuration should have different hash
            config2.add_module("docker")
            assert config1.get_config_hash() != config2.get_config_hash()


class TestModuleResolver:
    """Test the ModuleResolver class."""
    
    def test_resolve_module_success(self):
        """Test successful module resolution."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            # Create a mock modules directory structure
            modules_dir = project_path / "modules"
            core_dir = modules_dir / "core"
            core_dir.mkdir(parents=True)
            
            test_module = core_dir / "test.md"
            test_content = "# Test Module\n\nThis is a test module."
            test_module.write_text(test_content)
            
            # Mock the get_modules_dir method
            config = ClydeConfig(
                project_name="test-project",
                language="python", 
                project_path=project_path
            )
            
            with patch.object(config, 'get_modules_dir', return_value=modules_dir):
                resolver = ModuleResolver(config)
                content = resolver.resolve_module("core.test")
                
                assert content == test_content
    
    def test_resolve_module_not_found(self):
        """Test module resolution when module doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            config = ClydeConfig(
                project_name="test-project",
                language="python",
                project_path=project_path
            )
            
            resolver = ModuleResolver(config)
            content = resolver.resolve_module("nonexistent.module")
            
            assert content is None
    
    def test_get_all_module_content(self):
        """Test getting content for all modules."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            config = ClydeConfig(
                project_name="test-project",
                language="python",
                project_path=project_path
            )
            
            # Mock the resolve_module method
            with patch.object(ModuleResolver, 'resolve_module') as mock_resolve:
                mock_resolve.side_effect = lambda x: f"Content for {x}" if x.startswith("core.") else None
                
                resolver = ModuleResolver(config)
                all_content = resolver.get_all_module_content()
                
                # Should only contain content for modules that exist
                assert len(all_content) > 0
                for module_id, content in all_content.items():
                    assert content.startswith("Content for")


class TestConfigValidation:
    """Test configuration validation."""
    
    def test_validate_modules_success(self):
        """Test module validation when all modules exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            config = ClydeConfig(
                project_name="test-project",
                language="python",
                project_path=project_path,
                includes=["core.tdd"]  # Simple include list
            )
            
            # Mock module existence
            with patch.object(Path, 'exists', return_value=True):
                missing = config.validate_modules()
                assert missing == []
    
    def test_validate_modules_missing(self):
        """Test module validation when modules are missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            config = ClydeConfig(
                project_name="test-project",
                language="python",
                project_path=project_path,
                includes=["nonexistent.module"]
            )
            
            # Mock module non-existence
            with patch.object(Path, 'exists', return_value=False):
                missing = config.validate_modules()
                assert "nonexistent.module" in missing


if __name__ == "__main__":
    pytest.main([__file__])