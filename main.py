import os
import zipfile
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QProgressBar, QFileDialog, QLabel
from PyQt5.QtCore import QThread, pyqtSignal

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}

class Worker(QThread):
    progress = pyqtSignal(int, str)
    
    def __init__(self, path):
        super().__init__()
        self.path = path
    
    def run(self):
        folders = [d for d in Path(self.path).rglob('*') if d.is_dir()]
        total_folders = len(folders)
        for idx, folder in enumerate(folders, 1):
            self.process_folder(folder)
            self.progress.emit(idx * 100 // total_folders, str(folder))

    def process_folder(self, folder):
        images = [f for f in folder.iterdir() if f.suffix.lower() in IMAGE_EXTENSIONS]

        if not images:
            return

        cbz_path = folder.with_suffix('.cbz')
        if cbz_path.exists():
            return

        with zipfile.ZipFile(str(cbz_path), 'w', zipfile.ZIP_DEFLATED) as zipf:
            for image in images:
                zipf.write(str(image), image.name)

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('cbz_auto_zipper')
        layout = QVBoxLayout()

        self.progress_label = QLabel('')
        layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        btn = QPushButton('Choose Directory', self)
        btn.clicked.connect(self.choose_directory)
        layout.addWidget(btn)

        self.setLayout(layout)

    def choose_directory(self):
        path = QFileDialog.getExistingDirectory(self, 'Choose Directory to Process Images')
        if path:
            self.worker = Worker(path)
            self.worker.progress.connect(self.update_progress)
            self.worker.start()

    def update_progress(self, progress, folder):
        self.progress_bar.setValue(progress)
        self.progress_label.setText(f'Processing: {folder}')

if __name__ == '__main__':
    app = QApplication([])
    window = App()
    window.show()
    app.exec_()