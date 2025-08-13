#!/usr/bin/env python3
"""
Docker Configuration Manager for ALITA reproduction.

This module provides configuration management for Docker execution environments,
including resource limits, security settings, and environment customization.

Author: ALITA Development Team
Created: 2025-08-13
Version: 1.0.0
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict, field
from enum import Enum

logger = logging.getLogger(__name__)


class ContainerProfile(Enum):
    """Pre-defined container profiles for different use cases."""
    MINIMAL = "minimal"        # Basic Python execution
    STANDARD = "standard"      # Standard data processing
    SCIENTIFIC = "scientific"  # Scientific computing
    WEB = "web"               # Web scraping and requests
    SECURE = "secure"         # Maximum security restrictions
    DEVELOPMENT = "development"  # Development and testing


class NetworkMode(Enum):
    """Network mode options for containers."""
    NONE = "none"           # No network access
    BRIDGE = "bridge"       # Default bridge network
    HOST = "host"           # Host network (less secure)
    CUSTOM = "custom"       # Custom network


@dataclass
class ResourceLimits:
    """Container resource limitations."""
    memory_limit: str = "512m"          # Memory limit (e.g., "512m", "1g")
    memory_swap: str = "1g"             # Memory + swap limit
    cpu_quota: int = 100000             # CPU quota (100000 = 1 CPU)
    cpu_period: int = 100000            # CPU period
    cpu_shares: int = 1024              # CPU shares (relative weight)
    pids_limit: int = 100               # Maximum number of processes
    ulimits: Dict[str, int] = field(default_factory=lambda: {
        "nofile": 1024,      # Max open files
        "nproc": 64,         # Max processes
        "fsize": 1048576     # Max file size (1MB)
    })
    
    def to_docker_params(self) -> Dict[str, Any]:
        """Convert to Docker API parameters."""
        return {
            "mem_limit": self.memory_limit,
            "memswap_limit": self.memory_swap,
            "cpu_quota": self.cpu_quota,
            "cpu_period": self.cpu_period,
            "cpu_shares": self.cpu_shares,
            "pids_limit": self.pids_limit,
            "ulimits": [{"Name": k, "Soft": v, "Hard": v} for k, v in self.ulimits.items()]
        }


@dataclass
class SecuritySettings:
    """Container security configuration."""
    network_mode: NetworkMode = NetworkMode.NONE
    read_only_root: bool = True         # Read-only root filesystem
    no_new_privileges: bool = True      # Prevent privilege escalation
    drop_capabilities: List[str] = field(default_factory=lambda: [
        "ALL"  # Drop all capabilities by default
    ])
    add_capabilities: List[str] = field(default_factory=list)
    security_opt: List[str] = field(default_factory=lambda: [
        "no-new-privileges:true",
        "apparmor:docker-default"
    ])
    tmpfs_mounts: List[str] = field(default_factory=lambda: [
        "/tmp:rw,noexec,nosuid,size=100m"
    ])
    
    def to_docker_params(self) -> Dict[str, Any]:
        """Convert to Docker API parameters."""
        params = {
            "network_mode": self.network_mode.value,
            "read_only": self.read_only_root,
            "security_opt": self.security_opt
        }
        
        if self.drop_capabilities:
            params["cap_drop"] = self.drop_capabilities
        
        if self.add_capabilities:
            params["cap_add"] = self.add_capabilities
        
        if self.tmpfs_mounts:
            params["tmpfs"] = {mount.split(":")[0]: mount.split(":", 1)[1] 
                             for mount in self.tmpfs_mounts if ":" in mount}
        
        return params


@dataclass
class ExecutionSettings:
    """Code execution configuration."""
    timeout: int = 30                   # Execution timeout in seconds
    working_directory: str = "/app"     # Container working directory
    environment_vars: Dict[str, str] = field(default_factory=dict)
    python_path: List[str] = field(default_factory=list)
    startup_commands: List[str] = field(default_factory=list)
    cleanup_commands: List[str] = field(default_factory=list)
    allowed_file_patterns: List[str] = field(default_factory=lambda: [
        "*.py", "*.txt", "*.json", "*.csv", "*.yml", "*.yaml"
    ])
    blocked_file_patterns: List[str] = field(default_factory=lambda: [
        "*.sh", "*.exe", "*.bat", "*.cmd", "*.ps1"
    ])


@dataclass
class DockerConfiguration:
    """Complete Docker container configuration."""
    profile: ContainerProfile = ContainerProfile.STANDARD
    image_tag: str = "python:3.9-slim"
    container_name_prefix: str = "alita-executor"
    resource_limits: ResourceLimits = field(default_factory=ResourceLimits)
    security_settings: SecuritySettings = field(default_factory=SecuritySettings)
    execution_settings: ExecutionSettings = field(default_factory=ExecutionSettings)
    
    # Toolkit-specific settings
    print_stdout: bool = True
    print_stderr: bool = True
    require_confirm: bool = False
    
    def to_toolkit_params(self) -> Dict[str, Any]:
        """Convert to DockerInterpreterToolkit parameters."""
        return {
            "image_tag": self.image_tag,
            "container_directory": self.execution_settings.working_directory,
            "print_stdout": self.print_stdout,
            "print_stderr": self.print_stderr,
            "require_confirm": self.require_confirm
        }
    
    def to_full_docker_params(self) -> Dict[str, Any]:
        """Convert to full Docker API parameters (for future enhancement)."""
        params = {}
        params.update(self.resource_limits.to_docker_params())
        params.update(self.security_settings.to_docker_params())
        
        if self.execution_settings.environment_vars:
            params["environment"] = self.execution_settings.environment_vars
        
        return params


class DockerConfigManager:
    """
    Manager for Docker configurations and profiles.
    
    Provides pre-defined configurations for different use cases
    and allows for configuration customization and persistence.
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_dir: Directory for configuration files
        """
        self.config_dir = config_dir or Path.cwd() / "config"
        self.config_dir.mkdir(exist_ok=True)
        
        # Pre-defined profiles
        self._profiles = self._create_predefined_profiles()
        
        logger.info(f"DockerConfigManager initialized with {len(self._profiles)} profiles")
    
    def _create_predefined_profiles(self) -> Dict[ContainerProfile, DockerConfiguration]:
        """Create pre-defined configuration profiles."""
        profiles = {}
        
        # Minimal profile - basic execution
        profiles[ContainerProfile.MINIMAL] = DockerConfiguration(
            profile=ContainerProfile.MINIMAL,
            image_tag="python:3.9-alpine",
            resource_limits=ResourceLimits(
                memory_limit="256m",
                memory_swap="512m",
                pids_limit=50,
                ulimits={"nofile": 512, "nproc": 32, "fsize": 524288}
            ),
            execution_settings=ExecutionSettings(timeout=15)
        )
        
        # Standard profile - general purpose
        profiles[ContainerProfile.STANDARD] = DockerConfiguration(
            profile=ContainerProfile.STANDARD,
            image_tag="python:3.9-slim",
            resource_limits=ResourceLimits(),
            execution_settings=ExecutionSettings()
        )
        
        # Scientific profile - data processing
        profiles[ContainerProfile.SCIENTIFIC] = DockerConfiguration(
            profile=ContainerProfile.SCIENTIFIC,
            image_tag="python:3.9",
            resource_limits=ResourceLimits(
                memory_limit="2g",
                memory_swap="4g",
                cpu_quota=200000,  # 2 CPUs
                pids_limit=200
            ),
            execution_settings=ExecutionSettings(
                timeout=300,  # 5 minutes
                environment_vars={"PYTHONPATH": "/app:/usr/local/lib/python3.9/site-packages"}
            )
        )
        
        # Web profile - web scraping
        profiles[ContainerProfile.WEB] = DockerConfiguration(
            profile=ContainerProfile.WEB,
            image_tag="python:3.9-slim",
            resource_limits=ResourceLimits(
                memory_limit="1g",
                memory_swap="2g"
            ),
            security_settings=SecuritySettings(
                network_mode=NetworkMode.BRIDGE,  # Needs network for web requests
                read_only_root=True
            ),
            execution_settings=ExecutionSettings(
                timeout=60,
                environment_vars={"PYTHONPATH": "/app"}
            )
        )
        
        # Secure profile - maximum security
        profiles[ContainerProfile.SECURE] = DockerConfiguration(
            profile=ContainerProfile.SECURE,
            image_tag="python:3.9-alpine",
            resource_limits=ResourceLimits(
                memory_limit="128m",
                memory_swap="256m",
                pids_limit=20,
                ulimits={"nofile": 256, "nproc": 16, "fsize": 262144}
            ),
            security_settings=SecuritySettings(
                network_mode=NetworkMode.NONE,
                read_only_root=True,
                no_new_privileges=True,
                drop_capabilities=["ALL"],
                security_opt=[
                    "no-new-privileges:true",
                    "apparmor:docker-default",
                    "seccomp:default"
                ]
            ),
            execution_settings=ExecutionSettings(
                timeout=10,
                blocked_file_patterns=["*"]  # Block all file access
            )
        )
        
        # Development profile - for testing
        profiles[ContainerProfile.DEVELOPMENT] = DockerConfiguration(
            profile=ContainerProfile.DEVELOPMENT,
            image_tag="python:3.9",
            resource_limits=ResourceLimits(
                memory_limit="1g",
                memory_swap="2g",
                pids_limit=150
            ),
            security_settings=SecuritySettings(
                network_mode=NetworkMode.BRIDGE,
                read_only_root=False  # Allow file writes for development
            ),
            execution_settings=ExecutionSettings(
                timeout=120,
                environment_vars={
                    "PYTHONPATH": "/app",
                    "DEVELOPMENT_MODE": "true"
                }
            )
        )
        
        return profiles
    
    def get_profile(self, profile: ContainerProfile) -> DockerConfiguration:
        """
        Get a pre-defined configuration profile.
        
        Args:
            profile: Container profile to retrieve
            
        Returns:
            DockerConfiguration for the profile
        """
        if profile not in self._profiles:
            logger.warning(f"Profile {profile} not found, using STANDARD")
            profile = ContainerProfile.STANDARD
        
        return self._profiles[profile]
    
    def list_profiles(self) -> Dict[str, str]:
        """
        List available profiles with descriptions.
        
        Returns:
            Dictionary mapping profile names to descriptions
        """
        descriptions = {
            ContainerProfile.MINIMAL: "Basic Python execution with minimal resources",
            ContainerProfile.STANDARD: "Standard configuration for general use",
            ContainerProfile.SCIENTIFIC: "High-resource configuration for data processing",
            ContainerProfile.WEB: "Network-enabled configuration for web scraping",
            ContainerProfile.SECURE: "Maximum security with minimal permissions",
            ContainerProfile.DEVELOPMENT: "Development-friendly configuration"
        }
        
        return {profile.value: descriptions[profile] for profile in self._profiles.keys()}
    
    def create_custom_config(
        self,
        base_profile: ContainerProfile = ContainerProfile.STANDARD,
        **overrides
    ) -> DockerConfiguration:
        """
        Create a custom configuration based on a profile.
        
        Args:
            base_profile: Base profile to start from
            **overrides: Configuration overrides
            
        Returns:
            Custom DockerConfiguration
        """
        base_config = self.get_profile(base_profile)
        
        # Create a copy and apply overrides
        custom_config = DockerConfiguration(**asdict(base_config))
        
        for key, value in overrides.items():
            if hasattr(custom_config, key):
                setattr(custom_config, key, value)
            else:
                logger.warning(f"Unknown configuration key: {key}")
        
        return custom_config
    
    def save_config(self, config: DockerConfiguration, name: str) -> bool:
        """
        Save a configuration to disk.
        
        Args:
            config: Configuration to save
            name: Name for the saved configuration
            
        Returns:
            True if saved successfully
        """
        try:
            config_file = self.config_dir / f"{name}.json"
            config_dict = asdict(config)
            
            # Convert enums to strings for JSON serialization
            self._convert_enums_to_strings(config_dict)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2)
            
            logger.info(f"Configuration saved: {config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {str(e)}")
            return False
    
    def load_config(self, name: str) -> Optional[DockerConfiguration]:
        """
        Load a configuration from disk.
        
        Args:
            name: Name of the saved configuration
            
        Returns:
            DockerConfiguration if found, None otherwise
        """
        try:
            config_file = self.config_dir / f"{name}.json"
            
            if not config_file.exists():
                logger.error(f"Configuration file not found: {config_file}")
                return None
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            
            # Convert string enums back to enum objects
            self._convert_strings_to_enums(config_dict)
            
            return DockerConfiguration(**config_dict)
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {str(e)}")
            return None
    
    def _convert_enums_to_strings(self, data: Any) -> None:
        """Convert enum objects to strings for JSON serialization."""
        if isinstance(data, dict):
            for key, value in data.items():
                if hasattr(value, 'value'):  # Enum object
                    data[key] = value.value
                elif isinstance(value, (dict, list)):
                    self._convert_enums_to_strings(value)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if hasattr(item, 'value'):  # Enum object
                    data[i] = item.value
                elif isinstance(item, (dict, list)):
                    self._convert_enums_to_strings(item)
    
    def _convert_strings_to_enums(self, data: Dict[str, Any]) -> None:
        """Convert string values back to enum objects."""
        # Profile conversion
        if 'profile' in data:
            try:
                data['profile'] = ContainerProfile(data['profile'])
            except ValueError:
                data['profile'] = ContainerProfile.STANDARD
        
        # Network mode conversion
        if 'security_settings' in data and 'network_mode' in data['security_settings']:
            try:
                data['security_settings']['network_mode'] = NetworkMode(
                    data['security_settings']['network_mode']
                )
            except ValueError:
                data['security_settings']['network_mode'] = NetworkMode.NONE
    
    def validate_config(self, config: DockerConfiguration) -> List[str]:
        """
        Validate a Docker configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            List of validation warnings/errors
        """
        warnings = []
        
        # Check resource limits
        memory_mb = self._parse_memory_limit(config.resource_limits.memory_limit)
        if memory_mb < 64:
            warnings.append("Memory limit is very low (< 64MB)")
        elif memory_mb > 8192:
            warnings.append("Memory limit is very high (> 8GB)")
        
        # Check timeout
        if config.execution_settings.timeout < 1:
            warnings.append("Timeout is too low")
        elif config.execution_settings.timeout > 600:
            warnings.append("Timeout is very high (> 10 minutes)")
        
        # Check security settings
        if config.security_settings.network_mode != NetworkMode.NONE:
            warnings.append("Network access enabled - review security implications")
        
        if not config.security_settings.read_only_root:
            warnings.append("Read-write root filesystem - potential security risk")
        
        return warnings
    
    def _parse_memory_limit(self, limit: str) -> int:
        """Parse memory limit string to MB."""
        limit = limit.lower()
        if limit.endswith('g'):
            return int(limit[:-1]) * 1024
        elif limit.endswith('m'):
            return int(limit[:-1])
        elif limit.endswith('k'):
            return int(limit[:-1]) // 1024
        else:
            # Assume bytes
            return int(limit) // (1024 * 1024)
    
    def get_recommended_profile(self, script_type: str) -> ContainerProfile:
        """
        Get recommended profile based on script type.
        
        Args:
            script_type: Type of script to execute
            
        Returns:
            Recommended ContainerProfile
        """
        recommendations = {
            "data_processing": ContainerProfile.SCIENTIFIC,
            "web_scraping": ContainerProfile.WEB,
            "automation": ContainerProfile.STANDARD,
            "api_client": ContainerProfile.WEB,
            "simple": ContainerProfile.MINIMAL,
            "test": ContainerProfile.DEVELOPMENT
        }
        
        return recommendations.get(script_type.lower(), ContainerProfile.STANDARD)


# Convenience functions
def get_secure_config() -> DockerConfiguration:
    """Get a secure configuration for untrusted code execution."""
    manager = DockerConfigManager()
    return manager.get_profile(ContainerProfile.SECURE)


def get_standard_config() -> DockerConfiguration:
    """Get a standard configuration for general use."""
    manager = DockerConfigManager()
    return manager.get_profile(ContainerProfile.STANDARD)


def get_config_for_script_type(script_type: str) -> DockerConfiguration:
    """Get recommended configuration for a script type."""
    manager = DockerConfigManager()
    profile = manager.get_recommended_profile(script_type)
    return manager.get_profile(profile)