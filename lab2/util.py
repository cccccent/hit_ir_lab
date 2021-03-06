from pyltp import Segmentor, Postagger
from os.path import exists
import json

train_path, test_path = './data/train.json', './data/new_test.json'
passages_path, seg_passages_path = './data/passages_multi_sentences.json', './data/seg_passages.json'
train_question_path, test_question_path = './data/train_questions.txt', './data/test_questions.txt'
cws_path, pos_path = 'E:/pyltp/ltp_data_v3.4.0/cws.model', 'E:/pyltp/ltp_data_v3.4.0/pos.model'
test_answer_path = './data/test_answer.json'
stop_words_path = './data/stopwords.txt'
seg, postagger = None, None


def file_exists(path):
    return exists(path)


def seg_line(line: str) -> list:
    global seg
    if not seg:
        seg = Segmentor()
        seg.load(cws_path)  # 加载模型
    return list(seg.segment(line))


def pos_tag(words: list) -> list:  # 词性标注
    global postagger
    if not postagger:
        postagger = Postagger()
        postagger.load(pos_path)  # 加载模型
    return list(postagger.postag(words))


def read_json(json_path):  # 读取json文件，要求每一行都是标准的json格式文件，返回：list[python对象]
    with open(json_path, 'r', encoding='utf-8') as f:
        return [json.loads(json_line) for json_line in f]


def write_json(json_path, obj):  # 导出json文件，输出的每一行都是标准的json格式文件，输入：list[python对象]
    with open(json_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join([json.dumps(item, ensure_ascii=False) for item in obj]))


def load(json_path):  # 读取JSON文件，获取python数据结构
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def dump(json_path, obj):  # 导出python对象到JSON文件中
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False)


def load_seg_passages():  # 加载分词后的passages
    if exists(seg_passages_path):
        seg_passages = load(seg_passages_path)
    else:
        seg_passages = {}
        for item in read_json(passages_path):
            seg_passages[item['pid']] = [seg_line(line.replace(' ', '')) for line in item['document']]
        dump(seg_passages_path, seg_passages)  # 将分词后的文本集导出到文件中
    return seg_passages


def read_stop_words():
    with open(stop_words_path, 'r', encoding='utf-8') as f:
        stop_words = set()
        for line in f:
            stop_words.add(line.strip())
        return stop_words
