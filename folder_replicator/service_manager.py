import os
import sys
import time
import logging
import platform
import threading
from pathlib import Path
from .config_manager import ConfigManager
from .synchronization import Synchronizer
from .watcher import ReplicationWatcher

logger = logging.getLogger("FolderReplicator")


class ServiceManager:
    def __init__(self, interval_minutes=60):
        self.interval = interval_minutes
        self.stop_event = threading.Event()
        self.config_manager = ConfigManager()
        self.synchronizer = Synchronizer(self.config_manager)
        self.setup_logging()

    def setup_logging(self):
        """Configure logging for the service"""
        log_dir = os.path.expanduser('~/.frep/logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'frep_service.log')

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

    def run_as_service(self):
        """Run as a background service/daemon"""
        try:
            if platform.system() == 'Windows':
                self._run_windows_service()
            else:
                self._run_unix_daemon()
        except Exception as e:
            logger.error(f"Service error: {e}", exc_info=True)
        finally:
            logger.info("Service stopped")

    def _run_windows_service(self):
        """Windows service implementation"""
        try:
            import win32serviceutil
            import win32service
            import win32event
            import servicemanager

            class FRService(win32serviceutil.ServiceFramework):
                _svc_name_ = "FolderReplicatorService"
                _svc_display_name_ = "Folder Replicator Service"

                def __init__(self, args):
                    win32serviceutil.ServiceFramework.__init__(self, args)
                    self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
                    self.service_manager = ServiceManager()

                def SvcStop(self):
                    self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
                    self.service_manager.stop()
                    win32event.SetEvent(self.hWaitStop)

                def SvcDoCommand(self):
                    self.service_manager._run_watcher()

            if '--install' in sys.argv:
                win32serviceutil.HandleCommandLine(FRService)
            else:
                self._run_watcher()

        except ImportError:
            logger.warning("pywin32 not installed, running in simple mode")
            self._run_watcher()

    def _run_unix_daemon(self):
        """Unix daemon implementation"""
        try:
            import daemon
            from daemon.pidfile import TimeoutPIDLockFile

            pid_dir = os.path.expanduser('~/.frep')
            os.makedirs(pid_dir, exist_ok=True)
            pid_file = os.path.join(pid_dir, 'frep.pid')

            context = daemon.DaemonContext(
                pidfile=TimeoutPIDLockFile(pid_file),
                stdout=sys.stdout,
                stderr=sys.stderr,
                working_directory=os.getcwd(),
                files_preserve=[
                    handler.stream for handler in logging.root.handlers]
            )

            with context:
                self._run_watcher()

        except ImportError:
            logger.warning(
                "python-daemon not installed, running in simple mode")
            self._run_watcher()

    def _run_watcher(self):
        """Start the watcher with existing ReplicationWatcher class"""
        watcher = ReplicationWatcher(self.synchronizer, self.interval)
        try:
            watcher.watch()
        except KeyboardInterrupt:
            watcher.stop()
        except Exception as e:
            logger.error(f"Watcher error: {e}", exc_info=True)
            watcher.stop()

    def stop(self):
        """Stop the service"""
        self.stop_event.set()
        logger.info("Service stop requested")


if __name__ == "__main__":
    service = ServiceManager()
    service.run_as_service()
