#!/usr/bin/env python3
"""
Execution Monitor for ALITA reproduction.

This module provides comprehensive monitoring and logging for Docker script execution,
including performance tracking, resource monitoring, and detailed logging.

Author: ALITA Development Team
Created: 2025-08-13
Version: 1.0.0
"""

import time
import logging
import json
import threading
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import uuid
from datetime import datetime
import psutil
import queue

logger = logging.getLogger(__name__)


class ExecutionPhase(Enum):
    """Execution phases for monitoring."""
    INITIALIZATION = "initialization"
    VALIDATION = "validation"
    DOCKER_SETUP = "docker_setup"
    CODE_EXECUTION = "code_execution"
    RESULT_PROCESSING = "result_processing"
    CLEANUP = "cleanup"
    COMPLETED = "completed"
    FAILED = "failed"


class MonitoringLevel(Enum):
    """Monitoring detail levels."""
    MINIMAL = "minimal"      # Basic start/end logging
    STANDARD = "standard"    # Standard monitoring with key metrics
    DETAILED = "detailed"    # Detailed monitoring with resource usage
    DEBUG = "debug"         # Full debug information


@dataclass
class ExecutionMetrics:
    """Detailed execution metrics."""
    execution_id: str
    start_time: float
    end_time: Optional[float] = None
    phase: ExecutionPhase = ExecutionPhase.INITIALIZATION
    
    # Performance metrics
    cpu_usage_percent: List[float] = field(default_factory=list)
    memory_usage_mb: List[float] = field(default_factory=list)
    disk_io_bytes: Dict[str, int] = field(default_factory=dict)
    network_io_bytes: Dict[str, int] = field(default_factory=dict)
    
    # Execution details
    docker_image: Optional[str] = None
    container_id: Optional[str] = None
    timeout_seconds: Optional[int] = None
    security_issues: int = 0
    
    # Results
    success: Optional[bool] = None
    output_size_bytes: int = 0
    error_message: Optional[str] = None
    exit_code: Optional[int] = None
    
    # Timing breakdown
    phase_timings: Dict[str, float] = field(default_factory=dict)
    
    def get_total_duration(self) -> float:
        """Get total execution duration."""
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time
    
    def get_phase_duration(self, phase: ExecutionPhase) -> float:
        """Get duration for a specific phase."""
        return self.phase_timings.get(phase.value, 0.0)


@dataclass
class MonitoringConfig:
    """Configuration for execution monitoring."""
    level: MonitoringLevel = MonitoringLevel.STANDARD
    sample_interval: float = 1.0  # Resource sampling interval in seconds
    max_log_entries: int = 1000
    enable_resource_monitoring: bool = True
    enable_network_monitoring: bool = True
    enable_disk_monitoring: bool = True
    log_file: Optional[Path] = None
    metrics_file: Optional[Path] = None
    auto_cleanup: bool = True


class ExecutionMonitor:
    """
    Comprehensive execution monitor for Docker script execution.
    
    Provides real-time monitoring, logging, and performance tracking
    for script execution with configurable detail levels.
    """
    
    def __init__(self, config: MonitoringConfig = None):
        """
        Initialize execution monitor.
        
        Args:
            config: Monitoring configuration
        """
        self.config = config or MonitoringConfig()
        self._active_executions: Dict[str, ExecutionMetrics] = {}
        self._monitoring_threads: Dict[str, threading.Thread] = {}
        self._stop_monitoring: Dict[str, threading.Event] = {}
        self._metrics_queue = queue.Queue()
        
        # Set up logging
        self._setup_logging()
        
        logger.info(f"ExecutionMonitor initialized with {self.config.level.value} level")
    
    def _setup_logging(self):
        """Set up monitoring-specific logging."""
        if self.config.log_file:
            # Create file handler for monitoring logs
            file_handler = logging.FileHandler(self.config.log_file)
            file_handler.setLevel(logging.INFO)
            
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            
            # Add handler to logger
            monitor_logger = logging.getLogger('execution_monitor')
            monitor_logger.addHandler(file_handler)
            monitor_logger.setLevel(logging.INFO)
    
    def start_execution_monitoring(
        self,
        execution_id: str = None,
        docker_image: str = None,
        timeout: int = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Start monitoring an execution.
        
        Args:
            execution_id: Unique execution ID
            docker_image: Docker image being used
            timeout: Execution timeout
            metadata: Additional metadata
            
        Returns:
            Execution ID for tracking
        """
        if not execution_id:
            execution_id = str(uuid.uuid4())[:8]
        
        start_time = time.time()
        
        # Create metrics object
        metrics = ExecutionMetrics(
            execution_id=execution_id,
            start_time=start_time,
            docker_image=docker_image,
            timeout_seconds=timeout
        )
        
        self._active_executions[execution_id] = metrics
        
        # Start resource monitoring if enabled
        if self.config.enable_resource_monitoring and self.config.level != MonitoringLevel.MINIMAL:
            self._start_resource_monitoring(execution_id)
        
        # Log start
        self._log_event(execution_id, "EXECUTION_START", {
            "docker_image": docker_image,
            "timeout": timeout,
            "metadata": metadata or {}
        })
        
        return execution_id
    
    def update_execution_phase(self, execution_id: str, phase: ExecutionPhase, details: Dict[str, Any] = None):
        """
        Update the current execution phase.
        
        Args:
            execution_id: Execution ID
            phase: Current phase
            details: Phase-specific details
        """
        if execution_id not in self._active_executions:
            logger.warning(f"Execution {execution_id} not found for phase update")
            return
        
        metrics = self._active_executions[execution_id]
        current_time = time.time()
        
        # Record timing for previous phase
        if metrics.phase != ExecutionPhase.INITIALIZATION:
            prev_phase_duration = current_time - metrics.start_time
            for phase_name, duration in metrics.phase_timings.items():
                prev_phase_duration -= duration
            metrics.phase_timings[metrics.phase.value] = prev_phase_duration
        
        # Update to new phase
        metrics.phase = phase
        
        # Log phase change
        self._log_event(execution_id, f"PHASE_CHANGE", {
            "phase": phase.value,
            "details": details or {}
        })
    
    def record_security_issues(self, execution_id: str, issue_count: int):
        """Record security issues found during validation."""
        if execution_id in self._active_executions:
            self._active_executions[execution_id].security_issues = issue_count
            
            if issue_count > 0:
                self._log_event(execution_id, "SECURITY_ISSUES", {
                    "count": issue_count
                })
    
    def record_container_info(self, execution_id: str, container_id: str):
        """Record Docker container information."""
        if execution_id in self._active_executions:
            self._active_executions[execution_id].container_id = container_id
            
            self._log_event(execution_id, "CONTAINER_CREATED", {
                "container_id": container_id[:12]  # Short ID for logs
            })
    
    def record_execution_result(
        self,
        execution_id: str,
        success: bool,
        output_size: int = 0,
        error_message: str = None,
        exit_code: int = None
    ):
        """
        Record execution results.
        
        Args:
            execution_id: Execution ID
            success: Whether execution was successful
            output_size: Size of output in bytes
            error_message: Error message if failed
            exit_code: Process exit code
        """
        if execution_id not in self._active_executions:
            logger.warning(f"Execution {execution_id} not found for result recording")
            return
        
        metrics = self._active_executions[execution_id]
        metrics.success = success
        metrics.output_size_bytes = output_size
        metrics.error_message = error_message
        metrics.exit_code = exit_code
        
        # Update phase
        final_phase = ExecutionPhase.COMPLETED if success else ExecutionPhase.FAILED
        self.update_execution_phase(execution_id, final_phase)
        
        # Log result
        self._log_event(execution_id, "EXECUTION_RESULT", {
            "success": success,
            "output_size": output_size,
            "exit_code": exit_code,
            "error_message": error_message[:100] if error_message else None
        })
    
    def stop_execution_monitoring(self, execution_id: str) -> Optional[ExecutionMetrics]:
        """
        Stop monitoring an execution and return final metrics.
        
        Args:
            execution_id: Execution ID
            
        Returns:
            Final ExecutionMetrics or None if not found
        """
        if execution_id not in self._active_executions:
            logger.warning(f"Execution {execution_id} not found for stopping")
            return None
        
        metrics = self._active_executions[execution_id]
        metrics.end_time = time.time()
        
        # Stop resource monitoring
        if execution_id in self._stop_monitoring:
            self._stop_monitoring[execution_id].set()
        
        # Wait for monitoring thread to finish
        if execution_id in self._monitoring_threads:
            self._monitoring_threads[execution_id].join(timeout=1.0)
        
        # Final phase timing
        if metrics.phase != ExecutionPhase.COMPLETED and metrics.phase != ExecutionPhase.FAILED:
            current_time = time.time()
            prev_duration = current_time - metrics.start_time
            for duration in metrics.phase_timings.values():
                prev_duration -= duration
            metrics.phase_timings[metrics.phase.value] = prev_duration
        
        # Log completion
        self._log_event(execution_id, "EXECUTION_STOP", {
            "duration": metrics.get_total_duration(),
            "success": metrics.success,
            "phase_timings": metrics.phase_timings
        })
        
        # Save metrics if configured
        if self.config.metrics_file:
            self._save_metrics_to_file(metrics)
        
        # Cleanup
        if self.config.auto_cleanup:
            self._cleanup_execution(execution_id)
        
        return metrics
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of an execution."""
        if execution_id not in self._active_executions:
            return None
        
        metrics = self._active_executions[execution_id]
        
        return {
            "execution_id": execution_id,
            "phase": metrics.phase.value,
            "duration": metrics.get_total_duration(),
            "success": metrics.success,
            "docker_image": metrics.docker_image,
            "container_id": metrics.container_id,
            "security_issues": metrics.security_issues,
            "current_cpu_usage": metrics.cpu_usage_percent[-1] if metrics.cpu_usage_percent else None,
            "current_memory_usage": metrics.memory_usage_mb[-1] if metrics.memory_usage_mb else None
        }
    
    def get_all_active_executions(self) -> List[str]:
        """Get list of all active execution IDs."""
        return list(self._active_executions.keys())
    
    def _start_resource_monitoring(self, execution_id: str):
        """Start resource monitoring thread for execution."""
        stop_event = threading.Event()
        self._stop_monitoring[execution_id] = stop_event
        
        monitoring_thread = threading.Thread(
            target=self._resource_monitoring_loop,
            args=(execution_id, stop_event),
            daemon=True
        )
        
        self._monitoring_threads[execution_id] = monitoring_thread
        monitoring_thread.start()
    
    def _resource_monitoring_loop(self, execution_id: str, stop_event: threading.Event):
        """Resource monitoring loop running in separate thread."""
        metrics = self._active_executions[execution_id]
        
        while not stop_event.is_set():
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=None)
                metrics.cpu_usage_percent.append(cpu_percent)
                
                # Memory usage
                memory = psutil.virtual_memory()
                memory_mb = memory.used / (1024 * 1024)
                metrics.memory_usage_mb.append(memory_mb)
                
                # Disk I/O (if enabled)
                if self.config.enable_disk_monitoring:
                    disk_io = psutil.disk_io_counters()
                    if disk_io:
                        metrics.disk_io_bytes['read'] = disk_io.read_bytes
                        metrics.disk_io_bytes['write'] = disk_io.write_bytes
                
                # Network I/O (if enabled)
                if self.config.enable_network_monitoring:
                    net_io = psutil.net_io_counters()
                    if net_io:
                        metrics.network_io_bytes['sent'] = net_io.bytes_sent
                        metrics.network_io_bytes['recv'] = net_io.bytes_recv
                
                # Detailed logging for debug level
                if self.config.level == MonitoringLevel.DEBUG:
                    self._log_event(execution_id, "RESOURCE_SAMPLE", {
                        "cpu_percent": cpu_percent,
                        "memory_mb": memory_mb,
                        "timestamp": time.time()
                    })
            
            except Exception as e:
                logger.error(f"Resource monitoring error for {execution_id}: {str(e)}")
            
            # Wait for next sample
            stop_event.wait(timeout=self.config.sample_interval)
    
    def _log_event(self, execution_id: str, event_type: str, data: Dict[str, Any]):
        """Log a monitoring event."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "execution_id": execution_id,
            "event_type": event_type,
            "data": data
        }
        
        # Different logging based on level
        if self.config.level == MonitoringLevel.MINIMAL:
            if event_type in ["EXECUTION_START", "EXECUTION_STOP", "EXECUTION_RESULT"]:
                logger.info(f"[{execution_id}] {event_type}: {data}")
        
        elif self.config.level == MonitoringLevel.STANDARD:
            if event_type not in ["RESOURCE_SAMPLE"]:
                logger.info(f"[{execution_id}] {event_type}: {data}")
        
        elif self.config.level in [MonitoringLevel.DETAILED, MonitoringLevel.DEBUG]:
            logger.info(f"[{execution_id}] {event_type}: {data}")
        
        # Queue for potential external consumers
        try:
            self._metrics_queue.put_nowait(log_entry)
        except queue.Full:
            # Remove oldest entry and add new one
            try:
                self._metrics_queue.get_nowait()
                self._metrics_queue.put_nowait(log_entry)
            except queue.Empty:
                pass
    
    def _save_metrics_to_file(self, metrics: ExecutionMetrics):
        """Save metrics to file."""
        try:
            metrics_data = asdict(metrics)
            metrics_data['timestamp'] = datetime.utcnow().isoformat()
            
            # Append to metrics file
            with open(self.config.metrics_file, 'a', encoding='utf-8') as f:
                json.dump(metrics_data, f)
                f.write('\n')
                
        except Exception as e:
            logger.error(f"Failed to save metrics to file: {str(e)}")
    
    def _cleanup_execution(self, execution_id: str):
        """Clean up resources for an execution."""
        # Remove from active executions
        self._active_executions.pop(execution_id, None)
        
        # Clean up monitoring resources
        self._stop_monitoring.pop(execution_id, None)
        self._monitoring_threads.pop(execution_id, None)
    
    def generate_execution_report(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Generate comprehensive execution report."""
        if execution_id not in self._active_executions:
            return None
        
        metrics = self._active_executions[execution_id]
        
        # Calculate statistics
        avg_cpu = sum(metrics.cpu_usage_percent) / len(metrics.cpu_usage_percent) if metrics.cpu_usage_percent else 0
        max_cpu = max(metrics.cpu_usage_percent) if metrics.cpu_usage_percent else 0
        
        avg_memory = sum(metrics.memory_usage_mb) / len(metrics.memory_usage_mb) if metrics.memory_usage_mb else 0
        max_memory = max(metrics.memory_usage_mb) if metrics.memory_usage_mb else 0
        
        report = {
            "execution_id": execution_id,
            "summary": {
                "success": metrics.success,
                "total_duration": metrics.get_total_duration(),
                "docker_image": metrics.docker_image,
                "container_id": metrics.container_id,
                "security_issues": metrics.security_issues
            },
            "performance": {
                "avg_cpu_percent": round(avg_cpu, 2),
                "max_cpu_percent": round(max_cpu, 2),
                "avg_memory_mb": round(avg_memory, 2),
                "max_memory_mb": round(max_memory, 2),
                "output_size_bytes": metrics.output_size_bytes
            },
            "phase_timings": metrics.phase_timings,
            "io_stats": {
                "disk_io_bytes": metrics.disk_io_bytes,
                "network_io_bytes": metrics.network_io_bytes
            }
        }
        
        if metrics.error_message:
            report["error"] = {
                "message": metrics.error_message,
                "exit_code": metrics.exit_code
            }
        
        return report
    
    def get_recent_log_entries(self, count: int = 100) -> List[Dict[str, Any]]:
        """Get recent log entries from the metrics queue."""
        entries = []
        
        # Drain the queue
        while not self._metrics_queue.empty() and len(entries) < count:
            try:
                entry = self._metrics_queue.get_nowait()
                entries.append(entry)
            except queue.Empty:
                break
        
        return entries[-count:] if entries else []


# Convenience functions
def create_standard_monitor(log_file: Path = None) -> ExecutionMonitor:
    """Create a standard execution monitor."""
    config = MonitoringConfig(
        level=MonitoringLevel.STANDARD,
        log_file=log_file,
        sample_interval=2.0
    )
    return ExecutionMonitor(config)


def create_debug_monitor(log_file: Path = None, metrics_file: Path = None) -> ExecutionMonitor:
    """Create a debug-level execution monitor."""
    config = MonitoringConfig(
        level=MonitoringLevel.DEBUG,
        log_file=log_file,
        metrics_file=metrics_file,
        sample_interval=0.5
    )
    return ExecutionMonitor(config)


def create_minimal_monitor() -> ExecutionMonitor:
    """Create a minimal execution monitor."""
    config = MonitoringConfig(
        level=MonitoringLevel.MINIMAL,
        enable_resource_monitoring=False
    )
    return ExecutionMonitor(config)