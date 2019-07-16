import logging
import zipfile
import urllib.request

from tqdm import tqdm

logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    # filename='log.log'
)


# https://stackoverflow.com/a/53877507
class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download_file(url):
    output_path = url.split('/')[-1]
    try:
        with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=output_path) as t:
            urllib.request.urlretrieve(url, filename=output_path, reporthook=t.update_to)
        return output_path
    except Exception as e:
        logger.error(e)


def extract_zipfile(archive):
    with zipfile.ZipFile(archive, "r") as zip_ref:
        zip_ref.extractall("downloads")


if __name__ == '__main__':
    r = download_file("http://dvmn.org/media/modules_dist/quiz-questions.zip")
    extract_zipfile(r)

