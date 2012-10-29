import tfidf
import math


class VSM(object):

    def __init__(self):
        self.index = {}
        self.count = 0

    def make_vocabulary(self, doc_list):
        vocabulary = set()

        for doc in doc_list:
            for word in doc.split(' '):
                vocabulary.add(word)

        for word in vocabulary:
            self.index[word] = self.count
            self.count += 1

    def make_tf_matrix(self, doc_list):
        tf_matrix = []

        for doc in doc_list:
            row = [0] * self.count
            for word in doc.split(' '):
                row[self.index[word]] = tfidf.tf_idf(word, doc, doc_list)
            tf_matrix.append(row)

        return tf_matrix


def norm_l2(row):
    return math.sqrt(sum(map(lambda x: x * x, row)))


def dot(v1, v2):
    return sum(map(lambda x: x[0] * x[1], zip(v1, v2)))


def cosine(v1, v2):
    return dot(v1, v2) / (norm_l2(v1) * norm_l2(v2))


def main():
    doc_list = ['tigre vive selva', 'leon vive selva', 'leon come cebras']
    vsm = VSM()
    vsm.make_vocabulary(doc_list)
    m = vsm.make_tf_matrix(doc_list)
    print cosine(m[0], m[1])
    print cosine(m[0], m[2])
    print cosine(m[1], m[2])
    return m

if __name__ == '__main__':
    main()
