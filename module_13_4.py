# Домашнее задание по теме "Машина состояний".
# ВНИМАНИЕ: Данный код разработан в учебных целях, комментарии добавлены для себя!!!

from aiogram import Bot, Dispatcher, types  # Импортируем классы Bot, Dispatcher и типы сообщений
from aiogram.contrib.fsm_storage.memory import MemoryStorage  # Импортируем MemoryStorage для хранения состояний
from aiogram.dispatcher import FSMContext  # Импортируем контекст состояний
from aiogram.dispatcher.filters.state import State, StatesGroup  # Импортируем классы для описания состояний
from aiogram.utils import executor  # Импортируем утилиту для запуска long polling

api = ""  # Токен нашего бота

# Инициализация бота и диспетчера
bot = Bot(token=api)  # Создаём объект бота, используя наш токен
storage = MemoryStorage()  # Создаём объект MemoryStorage для хранения состояний
dp = Dispatcher(bot, storage=storage)  # Создаём объект диспетчера, связывая его с ботом и хранилищем состояний

# Создаем группу состояний
class UserState(StatesGroup):  # Наследуемся от StatesGroup для создания группы состояний
    age = State()  # Состояние для хранения возраста
    growth = State()  # Состояние для хранения роста
    weight = State()  # Состояние для хранения веса

@dp.message_handler(commands = ['start'])
async def start_message(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.')

# Функция для запуска цепочки
@dp.message_handler(text = ['Calories'])  # Декорируем функцию для обработки ожидания слова 'Calories'
async def set_age(message: types.Message):  # Асинхронная функция для обработки команды
    await message.answer('Введите свой возраст:')  # Отправляем сообщение с просьбой ввести возраст
    await UserState.age.set()  # Переводим пользователя в состояние ожидания ввода возраста

@dp.message_handler()
async def all_message(message):
    await message.answer("Введите команду /start, чтобы начать общение.")

# Обработка возраста
@dp.message_handler(state=UserState.age)  # Декорируем функцию для обработки состояния 'age'
async def set_growth(message: types.Message, state: FSMContext):  # Асинхронная функция для обработки возраста
    await state.update_data(age=int(message.text))  # Сохраняем возраст в контексте состояний
    await message.answer('Введите свой рост:')  # Отправляем сообщение с просьбой ввести рост
    await UserState.next()  # Переходим к следующему состоянию 'growth'

# Обработка роста
@dp.message_handler(state=UserState.growth)  # Декорируем функцию для обработки состояния 'growth'
async def set_weight(message: types.Message, state: FSMContext):  # Асинхронная функция для обработки роста
    await state.update_data(growth=float(message.text))  # Сохраняем рост в контексте состояний
    await message.answer('Введите свой вес:')  # Отправляем сообщение с просьбой ввести вес
    await UserState.next()  # Переходим к следующему состоянию 'weight'

# Обработка веса и расчет нормы калорий
@dp.message_handler(state=UserState.weight)  # Декорируем функцию для обработки состояния 'weight'
async def send_calories(message: types.Message, state: FSMContext):  # Асинхронная функция для обработки веса
    await state.update_data(weight=float(message.text))  # Сохраняем вес в контексте состояний

    # Получаем все сохраненные данные
    user_data = await state.get_data()  # Извлекаем все данные из контекста состояний
    age = user_data['age']  # Извлекаем возраст
    growth = user_data['growth']  # Извлекаем рост
    weight = user_data['weight']  # Извлекаем вес

    # Расчет нормы калорий по формуле Миффлина-Сан Жеора для мужчин
    calories_norm = 10 * weight + 6.25 * growth - 5 * age + 5  # Рассчитываем норму калорий

    await message.answer(f"Ваша норма калорий: {calories_norm:.2f}")  # Отправляем сообщение с результатом

    # Завершаем машину состояний
    await state.finish()  # Завершаем работу с машиной состояний

if __name__ == '__main__':  # Проверка, что файл запущен напрямую, а не импортирован
    executor.start_polling(dp, skip_updates=True)  # Запускаем long polling для обработки сообщений
