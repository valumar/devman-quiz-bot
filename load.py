import requests
import shutil
import logging
import zipfile


logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    # filename='log.log'
)


def download_file(url):
    local_filename = url.split('/')[-1]
    try:
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            with open(local_filename, 'wb') as f:
                shutil.copyfileobj(response.raw, f)
        return local_filename
    except Exception as e:
        logger.error(e)

def extract_zipfile(archive):
    with zipfile.ZipFile(archive, "r") as zip_ref:
        zip_ref.extractall("downloads")


if __name__ == '__main__':
    # r = download_file("http://dvmn.org/media/modules_dist/quiz-questions.zip")
    extract_zipfile("quiz-questions.zip")

