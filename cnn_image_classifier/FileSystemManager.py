import os
import tarfile
import shutil
import logging
from urllib.request import urlretrieve
from progressbar import ProgressBar, Percentage, Bar


class FileSystemManager:

    def __init__(self, source_data, download_url, model_dir, source_dir):
        self.source_data = source_data
        self.download_url = download_url
        self.model_dir = model_dir
        self.archive_dir = None
        self.source_dir = source_dir

    def clean_run(self):
        """Remove model and data dirs for a clean run"""

        for directory in [self.model_dir, self.source_dir]:
            if directory:
                if os.path.exists(directory):
                    try:
                        logging.info("Removing resource: Directory [%s].", directory)
                        shutil.rmtree(directory)
                    except OSError:
                        logging.error("Could not remove resource: Directory [%s].", directory)

    def download(self):
        """Download data if not present on local FileSystem"""

        def progress(count, blockSize, totalSize):
            pbar.update(int(count * blockSize * 100 / totalSize))

        download_url = self.download_url + '/' + self.source_data

        if not os.path.exists(self.source_data):
            logging.info(
                "%s not found on local filesystem. File will be downloaded from %s.", self.source_data, download_url)

            pbar = ProgressBar(widgets=[Percentage(), Bar()])
            urlretrieve(download_url, self.source_data, reporthook=progress)

    def extract(self):
        """Extract compressed archives tar.gz"""

        self.archive_dir = self.source_data.split('.')[0]

        if not os.path.exists(self.archive_dir):
            logging.info("Extracting archive %s to %s", self.source_data, self.archive_dir)

            if self.source_data.lower().endswith('.tar.gz'):
                tar = tarfile.open(self.source_data, "r:gz")
            tar.extractall()
            tar.close()

    def clean_files(self, extension):
        """Removes all files not ending in extension"""

        for root, dirs, files in os.walk(self.source_dir):
            for current_file in files:
                if not current_file.lower().endswith(extension):
                    try:
                        logging.debug("Removing resource: File [%s]", current_file)
                        os.remove(os.path.join(root, current_file))
                    except OSError:
                        logging.error("Could not remove resource: File [%s]", current_file)

    def flatten(self):
        """Flattens directory tree to single level"""

        os.mkdir(self.source_dir)

        for dirpath, dirnames, filenames in os.walk(self.archive_dir):
            for filename in filenames:

                try:
                    logging.debug("Moving %s from %s to %s", filename, dirpath, self.source_dir)
                    os.rename(os.path.join(dirpath, filename), os.path.join(self.source_dir, filename))

                except OSError:
                    logging.error("Could not move %s ", os.path.join(dirpath, filename))

        try:
            logging.info("Removing resource: Directory [%s].", self.archive_dir)
            shutil.rmtree(self.archive_dir)
        except OSError:
            logging.error("Could not remove resource: Directory [%s].", self.archive_dir)
