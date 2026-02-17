import asyncio
import json
import os
import random
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

# =========================
# 1) ВСТАВЬ ТОКЕН СЮДА
# =========================
TOKEN = os.getenv("BOT_TOKEN", "8296203999:AAHNwH3hdU9qD-6GGVjSyF3PPO-dWfmuVHQ")

DATA_FILE = "sabina_bot_data.json"

# ---- Контент ----
JOKES = [
    "Если бы у улыбки был Wi‑Fi — у тебя был бы самый сильный сигнал 😄",
    "Сабина, ты как кнопка «пропустить рекламу» — появляешься и жизнь сразу лучше 😌",
    "Сейчас официально: твоё настроение — национальное достояние 👑",
    "Ты настолько классная, что даже чай заваривается с уважением ☕",
    "Проверка связи: Сабина? — Принято. Уровень милоты: критический 💥",
]

COMPLIMENTS = [
    "Сабина, ты умеешь делать день легче — даже когда он тяжёлый 💛",
    "Твоя улыбка — как сохранёнка в игре: хочется возвращаться 😄",
    "Ты супер-человечная. Это редкость и очень ценится ✨",
    "С тобой спокойно. Это прям дар 💫",
    "Ты красивая так, что мир становится чуть добрее 🌷",
]

PREDICTIONS = [
    "Сегодня тебя ждёт маленькая победа и большая улыбка 🙂",
    "Кто-то подумает о тебе с теплом (спойлер: уже думают) 💛",
    "День принесёт приятный сюрприз: случайный комплимент + настроение вверх 📈",
    "Скоро появится повод сказать: «ну вот, я так и знала» 😎",
    "Сегодня ты точно сделаешь что-то классное, даже если не заметишь этого сразу ✨",
]

GIFT_STEPS = {
    1: ("Шаг 1/3: Выбери кнопку настроения 😄", [("Я — солнышко ☀️", "gift_1_sun"), ("Я — богиня 🌙", "gift_1_moon")]),
    2: ("Шаг 2/3: Выбери суперсилу на сегодня:", [("Очарование x100 💘", "gift_2_charm"), ("Спокойствие уровня «дзен» 🧘‍♀️", "gift_2_zen")]),
    3: ("Шаг 3/3: Финальный выбор:", [("Открыть милоту 🎀", "gift_3_cute"), ("Открыть смешинку 😂", "gift_3_fun")]),
}

# ---- Хранилище (простое) ----
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user(data, user_id: int):
    uid = str(user_id)
    if uid not in data:
        data[uid] = {"joy": 0, "secret_unlocked": False, "gift_step": 0}
    return data[uid]

# ---- Клавиатуры ----
def main_menu_kb(user_state: dict):
    kb = InlineKeyboardBuilder()
    kb.button(text="🎁 Открыть подарок", callback_data="gift_start")
    kb.button(text="😂 Кнопка «поржать»", callback_data="joke")
    kb.button(text="💌 Комплимент Сабине", callback_data="compliment")
    kb.button(text="🔮 Предсказание на сегодня", callback_data="predict")
    kb.button(text=f"📈 Радость: {user_state['joy']}", callback_data="joy")
    if user_state.get("secret_unlocked"):
        kb.button(text="🐾 Секретная кнопка", callback_data="secret")
    kb.adjust(1)
    return kb.as_markup()

def gift_step_kb(step: int):
    text, buttons = GIFT_STEPS[step]
    kb = InlineKeyboardBuilder()
    for t, cd in buttons:
        kb.button(text=t, callback_data=cd)
    kb.button(text="⬅️ В меню", callback_data="menu")
    kb.adjust(1)
    return text, kb.as_markup()

# ---- Бот ----
bot = Bot(TOKEN)
dp = Dispatcher()

@dp.message(F.text.in_({"/start", "старт", "меню", "menu"}))
async def start(message: Message):
    data = load_data()
    st = get_user(data, message.from_user.id)
    save_data(data)

    text = (
        "Привет! Это маленький подарочный бот для Сабины 🎀\\n\\n"
        "Тут есть смешные кнопки, милота и мини-квест.\\n"
        "Выбирай, куда нажать ↓"
    )
    await message.answer(text, reply_markup=main_menu_kb(st))

@dp.callback_query(F.data == "menu")
async def back_to_menu(call: CallbackQuery):
    data = load_data()
    st = get_user(data, call.from_user.id)
    save_data(data)
    await call.message.edit_text("Меню 🎛️ Выбирай кнопку:", reply_markup=main_menu_kb(st))
    await call.answer()

@dp.callback_query(F.data == "joke")
async def joke(call: CallbackQuery):
    data = load_data()
    st = get_user(data, call.from_user.id)
    st["joy"] += 1
    # Пасхалка: открыть секрет после 5 радостей
    if st["joy"] >= 5:
        st["secret_unlocked"] = True
    save_data(data)

    await call.message.edit_text(
        f"😂 {random.choice(JOKES)}\\n\\nНажимай ещё или возвращайся в меню:",
        reply_markup=main_menu_kb(st)
    )
    await call.answer("Ха! +1 радость")

@dp.callback_query(F.data == "compliment")
async def compliment(call: CallbackQuery):
    data = load_data()
    st = get_user(data, call.from_user.id)
    st["joy"] += 1
    if st["joy"] >= 5:
        st["secret_unlocked"] = True
    save_data(data)

    await call.message.edit_text(
        f"💌 {random.choice(COMPLIMENTS)}\\n\\nХочешь ещё кнопок?",
        reply_markup=main_menu_kb(st)
    )
    await call.answer("Мило! +1 радость")

@dp.callback_query(F.data == "predict")
async def predict(call: CallbackQuery):
    data = load_data()
    st = get_user(data, call.from_user.id)
    st["joy"] += 1
    if st["joy"] >= 5:
        st["secret_unlocked"] = True
    save_data(data)

    await call.message.edit_text(
        f"🔮 {random.choice(PREDICTIONS)}\\n\\nВернуться в меню?",
        reply_markup=main_menu_kb(st)
    )
    await call.answer("О-о-о! +1 радость")

@dp.callback_query(F.data == "joy")
async def joy(call: CallbackQuery):
    data = load_data()
    st = get_user(data, call.from_user.id)
    save_data(data)

    await call.message.edit_text(
        f"📈 Уровень радости сейчас: {st['joy']}.\\n\\n"
        "Подсказка: чем больше радости, тем больше секретов 😉",
        reply_markup=main_menu_kb(st)
    )
    await call.answer()

# ---- Подарок / квест ----
@dp.callback_query(F.data == "gift_start")
async def gift_start(call: CallbackQuery):
    data = load_data()
    st = get_user(data, call.from_user.id)
    st["gift_step"] = 1
    save_data(data)

    text, kb = gift_step_kb(1)
    await call.message.edit_text("🎁 Открываем подарок!\\n\\n" + text, reply_markup=kb)
    await call.answer("Поехали!")

@dp.callback_query(F.data.startswith("gift_"))
async def gift_flow(call: CallbackQuery):
    data = load_data()
    st = get_user(data, call.from_user.id)

    # шаги: 1->2->3->финал
    if st["gift_step"] == 1:
        st["gift_step"] = 2
        st["joy"] += 1
        save_data(data)
        text, kb = gift_step_kb(2)
        await call.message.edit_text("🎁 Отлично!\\n\\n" + text, reply_markup=kb)
        await call.answer("+1 радость")

    elif st["gift_step"] == 2:
        st["gift_step"] = 3
        st["joy"] += 1
        save_data(data)
        text, kb = gift_step_kb(3)
        await call.message.edit_text("🎁 Ещё чуть-чуть!\\n\\n" + text, reply_markup=kb)
        await call.answer("+1 радость")

    elif st["gift_step"] == 3:
        st["gift_step"] = 0
        st["joy"] += 2
        if st["joy"] >= 5:
            st["secret_unlocked"] = True
        save_data(data)

        if call.data == "gift_3_cute":
            final = (
                "🎀 *Подарок открыт!*\\n\\n"
                "Сабина, это маленькое напоминание:\\n"
                "ты — очень тёплый человек, с которым рядом спокойнее.\\n"
                "И да… ты реально умеешь делать людей счастливее 💛"
            )
        else:
            final = (
                "😂 *Подарок открыт!*\\n\\n"
                "Срочно объявляю:\\n"
                "Сабина официально назначена главной причиной хорошего настроения.\\n"
                "Сопротивление бесполезно 😄"
            )

        await call.message.edit_text(final, parse_mode="Markdown", reply_markup=main_menu_kb(st))
        await call.answer("Подарок! +2 радости")

# ---- Секрет ----
@dp.callback_query(F.data == "secret")
async def secret(call: CallbackQuery):
    data = load_data()
    st = get_user(data, call.from_user.id)
    st["joy"] += 3
    save_data(data)

    await call.message.edit_text(
        "🐾 *Секретная кнопка активирована!*\\n\\n"
        "Ты дошла до пасхалки.\\n"
        "Если бы это был квест, сейчас бы выпал легендарный лут: «Обнимашка +10» 🤍",
        parse_mode="Markdown",
        reply_markup=main_menu_kb(st)
    )
    await call.answer("Секрет найден!")

async def main():
    if TOKEN == "PASTE_YOUR_TOKEN_HERE":
        print("ОШИБКА: Вставь токен в переменную TOKEN (в начале файла) или задай BOT_TOKEN.")
        return
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
