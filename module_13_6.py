from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

api = ""
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

# Клавиатура для начала
main_menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu_keyboard.add(KeyboardButton("Рассчитать"), KeyboardButton("Информация"))

# Инлайн клавиатура
inline_menu_kb = InlineKeyboardMarkup(resize_keyboard=True)
inline_menu_kb.add(InlineKeyboardButton("Рассчитать норму калорий", callback_data="calories"),
                   InlineKeyboardButton("Формулы расчёта", callback_data="formulas"))


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Привет! Я бот для расчёта калорий. Нажми на кнопку ниже, чтобы начать.",
                         reply_markup=main_menu_keyboard)


@dp.message_handler(lambda message: message.text.lower() == "рассчитать")
async def main_menu(message: types.Message):
    await message.answer("Выберите опцию:", reply_markup=inline_menu_kb)


@dp.callback_query_handler(lambda call: call.data == "formulas")
async def get_formulas(call: types.CallbackQuery):
    formula = (
        "Формула Миффлина-Сан Жеора (для мужчин):\n"
        "BMR = 10 × вес (кг) + 6.25 × рост (см) − 5 × возраст (лет) + 5\n\n"
        "Формула Миффлина-Сан Жеора (для женщин):\n"
        "BMR = 10 × вес (кг) + 6.25 × рост (см) − 5 × возраст (лет) − 161"
    )
    await call.message.answer(formula)
    await call.answer()


@dp.callback_query_handler(lambda call: call.data == "calories")
async def set_age(call: types.CallbackQuery):
    await call.message.answer("Введите свой возраст:")
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("Введите свой рост:")
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(growth=message.text)
    await message.answer("Введите свой вес:")
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    await state.update_data(weight=message.text)
    data = await state.get_data()

    # Преобразование данных в нужные типы
    age = int(data.get('age'))
    growth = int(data.get('growth'))
    weight = int(data.get('weight'))

    # Формула Миффлина - Сан Жеора (для мужчин)
    bmr1 = 10 * weight + 6.25 * growth - 5 * age + 5
    # Формула Миффлина - Сан Жеора (для женщин)
    bmr2 = 10 * weight + 6.25 * growth - 5 * age - 161

    await message.answer(f"Ваша норма калорий: {bmr1} ккалорий для мужчин.")
    await message.answer(f"Ваша норма калорий: {bmr2} ккалорий для женщин.")
    await state.finish()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
