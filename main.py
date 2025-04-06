from flask import Flask, request
import openai
from telegram import Bot, Update
from telegram.ext import Dispatcher, MessageHandler, Filters
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

bot = Bot(token=TELEGRAM_TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)
openai.api_key = OPENAI_API_KEY

def analizar_estrategia(prompt):
    system_prompt = (
        "Actúa como un mentor experto en Smart Money Concept (SMC) y Fair Value Gaps (FVG). "
        "Corrige setups de trading, explica errores y da consejos como un mentor humano."
    )

    respuesta = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )
    return respuesta['choices'][0]['message']['content']

def handle_message(update: Update, context):
    chat_id = update.effective_chat.id
    msg = update.message.text

    if msg.startswith("#analizar"):
        prompt = msg.replace("#analizar", "").strip()
        reply = analizar_estrategia(prompt)
        context.bot.send_message(chat_id=chat_id, text=reply)
    else:
        context.bot.send_message(chat_id=chat_id, text="Usa el comando #analizar seguido de tu análisis.")

dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

@app.route('/')
def home():
    return '✅ Bot activo'

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'

if __name__ == '__main__':
    app.run(debug=False)
