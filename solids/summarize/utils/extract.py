from spacy.util import compile_prefix_regex, compile_infix_regex, compile_suffix_regex
from spacy.tokenizer import Tokenizer
# from spacy.matcher import Matcher
# from spacy.matcher import PhraseMatcher
from spacy.pipeline import EntityRuler
import spacy
import re

class Extract:
    def __init__(self, nlp=None, docs=None):
        self.nlp = nlp
        self.docs = docs

    def props(self, min_length=2):
        # stop_words = self.nlp.Defaults.stop_words
        # tokens = [set(token.lemma_ for token in doc
        #     if (token.tag_ == 'NNP' and token.pos_ == 'PROPN') and \
        #         len(token.lemma_) > min_length and \
        #         not token.lemma_ in stop_words) for doc in self.docs]
        tokens = [set(ent.text.strip() for ent in doc.ents if ent.label_ in ['ORG',
            'PRODUCT', 'CVE', 'PERSON', 'ADVISORY']) for doc in self.docs]
        return tokens

    @classmethod
    def from_docs(cls, docs, model='en_core_web_md', custom_patterns=None):
        nlp = spacy.load(model)
        url_regex = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        nlp.tokenizer = Tokenizer(nlp.vocab,
            prefix_search=compile_prefix_regex(nlp.Defaults.prefixes).search,
            suffix_search=compile_suffix_regex(nlp.Defaults.suffixes).search,
            url_match=url_regex.match,
            infix_finditer= re.compile(r'''[~]''').finditer
        )
        if custom_patterns:
            ruler = EntityRuler(nlp, validate=True, overwrite_ents=True).from_disk(custom_patterns)
            nlp.add_pipe(ruler)
        return cls(nlp, docs=nlp.pipe(docs))
