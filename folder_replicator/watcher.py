import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class ReplicationHandler(FileSystemEventHandler):
    """Handles filesystem events for replication"""

    def __init__(self, synchronizer, replication):
        super().__init__()
        self.synchronizer = synchronizer
        self.replication = replication
        self.debounce_interval = 2  # seconds
        self.last_event_time = 0

    def on_modified(self, event):
        """Handle file modification events"""
        current_time = time.time()
        if not event.is_directory and (current_time - self.last_event_time) > self.debounce_interval:
            print(f"\nDetected modification: {event.src_path}")
            self.synchronizer.sync_replication(self.replication)
            self.last_event_time = current_time

    def on_created(self, event):
        """Handle file creation events"""
        if not event.is_directory:
            print(f"\nDetected new file: {event.src_path}")
            self.synchronizer.sync_replication(self.replication)

    def on_deleted(self, event):
        """Handle file deletion events"""
        print(f"\nDetected deletion: {event.src_path}")
        self.synchronizer.sync_replication(self.replication)

    def on_moved(self, event):
        """Handle file move/rename events"""
        print(f"\nDetected move: {event.src_path} → {event.dest_path}")
        self.synchronizer.sync_replication(self.replication)


class ReplicationWatcher:
    def __init__(self, synchronizer, interval_minutes=60):
        self.synchronizer = synchronizer
        self.observers = []
        self.interval = interval_minutes * 60  # Convert to seconds
        self.stop_event = threading.Event()

    def watch(self):
        """Start watching with periodic sync"""
        try:
            # Start filesystem watchers
            for replication in self.synchronizer.config_manager.get_replications():
                observer = Observer()
                handler = ReplicationHandler(self.synchronizer, replication)
                observer.schedule(
                    handler, replication['source'], recursive=True)
                observer.start()
                self.observers.append(observer)
                print(f"Watching for changes: {replication['source']}")

            # Start periodic sync thread
            sync_thread = threading.Thread(target=self._periodic_sync)
            sync_thread.daemon = True
            sync_thread.start()

            print("\nPress Ctrl+C to stop watching...")
            while not self.stop_event.is_set():
                time.sleep(1)

        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            print(f"Error in watch mode: {e}")
            self.stop()

    def _periodic_sync(self):
        """Run periodic synchronization"""
        while not self.stop_event.is_set():
            print(
                f"\nRunning periodic sync (every {self.interval//60} minutes)...")
            self.synchronizer.sync_all()

            # Wait for interval or until stopped
            for _ in range(self.interval):
                if self.stop_event.is_set():
                    break
                time.sleep(1)

    def stop(self):
        """Stop all watchers and sync threads"""
        print("\nStopping watchers and sync threads...")
        self.stop_event.set()
        for observer in self.observers:
            observer.stop()
        for observer in self.observers:
            observer.join()
