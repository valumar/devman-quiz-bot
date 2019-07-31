import random
import json
import pymorphy2
import logging
import requests

from string import punctuation


logger = logging.getLogger(__name__)


def load_data(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    return data


def get_random_question(data):
    random_champ = random.choice(list(data.keys()))
    random_question = random.choice(data[random_champ])
    random_question['Чампионат'] = random_champ
    logger.info(f"get_random_question - {random_champ} {random_question}")
    return random_question


def normalize(sentence):
    morph = pymorphy2.MorphAnalyzer()
    for character in punctuation:
        sentence = sentence.replace(character, " ")
    sentence = sentence.split()
    normalized_sentence = []
    for word in sentence:
        normalized_sentence.append(morph.parse(word)[0].normal_form)
    return set(normalized_sentence)


def compare(answer, reference):
    normalized_answer = normalize(answer)
    normalized_reference = normalize(reference)
    difference = normalized_reference - normalized_answer
    result = False
    if len(difference) <= .5 * len(normalized_reference):
        result = True
    return result


def spellcheck(sentence):
    url = "https://speller.yandex.net/services/spellservice.json/checkTexts"
    payload = {
        "text": sentence
    }
    response = requests.get(url, params=payload)
    if response.ok and len(response.json()[0]) > 0:
        checked_sentence = " ".join(i['s'][0] for i in response.json()[0])
        return checked_sentence
    else:
        return sentence
