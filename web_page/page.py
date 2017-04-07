# coding=utf-8
"""
Web page for demonstrating work of the classifier.
"""
from flask import Flask
from flask import render_template
from flask import request

import numpy as np
import pymorphy2
from nltk.tokenize import RegexpTokenizer
import cPickle

morph = pymorphy2.MorphAnalyzer()
tokenizer = RegexpTokenizer('\w+')


def normalize(s):
    return ' '.join(map(lambda w: morph.parse(w)[0].normal_form, tokenizer.tokenize(s)))


def remove_minor_pos(s):
    return ' '.join(filter(lambda w: morph.parse(w)[0].tag.POS not in ['PREP', 'CONJ', 'INTJ'], tokenizer.tokenize(s)))


def normalize_remove(s):
    return normalize(remove_minor_pos(s))


def count_part_entries2(words, text, part_size, pair_weight):
    count = 0
    words = words.split(' ')
    words = map(lambda w: w[:part_size], words)
    text = ' '.join(map(lambda w: w[:part_size], text.split(' ')))
    for i in range(len(words)-1):
        if words[i] in text:
            count += 1
            pair = ' '.join((words[i], words[i+1]))
            if pair in text:
                count += pair_weight
    if words[-1] in text:
        count += 1
    return count


def get_top_tags(text_normed, tags, num_tags, part_size, pair_weight=2):
    similarities = []
    for tag in tags:
        support = tags_table[tags_table.norm == tag].support.values[0]
        variants = [tag]
        if type(support) is not float:
            variants += support.split(';')
        scores = map(lambda var:\
            count_part_entries2(var, text_normed, part_size, pair_weight) / (len(var.split(' ')) + 0.1), variants)
        similarities.append(np.max(scores))
    result = []
    for _ in range(num_tags):
        idx = np.argmax(similarities)
        result.append((tags[idx], similarities[idx]))
        similarities[idx] = 0.
    return result


tags_table = cPickle.load(open('../data/tags_table.p', 'rb'))
sessions = dict()


def predict_tag_for_request(tag_id, question_body, sender_id, session_new):
    cur_tag = u'ОСАГО'
    history = ''
    if sender_id in sessions:
        if not session_new:
            cur_tag, history = sessions[sender_id]
        else:
            sessions[sender_id] = None

    if tags_table[tags_table.tag == cur_tag].leaf.values[0]:
        return tags_table[tags_table.tag == cur_tag].index.values[0], 404

    tag_indices = []
    parents = [cur_tag]
    while parents:
        p = parents.pop()
        tag_indices += list(tags_table[tags_table.parent == p].index)
        parents += list(tags_table[tags_table.parent == p].tag)
    if cur_tag == u'ОСАГО':
        tag_indices.append(32)
    local_table = tags_table.ix[tag_indices]
    tags_norm = local_table.norm.values

    question_normed = normalize(remove_minor_pos(question_body))
    history += ' ' + question_normed
    top_tag_normed, similarity = get_top_tags(history, tags_norm, 1, 5)[0]
    top_tag = local_table[tags_table.norm == top_tag_normed].tag.values[0]

    sessions[sender_id] = (top_tag, history)

    return tags_table[tags_table.tag == top_tag].index.values[0], similarity


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def form():
    if request.method == 'GET':
        return render_template('page.html')

    user_ip = request.remote_addr
    text_raw = request.form['question']

    if request.form['btn'] == 'NO!':
        if user_ip in sessions:
            sessions.pop(user_ip)
        return render_template('page.html', question=text_raw, result='=(')

    idx, similarity = predict_tag_for_request(0, text_raw, user_ip, False)
    tag = tags_table.ix[idx].tag
    ans = tags_table.ix[idx].answer
    if type(ans) is float:
        ans = ''

    if similarity == 0.:
        sessions.pop(user_ip)
        return render_template('page.html', question=text_raw,
                               result=u'Чего чего??')
    else:
        return render_template('page.html', question=text_raw,
                               result='\n\n'.join([tag, ans]))


if __name__ == '__main__':
    app.run(host='0.0.0.0')
