import asyncio
import nest_asyncio
from flask import Flask
from pyngrok import ngrok
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config.settings import (
    TELEGRAM_TOKEN,
    NGROK_TOKEN,
    SERVER_HOST,
    SERVER_PORT,
    WEBHOOK_PATH,
)
from bot.handlers.base_handlers import start_handler, help_handler,echo_handler
from bot.handlers.calculator_handlers import calc_handler
from bot.routes.webhook_routes import webhook, init_routes
# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()


def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.register_blueprint(webhook)
    return app


def main():
    # Create a persistent event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Initialize bot application
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.loop = loop  # Store loop reference for webhook routes

    # Setup handlers
    setup_handlers(application)
    loop.run_until_complete(application.initialize())
    loop.run_until_complete(application.start())

    # Setup ngrok
    ngrok.set_auth_token(NGROK_TOKEN)

    public_url = ngrok.connect(SERVER_PORT).public_url

    webhook_url = f"{public_url}{WEBHOOK_PATH}"
    print(f"Webhook URL: {webhook_url}")

    # Set webhook
    loop.run_until_complete(application.bot.set_webhook(webhook_url))

    # Create Flask app and initialize routes
    app = create_app()
    init_routes(application)

    try:
        app.run(host=SERVER_HOST, port=SERVER_PORT)
    finally:
        loop.run_until_complete(application.stop())
        loop.close()


if __name__ == "__main__":
    print("hello")
    main() #non entra qui di base


def setup_handlers(application):
    """Setup all the bot command handlers"""
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("calc", calc_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_handler))


#@webhook.route("/")
#def index():
 #   """Root endpoint to check if the bot is active"""
    #main()
  #  return "Bot is up and running!"