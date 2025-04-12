import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QLineEdit,
                             QTextEdit, QFileDialog, QSystemTrayIcon, QMenu,
                             QCheckBox, QMessageBox, QScrollArea, QStatusBar,
                             QListWidget, QListWidgetItem, QTabWidget, QGroupBox, QComboBox, QSpinBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QMutex, QMutexLocker
from PyQt6.QtGui import QIcon, QAction
import qdarkstyle
from folder_replicator.config_manager import ConfigManager
from folder_replicator.synchronization import Synchronizer
from folder_replicator.watcher import ReplicationWatcher
from folder_replicator.logger import setup_logger
import logging


class LogHandler(logging.Handler):
    def __init__(self, signal):
        super().__init__()
        self.signal = signal

    def emit(self, record):
        msg = self.format(record)
        self.signal.emit(msg)


class SyncWorker(QThread):
    progress = pyqtSignal(str)
    error = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, synchronizer, replication):
        super().__init__()
        self.synchronizer = synchronizer
        self.replication = replication
        self._is_running = True
        self._mutex = QMutex()

    def run(self):
        try:
            with QMutexLocker(self._mutex):
                if not self._is_running:
                    return

            self.synchronizer.sync_replication(self.replication)
            self.progress.emit("Synchronization completed successfully")

        except Exception as e:
            self.error.emit(f"Error during synchronization: {str(e)}")
        finally:
            with QMutexLocker(self._mutex):
                self._is_running = False
            self.finished.emit()

    def stop(self):
        with QMutexLocker(self._mutex):
            self._is_running = False
        self.wait()  # Wait for the thread to finish


class WatchWorker(QThread):
    status = pyqtSignal(str)

    def __init__(self, watcher):
        super().__init__()
        self.watcher = watcher
        self.is_running = True

    def run(self):
        try:
            self.watcher.watch()
        except Exception as e:
            self.status.emit(f"Watch error: {str(e)}")

    def stop(self):
        self.is_running = False
        self.watcher.stop()


class MainWindow(QMainWindow):
    log_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ExtFileReplicator")
        self.setMinimumSize(1000, 700)

        self.config_manager = ConfigManager()
        self.logger = setup_logger(self.config_manager)
        self.synchronizer = Synchronizer(self.config_manager)
        self.watch_worker = None

        # Create status bar first
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        self.setup_ui()
        self.setup_logging()
        self.setup_tray()
        self.load_replications()
        self.load_config()

        # Apply dark style
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left panel for replications list and status
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Replications list
        self.replications_list = QListWidget()
        self.replications_list.itemClicked.connect(self.replication_selected)
        left_layout.addWidget(QLabel("Existing Replications:"))
        left_layout.addWidget(self.replications_list)

        # Status view
        status_group = QGroupBox("Replication Status")
        status_layout = QVBoxLayout()
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        status_layout.addWidget(self.status_text)
        status_group.setLayout(status_layout)
        left_layout.addWidget(status_group)

        main_layout.addWidget(left_panel)

        # Center panel with tabs
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)

        # Create tab widget
        tab_widget = QTabWidget()

        # Basic tab
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)

        # Source directory selection
        source_layout = QHBoxLayout()
        self.source_input = QLineEdit()
        source_btn = QPushButton("Browse Source")
        source_btn.clicked.connect(
            lambda: self.browse_directory(self.source_input))
        source_layout.addWidget(QLabel("Source:"))
        source_layout.addWidget(self.source_input)
        source_layout.addWidget(source_btn)
        basic_layout.addLayout(source_layout)

        # Destination directory selection
        dest_layout = QHBoxLayout()
        self.dest_input = QLineEdit()
        dest_btn = QPushButton("Browse Destination")
        dest_btn.clicked.connect(
            lambda: self.browse_directory(self.dest_input))
        dest_layout.addWidget(QLabel("Destination:"))
        dest_layout.addWidget(self.dest_input)
        dest_layout.addWidget(dest_btn)
        basic_layout.addLayout(dest_layout)

        # Exclusion patterns
        exclusion_layout = QHBoxLayout()
        self.exclusion_input = QLineEdit()
        self.exclusion_input.setPlaceholderText("*.tmp *.log cache/")
        exclusion_layout.addWidget(QLabel("Exclusions:"))
        exclusion_layout.addWidget(self.exclusion_input)
        basic_layout.addLayout(exclusion_layout)

        # Basic options
        options_layout = QHBoxLayout()
        self.auto_sync = QCheckBox("Auto-sync on startup")
        self.use_hash = QCheckBox("Use file hash comparison")
        self.minimize_to_tray = QCheckBox("Minimize to tray")
        options_layout.addWidget(self.auto_sync)
        options_layout.addWidget(self.use_hash)
        options_layout.addWidget(self.minimize_to_tray)
        basic_layout.addLayout(options_layout)

        # Action buttons
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Replication")
        self.sync_btn = QPushButton("Sync Selected")
        self.sync_all_btn = QPushButton("Sync All")
        self.watch_btn = QPushButton("Start Watching")
        self.add_btn.clicked.connect(self.add_replication)
        self.sync_btn.clicked.connect(self.sync_selected)
        self.sync_all_btn.clicked.connect(self.sync_all)
        self.watch_btn.clicked.connect(self.toggle_watch)
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.sync_btn)
        button_layout.addWidget(self.sync_all_btn)
        button_layout.addWidget(self.watch_btn)
        basic_layout.addLayout(button_layout)

        # Advanced tab
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)

        # Log level selection
        log_group = QGroupBox("Logging Configuration")
        log_layout = QVBoxLayout()

        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(['DEBUG', 'INFO', 'WARNING', 'ERROR'])
        self.log_level_combo.currentTextChanged.connect(self.update_log_level)
        log_level_layout = QHBoxLayout()
        log_level_layout.addWidget(QLabel("Log Level:"))
        log_level_layout.addWidget(self.log_level_combo)
        log_layout.addLayout(log_level_layout)

        # Max log size
        self.max_log_size = QSpinBox()
        self.max_log_size.setRange(1, 1000)
        self.max_log_size.setSuffix(" MB")
        self.max_log_size.valueChanged.connect(self.update_max_log_size)
        max_log_layout = QHBoxLayout()
        max_log_layout.addWidget(QLabel("Max Log Size:"))
        max_log_layout.addWidget(self.max_log_size)
        log_layout.addLayout(max_log_layout)

        # Clear logs button
        clear_logs_btn = QPushButton("Clear Logs")
        clear_logs_btn.clicked.connect(self.clear_logs)
        log_layout.addWidget(clear_logs_btn)

        log_group.setLayout(log_layout)
        advanced_layout.addWidget(log_group)

        # Sync interval configuration
        sync_group = QGroupBox("Sync Configuration")
        sync_layout = QVBoxLayout()

        self.sync_interval = QSpinBox()
        self.sync_interval.setRange(1, 1440)
        self.sync_interval.setSuffix(" minutes")
        self.sync_interval.valueChanged.connect(self.update_sync_interval)
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Sync Interval:"))
        interval_layout.addWidget(self.sync_interval)
        sync_layout.addLayout(interval_layout)

        sync_group.setLayout(sync_layout)
        advanced_layout.addWidget(sync_group)

        advanced_layout.addStretch()

        # Add tabs
        tab_widget.addTab(basic_tab, "Basic")
        tab_widget.addTab(advanced_tab, "Advanced")
        center_layout.addWidget(tab_widget)

        main_layout.addWidget(center_panel)

        # Right panel for detailed logging
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Activity Log viewer
        activity_group = QGroupBox("Activity Log")
        activity_layout = QVBoxLayout()
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        activity_layout.addWidget(self.log_viewer)
        activity_group.setLayout(activity_layout)

        # Detailed Log viewer
        detailed_group = QGroupBox("Detailed Log")
        detailed_layout = QVBoxLayout()
        self.detailed_log_viewer = QTextEdit()
        self.detailed_log_viewer.setReadOnly(True)
        detailed_layout.addWidget(self.detailed_log_viewer)
        detailed_group.setLayout(detailed_layout)

        right_layout.addWidget(activity_group)
        right_layout.addWidget(detailed_group)
        right_layout.setStretch(0, 1)  # Activity log
        right_layout.setStretch(1, 1)  # Detailed log

        main_layout.addWidget(right_panel)

        # Set stretch factors for panels
        main_layout.setStretch(0, 1)   # Left panel
        main_layout.setStretch(1, 2)   # Center panel
        main_layout.setStretch(2, 1)   # Right panel

    def setup_logging(self):
        gui_handler = LogHandler(self.log_signal)
        gui_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(gui_handler)
        self.log_signal.connect(self.update_log)

    def load_replications(self):
        self.replications_list.clear()
        replications = self.config_manager.get_replications()
        for rep in replications:
            item = QListWidgetItem(f"{rep['source']} → {rep['destination']}")
            item.setData(Qt.ItemDataRole.UserRole, rep)
            self.replications_list.addItem(item)

        has_items = len(replications) > 0
        self.sync_btn.setEnabled(has_items)
        self.sync_all_btn.setEnabled(has_items)
        self.watch_btn.setEnabled(has_items)

    def load_config(self):
        config = self.config_manager.get_config()
        self.log_level_combo.setCurrentText(str(config['log_level']))
        self.max_log_size.setValue(int(config['max_log_size']))
        self.sync_interval.setValue(int(config['sync_interval']))
        self.update_status()  # Update status view to show new config

    def update_log_level(self, level):
        if self.config_manager.set_config('log_level', level):
            self.logger = setup_logger(self.config_manager)
            self.log_signal.emit(f"Log level changed to {level}")
            self.update_status()  # Refresh status view

    def update_max_log_size(self, size):
        if self.config_manager.set_config('max_log_size', size):
            self.log_signal.emit(f"Max log size changed to {size} MB")
            self.update_status()  # Refresh status view

    def update_sync_interval(self, interval):
        if self.config_manager.set_config('sync_interval', interval):
            self.log_signal.emit(
                f"Sync interval changed to {interval} minutes")
            self.update_status()  # Refresh status view

    def clear_logs(self):
        try:
            log_file = self.config_manager.get_log_file()
            with open(log_file, 'w'):
                pass
            self.log_viewer.clear()
            self.log_signal.emit("Logs cleared successfully")
        except Exception as e:
            QMessageBox.warning(
                self, "Error", f"Failed to clear logs: {str(e)}")

    def add_replication(self):
        source = self.source_input.text()
        destination = self.dest_input.text()
        exclusions = [x.strip()
                      for x in self.exclusion_input.text().split() if x.strip()]

        if not source or not destination:
            QMessageBox.warning(
                self, "Error", "Please select both source and destination directories")
            return

        try:
            if self.config_manager.add_replication(source, destination, exclusions):
                self.log_signal.emit(
                    f"Added replication: {source} -> {destination}")
                if exclusions:
                    self.log_signal.emit(
                        f"Exclusions: {', '.join(exclusions)}")
                self.load_replications()
                self.source_input.clear()
                self.dest_input.clear()
                self.exclusion_input.clear()
            else:
                QMessageBox.warning(self, "Error", "Failed to add replication")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def update_status(self, replication=None):
        if replication is None:
            current_item = self.replications_list.currentItem()
            if not current_item:
                self.status_text.clear()
                return
            replication = current_item.data(Qt.ItemDataRole.UserRole)

        status = self.synchronizer.check_status(replication)
        config = self.config_manager.get_config()
        log_file = self.config_manager.get_log_file()

        # Basic replication status
        status_text = f"Replication Status\n{'='*50}\n"
        status_text += f"Source: {replication['source']}\n"
        status_text += f"Destination: {replication['destination']}\n"
        status_text += f"Last sync: {status['last_sync']}\n"
        status_text += f"Source files: {status['source_files']}\n"
        status_text += f"Destination files: {status['dest_files']}\n"
        status_text += f"Pending changes: {status['pending_changes']}\n"
        if status['errors']:
            status_text += f"Errors: {status['errors']}\n"
        if replication.get('exclusions'):
            status_text += f"Exclusions: {', '.join(replication['exclusions'])}\n"

        # Logging configuration
        status_text += f"\nLogging Configuration\n{'='*50}\n"
        status_text += f"Log Level: {config['log_level']}\n"
        status_text += f"Max Log Size: {config['max_log_size']} MB\n"
        status_text += f"Sync Interval: {config['sync_interval']} minutes\n"
        status_text += f"Log Directory: {self.config_manager.get_log_dir()}\n"
        status_text += f"Current Log File: {log_file}\n"

        self.status_text.setText(status_text)
        self.update_detailed_log()

    def update_detailed_log(self):
        try:
            log_file = self.config_manager.get_log_file()
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    self.detailed_log_viewer.setText(f.read())
                    detailed_scroll_bar = self.detailed_log_viewer.verticalScrollBar()
                    if detailed_scroll_bar is not None:
                        detailed_scroll_bar.setValue(
                            detailed_scroll_bar.maximum())
            else:
                self.detailed_log_viewer.setText("No log entries found.")
        except Exception as e:
            self.detailed_log_viewer.setText(
                f"Error reading log file: {str(e)}")

    def update_log(self, message):
        if "Synchronization completed successfully" in message:
            self.log_viewer.append(message)
            log_scroll_bar = self.log_viewer.verticalScrollBar()
            if log_scroll_bar is not None:
                log_scroll_bar.setValue(log_scroll_bar.maximum())
        self.update_detailed_log()  # Update detailed log when new messages arrive

    def replication_selected(self, item):
        rep_data = item.data(Qt.ItemDataRole.UserRole)
        self.source_input.setText(rep_data['source'])
        self.dest_input.setText(rep_data['destination'])
        if rep_data.get('exclusions'):
            self.exclusion_input.setText(' '.join(rep_data['exclusions']))
        self.update_status(rep_data)

    def sync_selected(self):
        current_item = self.replications_list.currentItem()
        if not current_item:
            QMessageBox.warning(
                self, "Error", "Please select a replication to sync")
            return

        # Clean up previous worker if exists
        if hasattr(self, '_sync_worker'):
            self._sync_worker.stop()
            self._sync_worker.wait()
            self._sync_worker.deleteLater()

        self.sync_btn.setEnabled(False)
        self.sync_all_btn.setEnabled(False)
        self.status_bar.showMessage("Synchronizing selected replication...")

        rep_data = current_item.data(Qt.ItemDataRole.UserRole)
        self._sync_worker = SyncWorker(self.synchronizer, rep_data)
        self._sync_worker.progress.connect(self.update_log)
        self._sync_worker.error.connect(self.handle_sync_error)
        self._sync_worker.finished.connect(self.sync_completed)
        self._sync_worker.start()

    def sync_all(self):
        # Clean up previous sync worker if exists
        if hasattr(self, '_sync_worker'):
            self._sync_worker.stop()
            self._sync_worker.wait()
            self._sync_worker.deleteLater()

        self.sync_btn.setEnabled(False)
        self.sync_all_btn.setEnabled(False)
        self.status_bar.showMessage("Synchronizing all replications...")

        replications = self.config_manager.get_replications()
        if not replications:
            QMessageBox.warning(self, "Error", "No replications configured")
            self.sync_completed()
            return

        self.current_sync_index = 0
        self.sync_next_replication()

    def sync_next_replication(self):
        replications = self.config_manager.get_replications()
        if self.current_sync_index >= len(replications):
            self.sync_completed()
            return

        rep = replications[self.current_sync_index]
        self._sync_worker = SyncWorker(self.synchronizer, rep)
        self._sync_worker.progress.connect(self.update_log)
        self._sync_worker.error.connect(self.handle_sync_error)
        self._sync_worker.finished.connect(self._continue_sync)
        self.status_bar.showMessage(
            f"Synchronizing {rep['source']} → {rep['destination']}")
        self._sync_worker.start()

    def _continue_sync(self):
        if hasattr(self, '_sync_worker'):
            self._sync_worker.wait()
            self._sync_worker.deleteLater()
            delattr(self, '_sync_worker')

        self.current_sync_index += 1
        self.sync_next_replication()

    def handle_sync_error(self, error_msg):
        QMessageBox.warning(self, "Synchronization Error",
                            f"Error during synchronization: {error_msg}")
        self.status_bar.showMessage("Synchronization failed")
        self.sync_completed()

    def sync_completed(self):
        if hasattr(self, '_sync_worker'):
            self._sync_worker.stop()
            self._sync_worker.wait()
            self._sync_worker.deleteLater()
            delattr(self, '_sync_worker')

        self.sync_btn.setEnabled(True)
        self.sync_all_btn.setEnabled(True)
        self.status_bar.showMessage("Synchronization completed")
        self.load_replications()

    def browse_directory(self, line_edit):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            line_edit.setText(directory)

    def toggle_watch(self):
        if self.watch_worker and self.watch_worker.is_running:
            self.watch_worker.stop()
            self.watch_btn.setText("Start Watching")
            self.status_bar.showMessage("Watch stopped")
        else:
            self.watch_btn.setText("Stop Watching")
            self.watch_worker = WatchWorker(
                ReplicationWatcher(self.synchronizer, interval_minutes=1)
            )
            self.watch_worker.status.connect(self.update_log)
            self.watch_worker.start()
            self.status_bar.showMessage("Watching for changes...")

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        icon = QIcon.fromTheme(
            "document-save", QIcon.fromTheme("drive-harddisk"))
        self.tray_icon.setIcon(icon)

        tray_menu = QMenu()
        show_action = QAction("Show", self)
        quit_action = QAction("Exit", self)
        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(self.close_application)

        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def closeEvent(self, event):
        # Clean up any running sync workers
        if hasattr(self, '_sync_worker'):
            self._sync_worker.stop()
            self._sync_worker.wait()
            self._sync_worker.deleteLater()

        if self.minimize_to_tray.isChecked() and event.spontaneous():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "ExtFileReplicator",
                "Application minimized to tray",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
        else:
            self.close_application()

    def close_application(self):
        if self.watch_worker:
            self.watch_worker.stop()
        self.tray_icon.hide()
        QApplication.quit()


def run_gui():
    """Entry point for the GUI application"""
    try:
        # Ensure only one instance
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        try:
            import qdarkstyle
            if isinstance(app, QApplication):
                app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
        except ImportError:
            print("QDarkStyle not found. Using default style.")
        except Exception as e:
            print(f"Error loading dark style: {e}")

        window = MainWindow()
        window.show()
        return app.exec()
    except Exception as e:
        print(f"Error launching GUI: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(run_gui())
