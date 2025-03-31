import os
import sys
import time
import logging
import platform
from threading import Event
from .watcher import ReplicationWatcher
from .config_manager import ConfigManager
from .synchronization import Synchronizer


class ServiceManager:
    def __init__(self, interval_minutes=1):
        self.interval = interval_minutes * 60
        self.stop_event = Event()
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
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('frep_service')

    def run(self):
        """Main service loop"""
        self.logger.info("Starting Folder Replicator service")

        try:
            self.synchronizer.sync_all()
            watcher = ReplicationWatcher(self.synchronizer)

            if platform.system() == 'Windows':
                self._windows_service_loop(watcher)
            else:
                self._unix_service_loop(watcher)

        except Exception as e:
            self.logger.error(f"Service error: {e}", exc_info=True)
        finally:
            self.logger.info("Service stopped")

    def _windows_service_loop(self, watcher):
        """Windows-specific service loop"""
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
                    self.service_manager.stop_event.set()
                    win32event.SetEvent(self.hWaitStop)

                def SvcDoCommand(self):
                    self.service_manager.run()

            if len(sys.argv) > 1 and sys.argv[1] == '--install':
                win32serviceutil.HandleCommandLine(FRService)
            else:
                watcher.watch()

        except ImportError:
            self.logger.warning(
                "pywin32 not installed, running in simple mode")
            watcher.watch()

    def _unix_service_loop(self, watcher):
        """Unix-like system service loop"""
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
                working_directory=os.getcwd()
            )

            with context:
                watcher.watch()

        except ImportError:
            self.logger.warning(
                "python-daemon not installed, running in simple mode")
            watcher.watch()

    def stop(self):
        """Stop the service"""
        self.stop_event.set()
