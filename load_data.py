import logging
import json
import zipfile
import urllib.error
import urllib.request
import re
import os

from tqdm import tqdm

logger = logging.getLogger(__name__)


# https://stackoverflow.com/a/53877507
class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download_file(url):
    logger.debug(f'Downloading file from {url}...')
    output_path = url.split('/')[-1]
    try:
        with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=output_path) as t:
            urllib.request.urlretrieve(url, filename=output_path, reporthook=t.update_to)
        return output_path
    except urllib.error.HTTPError as e:
        logger.error(f"HTTPError: {e}")
    except urllib.error.URLError as e:
        logger.error(f"URLError: {e}")
    except Exception as e:
        logger.error(f"Generic Error: {e}")


def extract_zipfile(archive):
    logger.debug(f'Extracting archive: {archive}...')
    with zipfile.ZipFile(archive, "r") as zip_ref:
        zip_ref.extractall("downloads")


def match_data(data):
    logger.debug('Matching data...')
    # https://regex101.com/r/UxmySB/3
    regex = r"""(Вопрос\s\d+:\n)                                    # Первый якорь: строка начинающаяся на `Вопрос`
                (.*(?:\n(?!Ответ:$).*)*)\n+                         # Извлекаем текст до якоря `Ответ:`
                (Ответ:$)                                           # Якорь `Ответ:` 
                \n(.*(?:\n(?!Вопрос\s\d+:\n)|(?!Тур:\n).*)*)\n+"""  # Извлекаем текст ответа до якоря `Вопрос` или `Тур`
    matches = re.findall(regex, data, re.VERBOSE | re.MULTILINE)
    return matches


def list_files(folder):
    logger.debug(f'Listing files in folder {folder}...')
    files_list = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    return files_list


def add_data_to_dict(title, matches, quiz_dict):
    logger.debug(f'\tAddinng data to dict from {title}...')
    quiz_dict[title] = list()
    for match in matches:
        if not match[1].startswith("(pic") and match[1].find("<раздатка>") == -1:
            question = match[1]
            answer_short = match[3].split(".")[0]
            answer_desc = ".".join(match[3].split(".")[1:])
            quiz_dict[title].append({
                "Вопрос": question,
                "Ответ": [answer_short, answer_desc]
            })
    return quiz_dict


def generate_dict():
    logger.debug('Generating dictionary...')
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
    logger.debug('START')
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG,
        filename='log.log'
    )
    r = download_file("http://dvmn.org/media/modules_dist/quiz-questions.zip")
    extract_zipfile(r)
    quiz_dict = generate_dict()
    with open('dict.json', 'w', encoding='utf-8') as json_file:
        logger.debug(f'Dumping dictionary to file {json_file.name} ...')
        json.dump(quiz_dict, json_file, ensure_ascii=False)
    logger.debug('FINISH')
