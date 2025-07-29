"""
Clyde - Development Environment Configuration System

A tool that standardizes how Claude approaches software development across all projects.
This tool manages modular configuration files that define coding principles, 
framework conventions, and project-specific guidelines.
"""

__version__ = "1.0.0"
__author__ = "Development Team"
__description__ = "Development Environment Configuration System for Claude"

from .config import ClydeConfig, ModuleResolver
from .builder import ConfigBuilder, ConfigValidator
from .sync import SyncManager, ChangeDetector, AutoSync
from .cli import cli

__all__ = [
    "ClydeConfig",
    "ModuleResolver", 
    "ConfigBuilder",
    "ConfigValidator",
    "SyncManager",
    "ChangeDetector",
    "AutoSync",
    "cli"
]