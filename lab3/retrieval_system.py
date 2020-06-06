"""
使用自己构建的BM25模型进行检索系统的构建.
"""
from json import load, dump, loads
from pyltp import Segmentor
from os.path import exists
from math import log

bm25_model_path, cws_path = './retrieval_system/bm25', 'E:/pyltp/ltp_data_v3.4.0/cws.model'
passages_path = './data/seg_res.json'
seg, passages = None, []


class BM25:
    def __init__(self, k1=1.5, b=0.75, k3=1.5):
        self.idf = {}  # 形如{word:idf}
        self.tf = []  # 形如[{word:tf}]
        self.doc_lens = []  # 形如[len(doc)]
        self.avg_doc_len = 0  # 所有文档的平均词数
        self.param = {'k1': k1, 'b': b, 'k3': k3}  # 模型超参数

    def fit(self, docs):  # 初始化模型参数
        self.doc_lens = [len(doc) for doc in docs]
        self.avg_doc_len = sum(self.doc_lens) / len(docs)
        for doc in docs:
            self.tf.append({})
            for word in doc:
                if word not in self.tf[-1]:
                    self.tf[-1][word] = 0
                    self.idf[word] = self.idf.get(word, 0) + 1
                self.tf[-1][word] += 1
        for word, df in self.idf.items():
            self.idf[word] = log(len(docs) / df)

    def calc_score(self, query_words):
        k1, b, k3, rsv_lst, query_tf = self.param['k1'], self.param['b'], self.param['k3'], [], {}
        for word in query_words:
            query_tf[word] = query_tf.get(word, 0) + 1
        for idx in range(len(self.tf)):
            rsv = sum([self.idf[word] * (k1 + 1) * self.tf[idx][word] / (
                    k1 * (1 - b + b * self.doc_lens[idx] / self.avg_doc_len) + self.tf[idx][word]) * (
                               k3 + 1) * tf / (k3 + tf) for word, tf in query_tf.items() if word in self.tf[idx]])
            rsv_lst.append(rsv)
        return rsv_lst

    def load(self, model_path):  # 加载模型
        with open(model_path, 'r', encoding='utf-8') as f:
            json_dic = load(f)
            self.idf, self.tf, self.doc_lens, self.avg_doc_len, self.param = json_dic['idf'], json_dic['tf'], json_dic[
                'doc_lens'], json_dic['avg_doc_len'], json_dic['param']

    def dump(self, model_path):  # 导出模型
        with open(model_path, 'w', encoding='utf-8') as f:
            dump({'idf': self.idf, 'tf': self.tf, 'doc_lens': self.doc_lens, 'avg_doc_len': self.avg_doc_len,
                  'param': self.param}, f, ensure_ascii=False)


def seg_line(line: str) -> list:
    global seg
    if not seg:
        seg = Segmentor()
        seg.load(cws_path)  # 加载模型
    return list(seg.segment(line))


def read_json(json_path):  # 读取json文件，要求每一行都是标准的json格式文件，返回：list[python对象]
    with open(json_path, 'r', encoding='utf-8') as f:
        return [loads(json_line) for json_line in f]


def get_res(query, bm25: BM25, num=10):  # num表示获取最相关的文章数目，返回值为[]*num，元素为{'url':url,segmented_title:''...}
    rsv_lst = bm25.calc_score(seg_line(query))
    rsv_lst = sorted([(idx, val) for idx, val in enumerate(rsv_lst)], key=lambda item: item[1], reverse=True)[:num]
    global passages
    if not passages:
        passages = read_json(passages_path)
    return [passages[item[0]] for item in rsv_lst]


def main():
    bm25 = BM25()
    if exists(bm25_model_path):
        bm25.load(bm25_model_path)
    else:
        docs = [item['segmented_paragraphs'] for item in read_json(passages_path)]
        bm25.fit(docs)
        bm25.dump(bm25_model_path)
    get_res('新冠疫情形势大好', bm25)


if __name__ == '__main__':
    main()
