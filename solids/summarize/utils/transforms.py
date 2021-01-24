import re
from lxml.html import document_fromstring
import unicodedata

class Transform:
    def __init__(self, content):
        self.content = content

    def __text(self, content):
        document = document_fromstring(content)
        text_content = str(document.text_content())
        result = re.sub(r"[\n\r]{1,}", ' ', text_content, 0, re.MULTILINE)
        return unicodedata.normalize("NFKD", result)

    def __stripped(self, content):
        clean_content = re.findall('[A-Za-z0-9-\.]+?(?=[\s_:\)\(\/,])', content.lower())
        restore_single = ' '.join(clean_content) 
        return restore_single

    @property
    def clean(self):
        return self.__text(self.content)
        # return self.__stripped(self.__text(self.content))
