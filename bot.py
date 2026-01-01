import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def ask_ai(question: str) -> str:
    """Utilise l'API Hugging Face pour répondre intelligemment"""
    try:
        api_token = os.environ.get('HUGGINGFACE_TOKEN')
        if not api_token:
            return "❌ Token Hugging Face manquant."
        
        # API Hugging Face Inference (gratuite)
        api_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        headers = {"Authorization": f"Bearer {api_token}"}
        
        payload = {
            "inputs": question,
            "parameters": {
                "max_length": 200,
                "temperature": 0.7
            }
        }
        
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', 'Désolé, je n\'ai pas pu générer une réponse.')
            return "Je traite votre question..."
        else:
            logger.error(f"Erreur API: {response.status_code} - {response.text}")
            return f"Votre question: {question}\n\nJe suis un bot intelligent propulsé par IA ! 🤖"
            
    except Exception as e:
        logger.error(f"Erreur: {e}")
        return "Une erreur s'est produite. Réessayez !"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Salut ! Je suis RockAI, votre assistant intelligent.\n\n"
        "💬 Posez-moi vos questions, je réponds grâce à l'IA !\n\n"
        "📌 Commandes : /start | /help"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Comment m'utiliser :\n\n"
        "• En privé : envoyez votre message directement\n"
        "• En groupe : mentionnez-moi @votre_bot ou répondez à mes messages\n\n"
        "Je suis propulsé par l'IA Hugging Face ! 🚀"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    should_respond = False
    
    if message.chat.type == 'private':
        should_respond = True
    else:
        bot_username = context.bot.username
        if message.reply_to_message and message.reply_to_message.from_user.id == context.bot.id:
            should_respond = True
        elif message.text and bot_username and f"@{bot_username}" in message.text:
            should_respond = True
    
    if should_respond:
        question = message.text
        if context.bot.username:
            question = question.replace(f"@{context.bot.username}", "").strip()
        
        await message.chat.send_action(action="typing")
        response = ask_ai(question)
        await message.reply_text(response)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Erreur: {context.error}")

def main():
    TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    
    if not TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN manquant !")
        return
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    
    logger.info("🚀 Bot RockAI démarré avec IA Hugging Face !")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
