from pathlib import Path
import datetime
import telebot
from configparser import ConfigParser
import prometheus_client
import logging
import argparse
from classify import classify_question
from keyboards import TelegramInlineKeyboard
import yaml
from faq_methods import faq_add_new_question, faq_extend_answer

parser = argparse.ArgumentParser(description="You can run this script locally, using flag --devmode or -d",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-d", "--devmode", action="store_true", help="Developer mode")
args = parser.parse_args()
config = vars(args)


devmode = config['devmode']
if devmode:
    logging.basicConfig(filename="C:\\Users\\amalinko\\PycharmProjects\\omni_faq_bot\\logs\\omni_faq_bot.log",
                        level=logging.INFO)
else:
    logging.basicConfig(filename="/omni_faq_bot/logs/omni_faq_bot.log", level=logging.INFO)
using_bot_counter = prometheus_client.Counter(
    "using_bot_count",
    "request to the bot",
    ['method', 'user_id', 'username']
)

parser = ConfigParser()
if devmode:
    parser.read(Path('C:\\Users\\amalinko\\PycharmProjects\\omni_faq_bot\\config\\init.ini').absolute())
else:
    parser.read(Path('/omni_faq_bot/config/init.ini').absolute())
telegram_api_token = parser['telegram']['telegram_api_token']
bot = telebot.TeleBot(token=telegram_api_token)

if devmode:
    faq_path: Path = Path(f"C:\\Users\\amalinko\\PycharmProjects\\omni_faq_bot\\config\\faq.yaml").absolute()
else:
    faq_path: Path = Path(f"/omni_faq_bot/config/faq.yaml").absolute()


if devmode:
    role_model_path: Path = Path(f"C:\\Users\\amalinko\\PycharmProjects\\omni_faq_bot\\config\\role_model.txt").absolute()
else:
    role_model_path: Path = Path(f"/omni_faq_bot/config/role_model.txt").absolute()

access_denied_message = "Для использоавания бота Вы должны быть в таблице \"Сотрудники стрима\" на странице \"Общие контакты\""


def check_access_rights(role_model_file, username):
    with open(role_model_file, "r") as stream:
        all_user = stream.read()
    if username in all_user:
        return True
    return False


def bot_monitoring(message):
    using_bot_counter.labels(message.text, message.from_user.id, message.from_user.full_name).inc()


def bot_logging(message):
    pass
    logging.info(
        f"{datetime.datetime.now().strftime('%d-%m-%Y %H:%M')}. "
        f"{message.text},"
        f" {message.from_user.id},"
        f" {message.from_user.full_name}"
    )


@bot.message_handler(commands=['add'])
def add_question_message(message):
    bot_logging(message)
    bot_monitoring(message)
    if not check_access_rights(role_model_file=role_model_path, username=f"@{message.chat.username}"):
        bot.send_message(
            message.chat.id,
            access_denied_message
        )
        return 0
    bot.send_message(
        message.chat.id,
        "Введите вопрос/Заголовок статьи",
    )
    bot.register_next_step_handler(message, header_message)


def header_message(message):
    question = message.text
    bot_monitoring(message)
    bot_logging(message)
    bot.send_message(
        message.chat.id,
        "Введите ответ на вопрос/Текст статьи",
    )
    bot.register_next_step_handler(message, content_message, question=question)


def content_message(message, question):
    content = message.text
    bot_monitoring(message)
    bot_logging(message)
    faq_add_new_question(faq_path, question, content, f"@{message.chat.username}")
    bot.send_message(
        message.chat.id,
        f"Добавлено {question}\n{content}",
    )


@bot.message_handler(content_types='text')
def question_message(message):
    bot_logging(message)
    bot_monitoring(message)
    if not check_access_rights(role_model_file=role_model_path, username=f"@{message.chat.username}"):
        bot.send_message(
            message.chat.id,
            access_denied_message
        )
        return 0
    using_bot_counter.labels(message.text, message.from_user.id, message.from_user.full_name).inc()
    logging.info(f"{datetime.datetime.now().strftime('%d-%m-%Y %H:%M')}. "
                 f"{message.text}, {message.from_user.id}, {message.from_user.full_name}")
    answer = classify_question(message.text, faq_path)
    keyboard = TelegramInlineKeyboard()
    keyboard.add_buttons(answer, 1)
    bot.send_message(
        message.chat.id,
        "Возможные варианты:",
        reply_markup=keyboard.get_keyboard()
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('answer'))
def query_handler(call):
    bot.answer_callback_query(callback_query_id=call.id)
    if not check_access_rights(role_model_file=role_model_path, username=f"@{call.message.chat.username}"):
        bot.send_message(
            call.message.chat.id,
            access_denied_message
        )
        return 0
    _, idx = call.data.split('_')
    with open(faq_path, 'r', encoding="windows-1251") as stream:
        faq = yaml.safe_load(stream)

    for dict_elem in faq['questions']:
        if dict_elem['idx'] == idx:
            call_answer = f"{dict_elem['question']}\n\n"
            for answer in dict_elem['answers']:
                call_answer += f"{answer['answer']}\n{answer['author']}\n\n"
            break
    else:
        call_answer = "Error"
    keyboard = TelegramInlineKeyboard()
    keyboard.add_button("Добавить ответ", f"extend_{idx}")
    bot.send_message(
        text=call_answer,
        chat_id=call.message.chat.id,
        reply_markup=keyboard.get_keyboard()
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('extend'))
def query_handler(call):
    bot.answer_callback_query(callback_query_id=call.id)
    if not check_access_rights(role_model_file=role_model_path, username=f"@{call.message.chat.username}"):
        bot.send_message(
            call.message.chat.id,
            access_denied_message
        )
        return 0
    _, idx = call.data.split('_')
    with open(faq_path, 'r', encoding="windows-1251") as stream:
        faq = yaml.safe_load(stream)

    for dict_elem in faq['questions']:
        if dict_elem['idx'] == idx:
            call_answer = f"{dict_elem['question']}"
            break
    else:
        call_answer = "Error"
    bot.send_message(
        text=f"Напишите еще один ответ для:\n{call_answer}",
        chat_id=call.message.chat.id,
    )
    bot.register_next_step_handler(call.message, extend_answer, idx=idx)


def extend_answer(message, idx):
    faq_extend_answer(faq_path, message.text, f"@{message.chat.username}", idx)
    with open(faq_path, 'r', encoding="windows-1251") as stream:
        faq = yaml.safe_load(stream)

    for dict_elem in faq['questions']:
        if dict_elem['idx'] == idx:
            call_answer = f"{dict_elem['question']}\n\n"
            for answer in dict_elem['answers']:
                call_answer += f"{answer['answer']}\n{answer['author']}\n\n"
            break
    else:
        call_answer = "Error"
    if call_answer != "Error":
        call_answer = f"Обновлено:\n{call_answer}"
        bot.send_message(
            text=call_answer,
            chat_id=message.chat.id
        )
    else:
        bot.send_message(
            text="Произошла ошибка",
            chat_id=message.chat.id
        )


if __name__ == '__main__':
    prometheus_client.start_http_server(9400)
    bot.infinity_polling()
