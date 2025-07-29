"""
Tests for Clyde CLI interface.
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from clyde.src.cli import cli


class TestCLIInit:
    """Test the CLI init command."""
    
    def test_init_basic(self):
        """Test basic project initialization."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            # Mock user input for language selection
            result = runner.invoke(cli, ['init'], input='python\nfastapi\n')
            
            assert result.exit_code == 0
            assert " Initialized clyde project" in result.output
            
            # Check that files were created
            assert Path('.claude').exists()
            assert Path('.claude/config.yaml').exists()
            assert Path('claude.md').exists()
    
    def test_init_with_options(self):
        """Test initialization with command line options."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            result = runner.invoke(cli, [
                'init', 
                '--language', 'python',
                '--framework', 'fastapi',
                '--name', 'my-project'
            ])
            
            assert result.exit_code == 0
            assert " Initialized clyde project" in result.output
            
            # Check configuration content
            with open('.claude/config.yaml') as f:
                config_content = f.read()
                assert 'python' in config_content
                assert 'fastapi' in config_content
    
    def test_init_existing_config(self):
        """Test initialization when config already exists."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            Path('.claude').mkdir()
            Path('.claude/config.yaml').touch()
            
            # Should prompt for overwrite
            result = runner.invoke(cli, ['init'], input='n\n')
            
            assert result.exit_code == 0
            assert "L Initialization cancelled" in result.output
    
    def test_init_custom_path(self):
        """Test initialization in custom directory."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            Path('myproject').mkdir()
            
            result = runner.invoke(cli, [
                'init',
                '--language', 'python',
                'myproject'
            ])
            
            assert result.exit_code == 0
            assert Path('myproject/.claude/config.yaml').exists()


class TestCLISync:
    """Test the CLI sync command."""
    
    def setup_method(self):
        """Set up test configuration."""
        self.runner = CliRunner()
    
    def create_test_config(self, tmpdir: Path):
        """Create a test configuration in the given directory."""
        claude_dir = tmpdir / '.claude'
        claude_dir.mkdir()
        
        config_data = {
            'version': '1.0',
            'project': {
                'name': 'test-project',
                'language': 'python'
            },
            'includes': ['core.tdd', 'python.general'],
            'options': {'show_module_boundaries': True}
        }
        
        with open(claude_dir / 'config.yaml', 'w') as f:
            yaml.dump(config_data, f)
    
    @patch('clyde.src.cli.SyncManager')
    def test_sync_basic(self, mock_sync_manager):
        """Test basic sync functionality."""
        mock_sync_instance = MagicMock()
        mock_sync_manager.return_value = mock_sync_instance
        
        with self.runner.isolated_filesystem():
            tmpdir = Path('.')
            self.create_test_config(tmpdir)
            
            result = self.runner.invoke(cli, ['sync'])
            
            assert result.exit_code == 0
            assert " Configuration synced successfully" in result.output
            mock_sync_instance.sync.assert_called_once()
    
    @patch('clyde.src.cli.SyncManager')
    def test_sync_check_mode(self, mock_sync_manager):
        """Test sync in check mode."""
        mock_sync_instance = MagicMock()
        mock_sync_instance.preview_changes.return_value = ['Update generated.md']
        mock_sync_manager.return_value = mock_sync_instance
        
        with self.runner.isolated_filesystem():
            tmpdir = Path('.')
            self.create_test_config(tmpdir)
            
            result = self.runner.invoke(cli, ['sync', '--check'])
            
            assert result.exit_code == 0
            assert "=Ë Would make the following changes:" in result.output
            assert "Update generated.md" in result.output
            mock_sync_instance.preview_changes.assert_called_once()
    
    def test_sync_no_config(self):
        """Test sync when no configuration exists."""
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(cli, ['sync'])
            
            assert result.exit_code == 1
            assert "L No clyde configuration found" in result.output
    
    @patch('clyde.src.cli.ClydeConfig')
    def test_sync_add_module(self, mock_config_class):
        """Test adding modules during sync."""
        mock_config = MagicMock()
        mock_config_class.from_file.return_value = mock_config
        
        with self.runner.isolated_filesystem():
            tmpdir = Path('.')
            self.create_test_config(tmpdir)
            
            result = self.runner.invoke(cli, ['sync', '--add', 'docker'])
            
            assert result.exit_code == 0
            mock_config.add_module.assert_called_with('docker')
            mock_config.save.assert_called_once()


class TestCLIListModules:
    """Test the CLI list-modules command."""
    
    def test_list_modules_basic(self):
        """Test basic module listing."""
        runner = CliRunner()
        
        # Mock the modules directory
        with patch('clyde.src.cli.Path') as mock_path:
            mock_modules_dir = MagicMock()
            mock_modules_dir.exists.return_value = True
            mock_modules_dir.iterdir.return_value = [
                MagicMock(name='core', is_dir=lambda: True),
                MagicMock(name='python', is_dir=lambda: True)
            ]
            
            mock_path.return_value.parent.parent = mock_modules_dir
            
            result = runner.invoke(cli, ['list-modules'])
            
            assert result.exit_code == 0
            assert "=Ú Available modules:" in result.output


class TestCLIShow:
    """Test the CLI show command."""
    
    def test_show_module_exists(self):
        """Test showing a module that exists."""
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a mock module file
            modules_dir = Path(tmpdir) / 'modules'
            core_dir = modules_dir / 'core'
            core_dir.mkdir(parents=True)
            
            test_module = core_dir / 'tdd.md'
            test_content = "# Test-Driven Development\n\nTDD principles..."
            test_module.write_text(test_content)
            
            # Mock the modules directory path
            with patch('clyde.src.cli.Path') as mock_path:
                mock_path.return_value.parent.parent = modules_dir
                
                result = runner.invoke(cli, ['show', 'core.tdd'])
                
                assert result.exit_code == 0
                # Output goes through pager, so we can't easily check content
    
    def test_show_module_not_found(self):
        """Test showing a module that doesn't exist."""
        runner = CliRunner()
        
        result = runner.invoke(cli, ['show', 'nonexistent.module'])
        
        assert result.exit_code == 1
        assert "L Module not found" in result.output


class TestCLICreateModule:
    """Test the CLI create-module command."""
    
    def test_create_module_basic(self):
        """Test basic module creation."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ['create-module', 'custom.my-patterns'])
            
            assert result.exit_code == 0
            assert " Created custom module" in result.output
            
            # Check that module file was created
            module_file = Path('.claude/custom/my-patterns.md')
            assert module_file.exists()
            
            # Check content
            content = module_file.read_text()
            assert "# My Patterns" in content
    
    def test_create_module_invalid_id(self):
        """Test creating module with invalid ID."""
        runner = CliRunner()
        
        result = runner.invoke(cli, ['create-module', 'invalid'])
        
        assert result.exit_code == 1
        assert "L Module ID must contain at least one dot" in result.output
    
    def test_create_module_existing(self):
        """Test creating module that already exists."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            # Create module first
            Path('.claude/custom').mkdir(parents=True)
            Path('.claude/custom/existing.md').touch()
            
            # Try to create again, decline overwrite
            result = runner.invoke(cli, ['create-module', 'custom.existing'], input='n\n')
            
            assert result.exit_code == 0
            assert "L Module creation cancelled" in result.output


if __name__ == "__main__":
    pytest.main([__file__])