###############################################################################
# Author: Wasi Ahmad
# Project: Multi-task Match Tensor: a Deep Relevance Model for Search
# Date Created: 7/29/2017
#
# File Description: This script provides a definition of the corpus, each
# example in the corpus and the dictionary.
###############################################################################

import os, helper, json
from collections import Counter


class Dictionary(object):
    def __init__(self):
        self.word2idx = {}
        self.idx2word = []
        self.pad_token = '<p>'
        self.idx2word.append(self.pad_token)
        self.word2idx[self.pad_token] = len(self.idx2word) - 1
        self.unk_token = '<unk>'
        self.idx2word.append(self.unk_token)
        self.word2idx[self.unk_token] = len(self.idx2word) - 1

    def build_dict(self, sessions, max_words=80000):
        word_count = Counter()
        for sess_len, session_list in sessions.data.items():
            for session in session_list:
                for query in session:
                    word_count.update(query.text)
                    for rel_doc in query.rel_docs:
                        word_count.update(rel_doc.text)

        print('total unique word = ', len(word_count))
        most_common = word_count.most_common(max_words)
        for (index, w) in enumerate(most_common):
            self.idx2word.append(w[0])
            self.word2idx[w[0]] = len(self.idx2word) - 1

    def contains(self, word):
        return True if word in self.word2idx else False

    def __len__(self):
        return len(self.idx2word)


class Document(object):
    def __init__(self, content, max_len, tokenize=False):
        content_terms = helper.tokenize(content, tokenize)
        self.text = ['<s>'] + content_terms if len(content_terms) <= max_len else content_terms[:max_len] + ['</s>']
        self.is_clicked = False

    def set_clicked(self):
        self.is_clicked = True


class Query(object):
    def __init__(self, text, max_len, tokenize=False):
        content_terms = helper.tokenize(text, tokenize)
        self.text = ['<s>'] + content_terms if len(content_terms) <= max_len else content_terms[:max_len] + ['</s>']
        self.rel_docs = []

    def add_rel_doc(self, doc):
        if isinstance(doc, Document):
            self.rel_docs.append(doc)
        else:
            print('unknown document type!')


class Corpus(object):
    def __init__(self, _tokenize, max_q_len, max_d_len):
        self.tokenize = _tokenize
        self.max_q_len = max_q_len
        self.max_d_len = max_d_len
        self.data = dict()

    def parse(self, in_file, max_example=None):
        """Parses the content of a file."""
        assert os.path.exists(in_file)

        total_session = 0
        with open(in_file, 'r') as f:
            for line in f:
                session = json.loads(line)
                assert len(session['query']) == len(session['clicks'])

                current_session = []
                for qidx in range(len(session['query'])):
                    query = Query(session['query'][qidx][0], self.max_q_len, self.tokenize)
                    for i in range(len(session['clicks'][qidx])):
                        doc = Document(session['clicks'][qidx][i][1], self.max_d_len, self.tokenize)
                        doc_label = session['clicks'][qidx][i][2]
                        if int(doc_label) == 1:
                            doc.set_clicked()
                        query.add_rel_doc(doc)
                    current_session.append(query)

                if len(current_session) in self.data:
                    self.data[len(current_session)].append(current_session)
                else:
                    self.data[len(current_session)] = [current_session]
                total_session += 1
                if total_session == max_example:
                    break

    def __len__(self):
        length = 0
        for key, value in self.data.items():
            length += len(value)
        return length
