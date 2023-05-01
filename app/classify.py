import json
from fuzzywuzzy import fuzz
import pymorphy2
import yaml

morph = pymorphy2.MorphAnalyzer()


def top_max_elements(array):
    result_list = [0, 0, 0]
    for element in array:
        if element > result_list[0]:
            result_list[2] = result_list[1]
            result_list[1] = result_list[0]
            result_list[0] = element
        elif element > result_list[1]:
            result_list[2] = result_list[1]
            result_list[1] = element
        elif element > result_list[2]:
            result_list[2] = element
    return result_list


def classify_question(text, faq_path):
    text = ' '.join(morph.parse(word)[0].normal_form for word in text.split())
    # with open(faq_path, encoding="utf-8") as json_file:
    #     faq = json.load(json_file)
    with open(faq_path, 'r', encoding="windows-1251") as stream:
        faq = yaml.safe_load(stream)
    existed_answers = []
    answer_idx = []
    for dict_elem in faq['questions']:
        existed_answer = dict_elem['question']
        # for answer in dict_elem['answers']:
        #     existed_answer += f" {answer['answer']}"
        existed_answers.append(existed_answer)
        answer_idx.append(dict_elem['idx'])
    scores = list()
    for existed_answer in existed_answers:
        norm_question = ' '.join(morph.parse(word)[0].normal_form for word in existed_answer.split())
        scores.append(fuzz.token_sort_ratio(norm_question.lower(), text.lower()))
    finded_answer_idx = top_max_elements(scores)
    for idx in range(0, len(finded_answer_idx)):
        finded_answer_idx[idx] = scores.index(finded_answer_idx[idx])
        scores[finded_answer_idx[idx]] = -1
    result_answer = []
    for idx in finded_answer_idx:
        for dict_elem in faq['questions']:
            if int(dict_elem['idx']) == idx:
                result_answer.append({"text": dict_elem['question'], "callback": f"answer_{dict_elem['idx']}"})
    return result_answer
