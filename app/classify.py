from fuzzywuzzy import process
import pymorphy2
import yaml

morph = pymorphy2.MorphAnalyzer()


def classify_question(text, faq_path):
    text = ' '.join(morph.parse(word)[0].normal_form for word in text.split())
    with open(faq_path, 'r', encoding="utf-8") as stream:
        faq = yaml.safe_load(stream)
    existed_answers = []
    for dict_elem in faq['questions']:
        existed_answer = dict_elem['question']
        existed_answers.append(existed_answer)

    scores = process.extract(text, existed_answers, limit=3)
    print(scores)
    result_answer = []
    for idx in scores:
        for dict_elem in faq['questions']:
            if dict_elem['question'] == idx[0]:
                result_answer.append({"text": dict_elem['question'], "callback": f"answer_{dict_elem['idx']}"})
    return result_answer
