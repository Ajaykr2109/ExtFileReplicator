import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class ReplicationWatcher:
    def __init__(self, synchronizer):
        self.synchronizer = synchronizer
        self.observers = []

    def watch(self):
        """Start watching all configured replications"""
        try:
            for replication in self.synchronizer.config_manager.get_replications():
                observer = Observer()
                handler = ReplicationHandler(self.synchronizer, replication)
                observer.schedule(
                    handler, replication['source'], recursive=True)
                observer.start()
                self.observers.append(observer)
                print(f"Watching for changes: {replication['source']}")

            print("\nPress Ctrl+C to stop watching...")
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            print(f"Error in watch mode: {e}")
            self.stop()

    def stop(self):
        """Stop all watchers"""
        print("\nStopping watchers...")
        for observer in self.observers:
            observer.stop()
        for observer in self.observers:
            observer.join()


class ReplicationHandler(FileSystemEventHandler):
    def __init__(self, synchronizer, replication):
        self.synchronizer = synchronizer
        self.replication = replication

    def on_modified(self, event):
        if not event.is_directory:
            print(f"Detected modification: {event.src_path}")
            self.synchronizer.sync_replication(self.replication)

    def on_created(self, event):
        print(f"Detected new item: {event.src_path}")
        self.synchronizer.sync_replication(self.replication)

    def on_deleted(self, event):
        print(f"Detected deletion: {event.src_path}")
        self.synchronizer.sync_replication(self.replication)

    def on_moved(self, event):
        print(f"Detected move: {event.src_path} → {event.dest_path}")
        self.synchronizer.sync_replication(self.replication)
