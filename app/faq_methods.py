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


def faq_edit_answer(faq_path, new_answer, existed_answer, idx):
    with open(faq_path, 'r', encoding="utf-8") as stream:
        faq = yaml.safe_load(stream)
    for dict_elem in faq['questions']:
        if dict_elem['idx'] == idx:
            for answer in dict_elem['answers']:
                if answer['answer'] in existed_answer:
                    answer['answer'] = new_answer
                    with open(faq_path, 'w', encoding="utf-8") as stream:
                        result = yaml.dump(faq, stream, allow_unicode=True)
                    break


def faq_delete_answer(faq_path, existed_answer, idx):
    with open(faq_path, 'r', encoding="utf-8") as stream:
        faq = yaml.safe_load(stream)
    for dict_elem in faq['questions']:
        if dict_elem['idx'] == idx:
            if len(dict_elem['answers']) > 1:
                for answer in dict_elem['answers']:
                    if answer['answer'] in existed_answer:
                        dict_elem['answers'].remove(answer)
                        with open(faq_path, 'w', encoding="utf-8") as stream:
                            result = yaml.dump(faq, stream, allow_unicode=True)
                        break
            else:
                faq['questions'].remove(dict_elem)
                with open(faq_path, 'w', encoding="utf-8") as stream:
                    result = yaml.dump(faq, stream, allow_unicode=True)
                break
