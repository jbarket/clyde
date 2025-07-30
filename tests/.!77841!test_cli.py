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
            assert Path('.clyde/config.yaml').exists()
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
            with open('.clyde/config.yaml') as f:
                config_content = f.read()
                assert 'python' in config_content
                assert 'fastapi' in config_content
    
    def test_init_existing_config(self):
        """Test initialization when config already exists."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            Path('.claude').mkdir()
            Path('.clyde/config.yaml').touch()
            
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
            assert Path('myproject/.clyde/config.yaml').exists()


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
