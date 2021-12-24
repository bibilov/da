import os
from collections import defaultdict

from nltk import PorterStemmer
from tqdm import tqdm
import pandas as pd
import nltk

import XmlReader
import csv

ps = PorterStemmer()


def normalize(s, not_allowed_parts=()):
    words = []
    for sent in filter(lambda x: not str.isspace(x), s.split('.')):
        words += list(map(ps.stem, map(str.strip, nltk.word_tokenize(sent, language='russian'))))

    tagged = nltk.pos_tag(words, lang='rus')
    return ', '.join(sorted(map(lambda x: x[0], filter(lambda x: x[0] != '' and not str.isspace(x[0]) and
                                                       x[1] not in not_allowed_parts,
                                                       tagged))))


def main():
    if not os.path.isfile('works.csv'):
        prepare_csv()
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger_ru')
    data = pd.read_csv('works.csv').dropna()

    not_allowed_parts = ['ADP', 'CONJ', 'DET', 'PRT', 'PRON', '.', 'X']
    data.jobTitle = data.jobTitle.map(lambda x: normalize(x, not_allowed_parts), na_action='ignore')
    data.qualification = data.qualification.map(lambda x: normalize(x, not_allowed_parts), na_action='ignore')

    not_matching = 0
    for (title, qualif) in zip(data.jobTitle, data.qualification):
        if title == '' or qualif == '' or str.isspace(title) or str.isspace(
                qualif):
            continue
        if title not in qualif and qualif not in title:
            not_matching += 1

    print(f'Не совпадающие профессии: {not_matching}') #989

    print(data[data.jobTitle.str.contains(
            'менеджер')].qualification)
    top_managers = data[data.jobTitle.str.contains(
            'менеджер')].qualification.value_counts().head(5)

    top_engineers = data[data.jobTitle.str.contains(
            'инженер')].qualification.value_counts().head(5)

    print('Топ 5 менеджеров:')
    print(top_managers)
    # бакалавр              11
    # менеджер              10
    # специалист             6
    # экономист              6
    # экономист-менеджер     4
    print('Топ 5 инженеров:')
    print(top_engineers)
    # инженер             18
    # бакалавр             4
    # инженер-механик      3
    # инженер-электрик     2
    # менеджер             2

def prepare_csv():
    from random import randint
    rename = {
            'salary':                                        'salary',
            'educationType':                                 'educationType',
            'workExperienceList/workExperience[1]/jobTitle': 'jobTitle',
            "educationList/educationType[1]/qualification":  'qualification',
            'gender':                                        'gender',
            'innerInfo/dateModify':                          'dateModify',
            "skills":                                        "skills",
            "otherInfo":                                     "otherInfo"
            }
    reader = XmlReader.ReadByChunk("big_xml.xml")
    with open('works.csv', 'w', newline='') as csvfile:
        fieldnames = list(rename.values())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for tag in tqdm(reader.tags()):
            props = defaultdict(str)
            for k, v in rename.items():
                actual_tag = tag.find(k)
                if actual_tag is None:
                    continue
                props[v] = actual_tag.text

            if randint(0, 100) == 0:
                writer.writerow(props)


if __name__ == "__main__":
    main()
