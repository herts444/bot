import sqlite3
from aiogram import executor, types, Bot, Dispatcher
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.contrib.fsm_storage.memory import MemoryStorage


# __________________________Данные бота__________________________
admin_id = 5217052048  # Id админа
token = "6083696772:AAG_vW3QL34ljD3s_6nC6UTIs1_-jqRYEnA"  # Токен бота
chat_link = "https://t.me/+h1l-kqHt-q0zMmJi"  # Ссылка на чат
bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
# __________________________Вопросы__________________________
question_1 = "👏 Зарегистрируйте новый аккаунт <b>MELBET</b> по ссылке: \n\n " \
             "http://surl.li/eozol \n\n 👨‍💻И введите промокод: <code>EURO500</code> <i>(После выполнения напишите: Готово )</i>"
question_2 = "<b> Пополните счет для нашей будущей работы! </b> \n\n " \
             "💰 Укажите сумму вашего депозита: (Например: <u>500 грн</u>)"
question_3 = "<b> Укажите ID вашего аккаунта MELBET: </b>"
# __________________________Отображение вопросов у админа__________________________
admin_question_1 = "Аккаунт"
admin_question_2 = "Депозит"
admin_question_3 = "ID"
# _________________________________________________________


# __________________________Действие при старте бота__________________________
async def on_startup(_):
    print("BOT STARTED")
# _________________________________________________________


# __________________________Действие с БД__________________________
class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        print("The database is connected successfully")

    def add_user(self, ID, username):
        with self.connection:
            try:
                self.cursor.execute("INSERT INTO 'user' VALUES (?, ?, ?, ?, ?)", (ID, "null", "null", "null", username))
            except: pass

    def add_client(self, ID):
        with self.connection:
            try:
                self.cursor.execute("INSERT INTO 'client' VALUES (?)", (ID,))
            except: pass

    def update_user_data(self, ID, a1, a2, a3):
        with self.connection:
            self.cursor.execute("UPDATE 'user' SET answer1 = ?, answer2 = ?, answer3 = ? WHERE user_id = ?", (a1, a2, a3, ID))

    def get_user_data(self, ID):
        with self.connection:
            return self.cursor.execute("SELECT * FROM 'user' WHERE user_id = ?", (ID,)).fetchmany()[0]

    def delete_zayavka(self, ID):
        with self.connection:
            return self.cursor.execute("DELETE FROM 'user' WHERE user_id = ?", (ID,))

    def client_exists(self, ID):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM 'user' WHERE user_id = ?", (ID,)).fetchmany(1)
            if not bool(len(result)):
                return False
            else: return True

    def confirmed_user(self, ID):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM 'client' WHERE user_id = ?", (ID,)).fetchmany(1)
            if not bool(len(result)):
                return False
            else: return True
# _________________________________________________________

# __________________________Кнопки__________________________
cb = CallbackData("fabnum", "action")

main_menu = InlineKeyboardMarkup(row_width=1)
main_menu.add(InlineKeyboardButton(text='Подать заявку 🎫', callback_data=cb.new(action='start_answer')))

send_menu = InlineKeyboardMarkup(row_width=2)
send_menu.add(InlineKeyboardButton(text="Отправить 🤝", callback_data=cb.new(action="send")),
              InlineKeyboardButton(text="Заполнить заново 👎", callback_data=cb.new(action='application')))


def admin_menu(ID):
    menu = InlineKeyboardMarkup(row_width=2)
    menu.add(InlineKeyboardButton(text="Одобрить ✅", callback_data=f"#y{str(ID)}"),
             InlineKeyboardButton(text="Отклонить ❌", callback_data=f'#n{str(ID)}'))
    return menu
# _________________________________________________________

# __________________________Подключаем БД__________________________
db = Database("data.db")
# _________________________________________________________


class get_answer(StatesGroup):
    answer1 = State()
    answer2 = State()
    answer3 = State()


# ____________________________________________________
# @dp.message_handlers(commands=["start"])
async def command_start(message: types.Message):  # Действие при /start
    if message.from_user.username is not None:
        if db.confirmed_user(message.from_user.id):
            await bot.send_message(message.from_user.id, "❇ Вы уже приняты 👍")
        else:
            if db.client_exists(message.from_user.id):
                await bot.send_message(message.from_user.id, "Вы уже подавали заявку ❌")
            else:
                await bot.send_message(message.from_user.id,
                                       "👋 Привет! Для получения тестового доступа тебе необходимо заполнить небольшую заявку. ️\n \n Учти, ответ должен быть корректным, иначе заявка будет отклонена :(",  # Приветственное сообщение
                                       reply_markup=main_menu)
    else:
        await bot.send_message(message.from_user.id, "У вас не установлен <b>username</b>(имя пользователя)\n\nУстановите его и напишите /start", parse_mode=types.ParseMode.HTML)


# @dp.callback_query_handlers(cb.filter(action=["send", "application"]), state="*")
async def send_state(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    action = callback_data["action"]
    current_state = await state.get_state()
    if current_state is None:
        return
    if action == "send":
        await bot.send_message(admin_id, f"Поступила новая заявка от @{str(db.get_user_data(call.from_user.id)[4])}\n"
                                         f"{admin_question_1}: <b>{str(db.get_user_data(call.from_user.id)[1])}</b>\n"
                                         f"{admin_question_2}: <b>{str(db.get_user_data(call.from_user.id)[2])}</b>\n"
                                         f"{admin_question_3}: <b>{str(db.get_user_data(call.from_user.id)[3])}</b>", parse_mode=types.ParseMode.HTML, reply_markup=admin_menu(call.from_user.id))
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text="✅ Ваша заявка успешно отправленна, ожидайте!")
        await state.finish()
    if action == "application":
        db.delete_zayavka(call.from_user.id)
        await state.finish()
        await command_start(call)
    await call.answer()


# @dp.callback_query_handler(text_contains="#")
async def access(call: types.CallbackQuery):  # Обработка заявки
    temp = [call.data[1:2], call.data[2:]]
    if temp[0] == "y":
        db.add_client(temp[1])
        db.delete_zayavka(temp[1])
        await bot.edit_message_text(chat_id=admin_id, message_id=call.message.message_id, text="Вы приняли заявку✅")
        await bot.send_message(temp[1], f'Добро пожаловать в команду! ✅\n \n'
                                        f'🔖 Ваше приглашение: {chat_link} \n \n', disable_web_page_preview=True, parse_mode=types.ParseMode.HTML)
    elif temp[0] == "n":
        await bot.edit_message_text(chat_id=admin_id, message_id=call.message.message_id, text="Вы отклонили заявку❌")
        await bot.send_message(temp[1], '❌ Вы не выполнили одно из условий, отправьте корректную заявку!', reply_markup=main_menu)

    await call.answer()


# @dp.callback_query_handlers(cb.filter(action=["start_answer"]))
async def start_state(call: types.CallbackQuery, callback_data: dict):  # Первый вопрос
    action = callback_data["action"]
    if action == "start_answer":
        db.add_user(call.from_user.id, call.from_user.username)
        await bot.send_message(call.from_user.id, f"• <b>Подтвердите выполнение:</b>\n\n {question_1}", parse_mode=types.ParseMode.HTML)
        await get_answer.answer1.set()


# @dp.message_handlers(state=get_answer.answer1)
async def answer1(message: types.Message, state: FSMContext):  # Второй вопрос
    async with state.proxy() as data:
        data["answer1"] = message.text
    await bot.send_message(message.from_user.id, f' ✅ {question_2}', parse_mode=types.ParseMode.HTML)
    await get_answer.next()


# @dp.message_handlers(state=get_answer.answer2)
async def answer2(message: types.Message, state: FSMContext):  # Третий вопрос
    async with state.proxy() as data:
        data["answer2"] = message.text
    await bot.send_message(message.from_user.id, f'🎲 {question_3}', parse_mode=types.ParseMode.HTML)
    await get_answer.next()


# @dp.message_handlers(state=get_answer.answer3)
async def answer3(message: types.Message, state: FSMContext):  # Отображение ответов на вопросы
    async with state.proxy() as data:
        data["answer3"] = message.text
    await bot.send_message(message.from_user.id, f'Отправить запрос менеджеру:\n\n'
                                                 f'🆕 <b> Создан новый аккаунт: </b>{data["answer1"]}\n'
                                                 f'💰 <b> Мой депозит: </b>{data["answer2"]}\n'
                                                 f'🆔 <b> Мой ID: </b>{data["answer3"]}', parse_mode=types.ParseMode.HTML, reply_markup=send_menu)
    db.update_user_data(message.from_user.id, data["answer1"], data["answer2"], data["answer3"])
# _________________________________________________________


# __________________________Обработка всех событий__________________________
def register_handlers_client(dp: Dispatcher):
    dp.register_callback_query_handler(send_state, cb.filter(action=["send", "application"]), state="*")
    dp.register_message_handler(command_start, commands=["start"])
    dp.register_callback_query_handler(access, text_contains="#")
    dp.register_callback_query_handler(start_state, cb.filter(action=["start_answer"]))
    dp.register_message_handler(answer1, state=get_answer.answer1)
    dp.register_message_handler(answer2, state=get_answer.answer2)
    dp.register_message_handler(answer3, state=get_answer.answer3)
# _________________________________________________________


register_handlers_client(dp)  # Запуск обработки событий


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)
