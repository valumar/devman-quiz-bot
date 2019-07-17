import logging
import zipfile
import urllib.request
import re
import os

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


def match_data(data):
    # https://regex101.com/r/UxmySB/2
    regex = r"(Вопрос \d+:\n)(.*(?:\n(?!Ответ:$).*)*)\n+(Ответ:$)\n(.*(?:\n(?!Вопрос \d+:\n)|(?!Тур:\n).*)*)\n+"
    matches = re.findall(regex, data, re.MULTILINE)
    return matches


def list_files(folder):
    files_list = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    return files_list


def add_data_to_dict(title, matches, quiz_dict):
    quiz_dict[title] = list()
    for match in matches:
        quiz_dict[title].append({
            "Вопрос": match[1],
            "Ответ": match[3]
        })
    return quiz_dict


def generate_dict():
    files_list = list_files('downloads')
    quiz_dict = dict()
    for data_file in files_list:
        file_path = os.path.join('downloads', data_file)
        with open(file_path, 'r', encoding='koi8-r') as f:
            data = f.read()
        matches = match_data(data)
        title = data.split('\n')[1]
        add_data_to_dict(title, matches, quiz_dict)
    return quiz_dict


if __name__ == '__main__':
    # r = download_file("http://dvmn.org/media/modules_dist/quiz-questions.zip")
    # extract_zipfile(r)
    quiz_dict = generate_dict()

