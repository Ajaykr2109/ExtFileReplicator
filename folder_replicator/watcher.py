import time
import threading
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger("FolderReplicator")


class ReplicationHandler(FileSystemEventHandler):
    def __init__(self, synchronizer, replication):
        super().__init__()
        self.synchronizer = synchronizer
        self.replication = replication
        self.debounce_interval = 2  # seconds
        self.last_event_time = 0

    def on_modified(self, event):
        current_time = time.time()
        if not event.is_directory and (current_time - self.last_event_time) > self.debounce_interval:
            logger.info(f"Detected modification: {event.src_path}")
            self.synchronizer.sync_replication(self.replication)
            self.last_event_time = current_time

    def on_created(self, event):
        if not event.is_directory:
            logger.info(f"Detected new file: {event.src_path}")
            self.synchronizer.sync_replication(self.replication)

    def on_deleted(self, event):
        logger.info(f"Detected deletion: {event.src_path}")
        self.synchronizer.sync_replication(self.replication)

    def on_moved(self, event):
        logger.info(f"Detected move: {event.src_path} → {event.dest_path}")
        self.synchronizer.sync_replication(self.replication)


class ReplicationWatcher:
    def __init__(self, synchronizer, interval_minutes=60):
        self.synchronizer = synchronizer
        self.observers = []
        self.interval = interval_minutes * 60
        self.stop_event = threading.Event()

    def watch(self):
        try:

            for replication in self.synchronizer.config_manager.get_replications():
                observer = Observer()
                handler = ReplicationHandler(self.synchronizer, replication)
                observer.schedule(
                    handler, replication['source'], recursive=True)
                observer.start()
                self.observers.append(observer)
                logger.info(f"Watching for changes: {replication['source']}")

            sync_thread = threading.Thread(target=self._periodic_sync)
            sync_thread.daemon = True
            sync_thread.start()

            logger.info("Press Ctrl+C to stop watching...")
            while not self.stop_event.is_set():
                time.sleep(1)

        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            logger.error(f"Error in watch mode: {str(e)}", exc_info=True)
            self.stop()

    def _periodic_sync(self):
        while not self.stop_event.is_set():
            logger.info(
                f"Running periodic sync (every {self.interval//60} minutes)")
            self.synchronizer.sync_all()

            for _ in range(self.interval):
                if self.stop_event.is_set():
                    break
                time.sleep(1)

    def stop(self):
        logger.info("Stopping watchers and sync threads")
        self.stop_event.set()
        for observer in self.observers:
            observer.stop()
        for observer in self.observers:
            observer.join()
