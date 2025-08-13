#!/usr/bin/env python3
"""
Tests for Docker execution functionality in ALITA reproduction.

This module contains comprehensive tests for the Docker security execution environment,
including DockerExecutionAction, security validation, result validation, and error recovery.
"""

import pytest
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from actions.docker_execution import DockerExecutionAction, DockerConfig, ExecutionStatus, ExecutionResult
from utils.security_validator import SecurityValidator, quick_security_check, SecurityLevel
from utils.docker_config import DockerConfigManager, ContainerProfile, get_config_for_script_type
from utils.result_validator import ResultValidator, quick_validate_result, ResultStatus
from utils.error_recovery import ErrorRecoverySystem, analyze_error_type
from utils.execution_monitor import ExecutionMonitor, MonitoringConfig, MonitoringLevel
from agents.manager_agent import ManagerAgent


class TestDockerConfiguration:
    """Test Docker configuration management."""
    
    def test_docker_config_creation(self):
        """Test creating Docker configuration."""
        config = DockerConfig(
            image_tag="python:3.9-slim",
            memory_limit="512m",
            timeout=30
        )
        
        assert config.image_tag == "python:3.9-slim"
        assert config.memory_limit == "512m"
        assert config.timeout == 30
    
    def test_docker_config_manager(self):
        """Test Docker configuration manager."""
        manager = DockerConfigManager()
        
        # Test profile listing
        profiles = manager.list_profiles()
        assert len(profiles) > 0
        assert "standard" in profiles
        assert "secure" in profiles
        
        # Test getting profile
        config = manager.get_profile(ContainerProfile.STANDARD)
        assert config.image_tag == "python:3.9-slim"
        
        # Test secure profile
        secure_config = manager.get_profile(ContainerProfile.SECURE)
        assert secure_config.resource_limits.memory_limit == "128m"
        assert secure_config.execution_settings.timeout == 10
    
    def test_script_type_config_recommendation(self):
        """Test configuration recommendation based on script type."""
        config = get_config_for_script_type("web_scraping")
        assert config.profile.value == "web"
        
        config = get_config_for_script_type("data_processing")
        assert config.profile.value == "scientific"
        
        config = get_config_for_script_type("unknown")
        assert config.profile.value == "standard"


class TestSecurityValidator:
    """Test security validation functionality."""
    
    def test_security_validator_initialization(self):
        """Test security validator initialization."""
        validator = SecurityValidator()
        assert validator is not None
    
    def test_safe_code_validation(self):
        """Test validation of safe code."""
        safe_code = '''
def greet(name):
    """Greet someone."""
    return f"Hello, {name}!"

def main():
    print(greet("World"))

if __name__ == "__main__":
    main()
'''
        result = quick_security_check(safe_code)
        
        assert result['is_safe'] is True
        assert result['critical_issues'] == 0
        assert result['total_issues'] >= 0
    
    def test_dangerous_code_validation(self):
        """Test validation of dangerous code."""
        dangerous_code = '''
import os
import subprocess

def dangerous_function():
    user_input = input("Enter command: ")
    os.system(user_input)  # Security risk
    result = eval(user_input)  # Another risk
    return result
'''
        result = quick_security_check(dangerous_code)
        
        assert result['is_safe'] is False
        assert result['total_issues'] > 0
        assert result['has_security_risks'] is True
    
    def test_import_validation(self):
        """Test validation of imports."""
        validator = SecurityValidator()
        
        # Test dangerous import
        dangerous_import = "import subprocess\nsubprocess.call(['ls'])"
        report = validator.analyze_code(dangerous_import)
        
        assert not report.is_safe_to_execute
        assert any(issue.violation_type.value == "dangerous_import" for issue in report.issues)


class TestResultValidator:
    """Test result validation functionality."""
    
    def test_result_validator_initialization(self):
        """Test result validator initialization."""
        validator = ResultValidator()
        assert validator is not None
    
    def test_successful_output_validation(self):
        """Test validation of successful output."""
        output = "Processing completed successfully!\nResults: 42 items processed"
        
        result = quick_validate_result(output, None, 1.5)
        
        assert result['is_valid'] is True
        assert result['status'] == 'valid'
        assert result['error_count'] == 0
    
    def test_error_output_validation(self):
        """Test validation of error output."""
        output = ""
        error = "ValueError: invalid input data"
        
        result = quick_validate_result(output, error, 0.1)
        
        assert result['is_valid'] is False
        assert result['status'] == 'error'
        assert result['error_count'] > 0
    
    def test_script_type_specific_validation(self):
        """Test script type specific validation."""
        # Data processing output
        data_output = "Processed 1000 rows\nAverage: 45.7\nStandard deviation: 12.3"
        result = quick_validate_result(data_output, None, 2.0, "data_processing")
        
        assert result['is_valid'] is True
        
        # Web scraping minimal output
        web_output = "Done"
        result = quick_validate_result(web_output, None, 1.0, "web_scraping")
        
        assert result['warning_count'] > 0  # Should warn about minimal output


class TestErrorRecovery:
    """Test error recovery functionality."""
    
    def test_error_type_analysis(self):
        """Test error type analysis."""
        # Timeout error
        timeout_error = "TimeoutError: execution time exceeded"
        result = analyze_error_type(timeout_error)
        
        assert result['error_type'] == 'timeout'
        assert 'Increase execution timeout' in result['suggested_fixes']
        
        # Import error
        import_error = "ImportError: No module named 'pandas'"
        result = analyze_error_type(import_error)
        
        assert result['error_type'] == 'import_error'
        assert 'Install missing Python packages' in result['suggested_fixes']
    
    def test_recovery_system_initialization(self):
        """Test error recovery system initialization."""
        recovery = ErrorRecoverySystem()
        assert recovery is not None
        assert recovery.max_total_attempts == 3


class TestExecutionMonitor:
    """Test execution monitoring functionality."""
    
    def test_monitor_initialization(self):
        """Test monitor initialization."""
        config = MonitoringConfig(level=MonitoringLevel.STANDARD)
        monitor = ExecutionMonitor(config)
        assert monitor is not None
    
    def test_execution_tracking(self):
        """Test execution tracking."""
        config = MonitoringConfig(
            level=MonitoringLevel.MINIMAL,
            enable_resource_monitoring=False
        )
        monitor = ExecutionMonitor(config)
        
        # Start monitoring
        execution_id = monitor.start_execution_monitoring(
            docker_image="python:3.9-slim",
            timeout=30
        )
        
        assert execution_id is not None
        
        # Update phase
        from utils.execution_monitor import ExecutionPhase
        monitor.update_execution_phase(execution_id, ExecutionPhase.CODE_EXECUTION)
        
        # Record result
        monitor.record_execution_result(execution_id, True, 100)
        
        # Stop monitoring
        metrics = monitor.stop_execution_monitoring(execution_id)
        
        assert metrics is not None
        assert metrics.success is True
        assert metrics.output_size_bytes == 100


@pytest.mark.skipif(not os.getenv("DOCKER_AVAILABLE"), reason="Docker not available")
class TestDockerExecutionAction:
    """Test Docker execution action (requires Docker)."""
    
    def setup_method(self):
        """Set up test method."""
        config = DockerConfig(
            image_tag="python:3.9-alpine",
            timeout=10,
            print_stdout=False,
            print_stderr=False
        )
        self.executor = DockerExecutionAction(config)
    
    def test_simple_code_execution(self):
        """Test simple code execution."""
        code = "print('Hello from Docker!')"
        
        result = self.executor.execute_code(code, validate_security=False)
        
        assert result.status == ExecutionStatus.SUCCESS
        assert "Hello from Docker!" in result.output
        assert result.execution_time > 0
    
    def test_code_with_security_validation(self):
        """Test code execution with security validation."""
        safe_code = "print('Safe code execution')"
        
        result = self.executor.execute_code(safe_code, validate_security=True)
        
        assert result.status == ExecutionStatus.SUCCESS
        assert result.security_issues is None or len(result.security_issues) == 0
    
    def test_dangerous_code_execution(self):
        """Test execution of code with security issues."""
        dangerous_code = "import os; os.system('echo dangerous')"
        
        result = self.executor.execute_code(dangerous_code, validate_security=True)
        
        # Should execute but report security issues
        assert result.security_issues is not None
        assert len(result.security_issues) > 0
    
    def test_environment_validation(self):
        """Test Docker environment validation."""
        result = self.executor.validate_execution_environment()
        
        assert result['valid'] is True
        assert 'docker_image' in result
        assert 'test_output' in result
    
    def test_execution_statistics(self):
        """Test execution statistics."""
        # Execute some code first
        self.executor.execute_code("print('test')", validate_security=False)
        
        stats = self.executor.get_execution_statistics()
        
        assert stats['total_executions'] >= 1
        assert stats['successful_executions'] >= 1
        assert 'success_rate' in stats


class TestManagerAgentDockerIntegration:
    """Test Docker integration with Manager Agent."""
    
    def setup_method(self):
        """Set up test method with mocked LLM."""
        # Mock the OpenAI LLM to avoid requiring API keys
        with patch('evoagentx.models.OpenAILLMConfig') as mock_llm_config:
            mock_llm_config.return_value = Mock()
            self.manager = ManagerAgent()
    
    def test_docker_capabilities(self):
        """Test Docker capabilities in Manager Agent."""
        capabilities = self.manager.get_capabilities()
        
        assert "docker_execution" in capabilities
        assert "security_validation" in capabilities
        assert "result_validation" in capabilities
        assert "error_recovery" in capabilities
        assert "execution_monitoring" in capabilities
    
    def test_security_validation_integration(self):
        """Test security validation integration."""
        safe_code = "print('Hello, world!')"
        
        result = self.manager.validate_code_security(safe_code)
        
        assert result['is_safe'] is True
        assert result['critical_issues'] == 0
    
    @patch('examples.alita_reproduction.actions.docker_execution.DockerExecutionAction')
    def test_docker_execution_integration(self, mock_docker_action):
        """Test Docker execution integration with Manager Agent."""
        # Mock successful execution
        mock_result = ExecutionResult(
            status=ExecutionStatus.SUCCESS,
            output="Hello from mocked Docker!",
            execution_time=1.5
        )
        mock_docker_action.return_value.execute_code.return_value = mock_result
        mock_docker_action.return_value.config.image_tag = "python:3.9-slim"
        mock_docker_action.return_value.config.timeout = 30
        
        code = "print('Hello, world!')"
        result = self.manager.execute_code_in_docker(code, validate_security=False, monitor_execution=False)
        
        assert result['success'] is True
        assert result['execution_method'] == 'docker'
        assert 'validation_result' in result
    
    def test_docker_environment_validation(self):
        """Test Docker environment validation through Manager Agent."""
        # This will fail without Docker, but tests the integration
        result = self.manager.validate_docker_environment()
        
        # Should return either success or a proper error
        assert 'valid' in result
        if not result['valid']:
            assert 'error' in result


class TestDockerIntegrationWorkflow:
    """Test complete Docker integration workflow."""
    
    def test_script_generation_and_execution_workflow(self):
        """Test complete workflow from generation to execution."""
        with patch('evoagentx.models.OpenAILLMConfig'):
            manager = ManagerAgent()
        
        # Step 1: Generate a script
        script_result = manager.create_script_from_requirements(
            script_name="test_workflow_script",
            task_description="Print hello world message",
            script_type="simple"
        )
        
        assert script_result['success'] is True
        script_path = script_result['script_path']
        
        # Step 2: Validate security
        with open(script_path, 'r') as f:
            script_content = f.read()
        
        security_result = manager.validate_code_security(script_content)
        assert security_result['is_safe'] is True
        
        # Step 3: Execute with Docker (mocked)
        with patch('examples.alita_reproduction.actions.docker_execution.DockerExecutionAction') as mock_docker:
            mock_result = ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                output="Hello World",
                execution_time=1.0
            )
            mock_docker.return_value.execute_script_file.return_value = mock_result
            mock_docker.return_value.config.image_tag = "python:3.9-slim"
            mock_docker.return_value.config.timeout = 30
            
            execution_result = manager.execute_script_in_docker(
                script_path, script_type="simple", validate_security=False, monitor_execution=False
            )
            
            assert execution_result['success'] is True
            assert execution_result['execution_method'] == 'docker'
    
    def test_error_recovery_workflow(self):
        """Test error recovery workflow."""
        recovery = ErrorRecoverySystem()
        
        # Simulate a function that fails then succeeds
        call_count = 0
        def mock_execution_function():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("TimeoutError: execution timed out")
            return {"success": True, "output": "Success after retry"}
        
        # Test recovery
        result = recovery.recover_from_error(
            error_message="TimeoutError: execution timed out",
            execution_function=mock_execution_function,
            max_total_attempts=3
        )
        
        # Should succeed on second attempt due to retry strategy
        assert result.success is True or result.attempts_made > 1
        assert len(result.recovery_log) > 0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])