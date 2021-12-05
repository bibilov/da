# Работа с большими XML-файлами

Для большинства языков программирования доступно некоторое количество устоявшихся API для работы с XML-документами.

Один из самых известных &mdash; построение дерева элементов (DOM) в памяти. Это один из самых удобных и быстрых API, потому что позволяет работать с деревом элементов, непосредственно поднятым в RAM, перемещаясь по нему в произвольном порядке.

```python
import xml.etree.ElementTree as ET
```

Но иногда такой подход не срабатывает. Например, XML-файл может быть слишком большим. 

Если мы загрузим все резюме с портала Труд всем (https://trudvsem.ru/), а это 15Гб XML, то мы не сможем работать как с деревом в памями. Если только конечно у нас нет лишних 50-60-70Гб RAM (так как каждый элемент и его свойства оборачиваются в объектную структуру Питона, в памяти это будет занимать больше места, чем на жестком диске).

Отдельно инетересно, если ли у кого-то из вас компьютер, у которого хватит оперативной памяти для этого.

Ссылка на XML:

http://opendata.trudvsem.ru/7710538364-vacancy/data-20211202T130014-structure-20161130T143000.xml

Кстати, воотще весь xml записан в одну строку, с ним не справится ни одна IDE, ни один prettifier, ни один браузер (тоже нужно очень много оперативной памяти). 

Даже получить в читаемом виде хотя бы одно отформатированное резюме &mdash; нетривиальная задача.

Как быть в таких случаях? В этом случае помогает событийная модель работы с XML (SAX). Это однопроходный парсер по тексту XML-документа, сообщающий о событиях: тег начался, тег закончился и т.д. Вы переопределяете у себя в коде обработчики таких событий.

Довольно содержательный пример можно посмотреть вот тут:

https://www.tutorialspoint.com/parsing-xml-with-sax-apis-in-python

Затрат оперативной памяти никаких, зато трудно собирать все теги вместе, особенно если их много или большая вложенность.

В подготовке датасета для ваших задач я попробовал объединить два подхода:

* Идет считывание текстового файла блоками по нескольку мегабайт, выкусывается все, что между `<cv ` и `</cv>`, в файле несколько миллионов таких тегов.
* Содержимое каждого оборачивается в `ET`.
* Парсер работает как генератор по резюме.
* Почему тег называется `cv`? От `Curriculum vitae`, _краткое хронологическое описание жизни, образования, мест работы и профессиональных навыков по определённой форме_.

```python
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError

class ReadByChunk():
   def __init__(self, file, tag="cv", bufsize=1):
        self.tag = tag
        self._buf = ""
        self.file = open(file, encoding="utf8")
        self.bufsize = bufsize

   def tags(self):
        while True:
            pos = self._buf.find(f'<{self.tag} ')
            if pos == -1:
                self._buf += self.file.read(self.bufsize * 1024 * 1024)
                pos = self._buf.find(f'<{self.tag} ')
                if pos == -1:
                    raise StopIteration
            self._buf = self._buf[pos:]

            end_pos = self._buf.find(f'</{self.tag}>')
            if end_pos == -1:
                self._buf += self.file.read(self.bufsize * 1024 * 1024)
                end_pos = self._buf.find(f'</{self.tag}>')
                if end_pos == -1:
                    raise StopIteration

            xml_tag = self._buf[:end_pos+len(f'</{self.tag}>')]
            self._buf = self._buf[end_pos+len(f'</{self.tag}>'):]
            try:
                root = ET.fromstring(xml_tag)
            except ParseError as e:
                pass
            yield root
```

Особенности:
* Этот код, конечно, нуждается в рефакторинге.
* `self.bufsize` вроде бы как в мегабайтах, на самом деле нет, потому что в тектовом режиме чтения он считывает `1024 * 1024` _символов_. Причем кириллица занимает 2 байта. То есть по умолчанию чтение идет кусками размером `1 <= s <= 2` Мб.
* Делается предположение, что `cv` никогда не привысит размер `bufsize`: допускает только одно повторное считывание на границе буфера.
* Если делать буфер большим, например, 100Мб, парсер замедляется в десятки раз. Попробуйте понять почему.

Далее мы формируем CSV-файл на основе некоторых тегов. Словарб содержит XPATH для элемента и его имя в CSV.

```python
import csv

rename = {
   'salary': 'salary', 
   'educationType': 'educationType', 
   'workExperienceList/workExperience[1]/jobTitle': 'jobTitle',
   "educationList/educationType[1]/qualification": 'qualification',
   'gender': 'gender', 
   'innerInfo/dateModify': 'dateModify', 
   "skills": "skills", 
   "otherInfo": "otherInfo"  
}
```

А далее просто кладем в итоговый файл 1% cv.


```python
from random import randint

reader = ReadByChunk("cv.xml", bufsize=1)

with open('works.csv', 'w', newline='') as csvfile:
    fieldnames = list(rename.values())
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
        
    for tag in tqdm(reader.tags()):
        props = {}
        for k, v in rename.items():
            try:
                props[v] = tag.find(k).text
            except: 
                props[v] = ""

        if randint(0, 100) == 0:    
            writer.writerow(props)
```

* Здесь бы уместно смотрелся `collections.defaultdict`.

# ДЗ

В датасете есть два поля:
* `jobTitle` &mdash; должность на последнем месте работы.
* `qualification` &mdash; условно, что написано в дипломе.

Попробуйте поработать с городскими легендами про профессии:

* У какого количества людей профессия и должность не совпадают?
* Люди с каким образованием становятся менеджерами (топ-5)?
* Кем работают люди, которые по диплому являются инженерами (топ-5)? 

Какие сложности могут возникнуть? 

* Редко, когда эти поля состоят из одного слова:  `менеджер`, `товаровед`. Иногда это `Продавец-кассир`, `Экономист-менеджер`. Или даже `Помощник юриста`, `бакалавр юриспруденции`.
* Сделайте небольшой анализ на эту тему и попробуйте свести все профессии и квалификации к категориям из одного слова: `юрист`, `продавец`, `кассир`, `инженер`, `автомеханик`. Для этого можно использовать встроенные строковые функции, модуль `re`, а также ассортимент NLP (natural language processing) библиотек.

### Необязательное усложнение

https://matplotlib.org/stable/gallery/images_contours_and_fields/image_annotated_heatmap.html

Постройте с помощью `matplotlib` таблицу с top-5 профессий и top-5 должностей, а также с частотой их взаимосвязи.

Что-то типа этого:
![Таблица](https://matplotlib.org/stable/_images/sphx_glr_image_annotated_heatmap_001_2_0x.png)
