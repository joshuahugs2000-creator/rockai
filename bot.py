import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configuration du logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Fonction pour répondre aux questions (version gratuite avec API simple)
def ask_ai(question: str) -> str:
    """Génère une réponse intelligente à la question"""
    try:
        # Ici on utilise une API gratuite - vous pourrez la changer plus tard
        # Pour l'instant, réponse simple
        return f"J'ai bien reçu votre question : '{question}'. Je suis un bot en développement et je peux répondre à vos questions !"
    except Exception as e:
        logger.error(f"Erreur: {e}")
        return "Désolé, une erreur s'est produite."

# Commande /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Envoie un message de bienvenue"""
    await update.message.reply_text(
        "👋 Bonjour ! Je suis un bot intelligent.\n\n"
        "💬 Posez-moi n'importe quelle question !\n\n"
        "📌 Commandes :\n"
        "/start - Afficher ce message\n"
        "/help - Obtenir de l'aide\n\n"
        "Dans les groupes, mentionnez-moi ou répondez à mes messages."
    )

# Commande /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Envoie un message d'aide"""
    await update.message.reply_text(
        "🤖 Comment m'utiliser :\n\n"
        "• En privé : envoyez votre question\n"
        "• En groupe : mentionnez-moi (@votre_bot)\n\n"
        "Je réponds à toutes vos questions !"
    )

# Gestion des messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Traite les messages reçus"""
    message = update.message
    should_respond = False
    
    # En conversation privée
    if message.chat.type == 'private':
        should_respond = True
    else:
        # Dans les groupes
        bot_username = context.bot.username
        if message.reply_to_message and message.reply_to_message.from_user.id == context.bot.id:
            should_respond = True
        elif message.text and f"@{bot_username}" in message.text:
            should_respond = True
    
    if should_respond:
        question = message.text
        if context.bot.username:
            question = question.replace(f"@{context.bot.username}", "").strip()
        
        await message.chat.send_action(action="typing")
        response = ask_ai(question)
        await message.reply_text(response)

# Gestion des erreurs
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère les erreurs"""
    logger.error(f"Erreur: {context.error}")

def main():
    """Démarre le bot"""
    TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    
    if not TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN non défini !")
        return
    
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    logger.info("🚀 Bot démarré !")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
