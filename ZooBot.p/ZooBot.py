import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from collections import Counter
from config import TOKEN

bot = telebot.TeleBot(TOKEN) #Здесь нужно вствить ваш Токен#

class InvalidAnswerError(Exception):
    pass


# Вопросы и ответы викторины с категориями
questions = [
    {
        "question": "Насколько часто вы проводите время с семьёй/друзьями?",
        "options": ["Всё время, одному скучно",
                    "Люблю проводить время один",
                    "Часто, но иногда хочется побыть наедине с собой"]
    },
    {
        "question": "Вам больше нравится лето или зима?",
        "options": ["Я больше люблю лето, не переношу холод",
                    "Для меня не имеет особого значения, любое время года по своему прекрасно",
                    "Я больше люблю зиму, мне не нравится жара"]
    },
    {
        "question": "Вы любите путешествовать?",
        "options": ["Обожаю путешествия, хотел бы посетить много разных стран",
                    "Люблю поездки, но не часто, всё же от них тоже нужно отдыхать",
                    "Не люблю путешествовать, дома я чувствую себя уютнее"]
    },
    {
        "question": "Вы любите мясо или предпочитаете зелень и овощи?",
        "options": ["Предпочитаю мясу овощи, они намного полезнее",
                    "Я всеядный человек, мне нравится всё",
                    "Люблю мясные блюда и мне не нравятся многие овощи"]
    },
    {
        "question": "Вы ведёте активный образ жизни?",
        "options": ["Я люблю спорт, но поваляться дома тоже иногда хочется",
                    "Люблю как можно больше спать и отдыхать, это же замечательно",
                    "Да, я люблю много гулять и заниматься спортом"]
    },
    {
        "question": "Вы любите плавать?",
        "options": ["Нет, я не умею/не люблю плавать",
                    "Да, обожаю купаться везде, где появляется возможность",
                    "Иногда можно съездить искупаться в жаркий денёк"]
    },
    {
        "question": "Вы активнее всего рано утром или ночью?",
        "options": ["Я люблю встать пораньше, чтобы успеть сделать все дела",
                    "Ночью чувствую себя комфортно и люблю подольше поспать утром",
                    "Я не ложусь поздно, но и не встаю рано"]
    },
    {
        "question": "Какой пейзаж вам по душе?",
        "options": ["Пустыня",
                    "Лес",
                    "Заснеженные горы"]
    }
]

user_answers = {}

animal_mapping = {
    ("1", "2"): "Серый тюлень",
    ("1", "3"): "Викунья",
    ("2", "3"): "Дальневосточный леопард",
    ("2", "1"): "Чилийская свиязь",
    ("3", "1"): "Канадский овцебык",
    ("3", "2"): "Восточно-сибирская рысь",
    "1": "Двугорбый верблюд",
    "2": "Ушастый ёж",
    "3": "Амурский тигр"
}

animal_images = {
    "Серый тюлень": "images/Тюлень.jpeg",
    "Викунья": "images/Викунья.jpg",
    "Дальневосточный леопард": "images/Леопард.jpeg",
    "Чилийская свиязь": "images/Свиязь.jpg",
    "Канадский овцебык": "images/Овцебык.jpeg",
    "Восточно-сибирская рысь": "images/Рысь.jpeg",
    "Двугорбый верблюд": "images/Верблюд.jpeg",
    "Ушастый ёж": "images/Ёж.jpeg",
    "Амурский тигр": "images/Тигр.jpeg"
}

def send_main_menu(chat_id):
    keyboard = InlineKeyboardMarkup()
    start_button = InlineKeyboardButton(text="Начать", callback_data="start_quiz")
    keyboard.add(start_button)
    bot.send_message(chat_id, "Добро пожаловать! В данной викторине вам предлагается выяснить,"
" какое ваше тотемное животное из Московского зоопарка. Нажмите кнопку, чтобы начать викторину:", reply_markup=keyboard)

@bot.message_handler(commands=['start'])
def welcome(message):
    send_main_menu(message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data == "start_quiz")
def start_quiz(call):
    user_answers[call.message.chat.id] = []
    send_question(call.message.chat.id, 0)

def send_question(chat_id, question_index):
    if question_index < len(questions):
        question = questions[question_index]
        options = "\n".join([f"{i + 1}. {opt}" for i, opt in enumerate(question["options"])])
        bot.send_message(chat_id, f"{question['question']}\n{options}")
        bot.register_next_step_handler_by_chat_id(chat_id, lambda msg: handle_answer(msg, question_index))
    else:
        finish_quiz(chat_id)


def handle_answer(message, question_index):
    try:
        if message.text.isdigit() and 1 <= int(message.text) <= len(questions[question_index]["options"]):
            user_answers[message.chat.id].append(message.text)
            send_question(message.chat.id, question_index + 1)
        else:
            raise InvalidAnswerError("Неверный ввод. Пожалуйста, введите номер, соответствующий варианту ответа.")
    except InvalidAnswerError as e:
        bot.send_message(message.chat.id, str(e))
        send_question(message.chat.id, question_index)


def finish_quiz(chat_id):
    counts = Counter(user_answers[chat_id])
    most_common = counts.most_common()

    if most_common:
        most_popular = most_common[0][0]
        most_popular_count = most_common[0][1]

        if len(most_common) > 1 and most_common[0][1] == most_common[1][1]:
            second_popular = most_common[1][0]
            pair_key = (most_popular, second_popular)
            animal = animal_mapping.get(pair_key)

            if animal:
                send_animal_info(chat_id, animal)
        else:
            # Иначе, показываем животное для одного самого популярного ответа
            animal = animal_mapping.get(most_popular)

            if animal:
                send_animal_info(chat_id, animal)

    # Кнопка для перезапуска викторины
    send_restart_button(chat_id)
    send_feedback_button(chat_id)
    send_saport_button(chat_id)

def send_animal_info(chat_id, animal):
    bot.send_message(chat_id, f"Ваше тотемное животное: {animal}. Вы можете стать его опекуном, "
                              f"чтобы спонсировать его содержание, знать о всех подробностях его жизни "
                              f"и иметь доступ к постоянному его посещению. "
                              f"Все подробности вы можете узнать на нашем сайте: https://moscowzoo.ru/animals/kinds")
    if animal in animal_images:
        with open(animal_images[animal], 'rb') as photo:
            bot.send_photo(chat_id, photo)

def send_restart_button(chat_id):
    keyboard = InlineKeyboardMarkup()
    restart_button = InlineKeyboardButton(text="Пройти тест заново", callback_data="restart_quiz")
    keyboard.add(restart_button)
    bot.send_message(chat_id, "Хотите пройти викторину снова?", reply_markup=keyboard)

def send_feedback_button(chat_id):
    keyboard = InlineKeyboardMarkup()
    feedback_button = InlineKeyboardButton(text="Оставить отзыв", callback_data="feedback")
    keyboard.add(feedback_button)
    bot.send_message(chat_id, "Хотите оставить отзыв о боте?", reply_markup=keyboard)

def send_saport_button(chat_id):
    keyboard = InlineKeyboardMarkup()
    saport_button = InlineKeyboardButton(text="Написать нам", url='https://moscowzoo.ru/contacts')
    keyboard.add(saport_button)
    bot.send_message(chat_id, "Если у вас возникли вопросы или технические проблемы, "
"то вы можете написать в нашу поддержку.", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == "restart_quiz")
def handle_restart_quiz(call):
    start_quiz(call)

@bot.callback_query_handler(func=lambda call: call.data == "feedback")
def handle_feedback(call):
    bot.send_message(call.message.chat.id, "Пожалуйста, напишите ваш отзыв:")
    bot.register_next_step_handler(call.message, save_feedback)


def save_feedback(message):
    user_feedback = message.text  # Сохраните отзыв в переменной или базе данных
    bot.send_message(message.chat.id, "Спасибо за ваш отзыв! Мы его учтем.")

    # Кнопка для перезапуска викторины
    send_restart_button(message.chat.id)

if __name__ == "__main__":
    bot.polling(none_stop=True)