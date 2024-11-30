from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, CallbackContext
import random

# Определяем этапы диалога
QUESTION1, QUESTION2, QUESTION3 = range(3)

# Списки дел
tasks = {
    ('улица', '30', 'делать'): ['Прогулка по парку около 30 мин', 'Сделать уборку на улице','123','123445123','sdfsdfsdf'],
    ('улица', '30', 'думать'): ['Подумать о проекте на свежем воздухе', 'Провести мозговой штурм в кафе'],
    ('улица', '60', 'делать'): ['Пойти на длительную прогулку', 'Сделать домашнее задание в парке'],
    ('улица', '60', 'думать'): ['Писать статьи в парке', 'Подумать о новых идеях для стартапа'],
    ('дом', '30', 'делать'): ['Приготовить ужин', 'Убрать в комнате'],
    ('дом', '30', 'думать'): ['Почитать книгу', 'Написать план на завтра'],
    ('дом', '60', 'делать'): ['Сделать проект'],
    ('дом', '60', 'думать'): ['Разработать новые идеи', 'Продумать свои цели'],
}


# Начало диалога
def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Привет! Нужна помощь? Давай выясним, что тебе нужно. Нужно дело на улице или дома?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Улица", callback_data='улица'),
             InlineKeyboardButton("Дом", callback_data='дом')]
        ])
    )
    return QUESTION1


def question1(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    context.user_data['location'] = query.data
    query.answer()

    query.edit_message_text(text="Отлично! Как долго это должно занять? (30 / 60)",
                            reply_markup=InlineKeyboardMarkup([
                                [InlineKeyboardButton("30", callback_data='30'),
                                 InlineKeyboardButton("60", callback_data='60')]
                            ]))

    return QUESTION2


def question2(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    context.user_data['duration'] = query.data
    query.answer()

    query.edit_message_text(text="Что именно ты хочешь сделать?",
                            reply_markup=InlineKeyboardMarkup([
                                [InlineKeyboardButton("Думать", callback_data='думать'),
                                 InlineKeyboardButton("Делать", callback_data='делать')]
                            ]))

    return QUESTION3


def question3(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    action = query.data
    context.user_data['action'] = action
    query.answer()

    location = context.user_data.get('location')
    duration = context.user_data.get('duration')

    if location and duration and action:
        selected_tasks = tasks.get((location, duration, action), [])

        # Инициализируем список предыдущих задач, если он отсутствует
        if 'previous_tasks' not in context.user_data:
            context.user_data['previous_tasks'] = []

        previous_tasks = context.user_data['previous_tasks']
        remaining_tasks = [task for task in selected_tasks if task not in previous_tasks]

        if remaining_tasks:
            chosen_task = random.choice(remaining_tasks)
            previous_tasks.append(chosen_task)  # Сохраняем новую задачу в предыдущие
            context.user_data['previous_tasks'] = previous_tasks  # Обновляем список

            # Кнопка "Придумай еще"
            keyboard = [[InlineKeyboardButton("Придумай еще", callback_data='repeat')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(text=f"Как насчет этого дела: \n {chosen_task}?", reply_markup=reply_markup)
        else:
            # Если не осталось задач, начинаем заново
            query.edit_message_text(text="Не осталось доступных задач. Давайте попробуем снова.")
            return start(update, context)
    else:
        query.edit_message_text(text="Произошла ошибка. Попробуйте еще раз.")
        return ConversationHandler.END  # Завершить разговор в случае ошибки


def repeat_task(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    return QUESTION3(update, context)  # Запрос снова выполнения задачи


def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Диалог завершен. Напишите /start, чтобы начать заново.')
    return ConversationHandler.END


def main():
    updater = Updater("8123045383:AAESEC7SH6ZS2FgEWEQNlCre-oZGpKcdppE")  # Ваш токен
    dispatcher = updater.dispatcher

    # Создаем обработчик разговоров
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            QUESTION1: [CallbackQueryHandler(question1)],
            QUESTION2: [CallbackQueryHandler(question2)],
            QUESTION3: [CallbackQueryHandler(question3)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CallbackQueryHandler(repeat_task, pattern='repeat'))  # Обработчик для кнопки "Придумай еще"

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()