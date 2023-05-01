import yaml


def faq_add_new_question(faq_path, question, answer, author):
    with open(faq_path, 'r', encoding="utf-8") as stream:
        faq = yaml.safe_load(stream)
    max_idx = -1
    for dict_elem in faq['questions']:
        if int(dict_elem['idx']) > max_idx:
            max_idx = int(dict_elem['idx'])
    faq['questions'].append({'question': question, 'answers': [{'answer': answer, 'author': author}], 'idx': str(max_idx+1)})
    with open(faq_path, 'w', encoding="utf-8") as stream:
        result = yaml.dump(faq, stream, allow_unicode=True)


def faq_extend_answer(faq_path, answer, author, idx):
    with open(faq_path, 'r', encoding="utf-8") as stream:
        faq = yaml.safe_load(stream)
    for dict_elem in faq['questions']:
        if dict_elem['idx'] == idx:
            dict_elem['answers'].append({'answer': answer, 'author': author})
            with open(faq_path, 'w', encoding="utf-8") as stream:
                result = yaml.dump(faq, stream, allow_unicode=True)
            break
