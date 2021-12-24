import sys
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError


class ReadByChunk:
    def __init__(self, file, tag="cv", read_chars=1024 * 1024):
        self.read_chars = read_chars
        self.tag = tag
        self._buf = ""
        self.file = open(file, encoding="utf8")

    def _find_string(self, s, is_opening=True):
        pos = self._buf.find(s)
        while pos == -1:
            additional_buf = self.file.read(self.read_chars)
            if additional_buf == '':
                return -1
            if is_opening and self._buf != '':
                for i in range(1, len(s)):
                    buf_end = self._buf[-i:]
                    end_partial = buf_end + additional_buf[:(len(s) - i)]
                    if end_partial == s:
                        self._buf = buf_end + additional_buf
                        return 0
            self._buf += additional_buf
            pos = self._buf.find(s)
        return pos

    def tags(self):
        open_string = f'<{self.tag} '
        end_string = f'</{self.tag}>'
        while True:
            pos = self._find_string(open_string)
            if pos == -1:
                raise StopIteration
            if pos != 0:
                self._buf = self._buf[pos:]

            end_pos = self._find_string(end_string, False)
            if end_pos == -1:
                raise StopIteration

            xml_tag = self._buf[:end_pos + len(f'</{self.tag}>')]
            self._buf = self._buf[end_pos + len(f'</{self.tag}>'):]
            try:
                root = ET.fromstring(xml_tag)
                yield root
            except ParseError as e:
                pass
