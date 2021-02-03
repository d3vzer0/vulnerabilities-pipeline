from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd


class TFIDF:
    def __init__(self, threshold=0.2):
        self.threshold = threshold
        self.tokenizer = lambda doc: doc.split('__')
    
    def keywords(self, docs):
        vectorizer = TfidfVectorizer(
            strip_accents = None,
            use_idf=True,
            sublinear_tf=False,
            preprocessor=None,
            tokenizer=self.tokenizer
        )
        vectors = vectorizer.fit_transform([doc['content'] for doc in docs])
        df = pd.DataFrame(vectors.toarray(), index=[doc['title'] for doc in docs],
            columns=vectorizer.get_feature_names())
        terms = {index: [column.lower() for column, value in row.iteritems() if value > self.threshold and len(column) > 1] \
            for index, row in df.iterrows()}
        return terms
 