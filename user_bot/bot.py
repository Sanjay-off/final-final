"""
User Bot Main Module
Main entry point for the user bot application.
Initializes and runs the Telegram user bot for file distribution.
"""

import logging
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

# Import configuration
from config.settings import USER_BOT_TOKEN

# Import handlers
from user_bot.handlers import (
    start_handler,
    download_handler,
    verification_handler,
    callbacks_handler
)

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# Global application instance
user_application = None


def setup_handlers(application: Application) -> None:
    """
    Setup all handlers for the user bot.
    
    Args:
        application: Telegram application instance
    """
    logger.info("Setting up user bot handlers...")
    
    # Start handler (CommandHandler)
    application.add_handler(start_handler)
    
    # Download handlers (if list)
    if isinstance(download_handler, list):
        for handler in download_handler:
            application.add_handler(handler)
    elif download_handler:
        application.add_handler(download_handler)
    
    # Verification handlers (list of CallbackQueryHandlers)
    if isinstance(verification_handler, list):
        for handler in verification_handler:
            application.add_handler(handler)
    elif verification_handler:
        application.add_handler(verification_handler)
    
    # Callback handlers (list of CallbackQueryHandlers)
    if isinstance(callbacks_handler, list):
        for handler in callbacks_handler:
            application.add_handler(handler)
    elif callbacks_handler:
        application.add_handler(callbacks_handler)
    
    logger.info("User bot handlers setup complete")


async def post_init(application: Application) -> None:
    """
    Post initialization tasks.
    
    Args:
        application: Telegram application instance
    """
    logger.info("Running post-initialization tasks...")
    
    # Set bot commands (visible in menu)
    try:
        commands = [
            ("start", "Start the bot"),
        ]
        
        await application.bot.set_my_commands(commands)
        logger.info(f"Set {len(commands)} bot commands")
    except Exception as e:
        logger.error(f"Failed to set bot commands: {e}")
    
    # Log bot info
    bot_info = await application.bot.get_me()
    logger.info(f"User Bot started: @{bot_info.username} (ID: {bot_info.id})")
    
    # Connect to database
    try:
        from config.database import connect_database
        connect_database()
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")


async def post_shutdown(application: Application) -> None:
    """
    Post shutdown cleanup tasks.
    
    Args:
        application: Telegram application instance
    """
    logger.info("Running post-shutdown cleanup...")
    
    # Close database connection
    try:
        from config.database import close_database
        close_database()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")
    
    logger.info("User bot stopped")


async def error_handler(update: object, context) -> None:
    """
    Handle errors in the bot.
    
    Args:
        update: Update object
        context: Context object
    """
    logger.error(f"Exception while handling an update: {context.error}", exc_info=context.error)
    
    # Try to notify user if possible
    try:
        if update and hasattr(update, 'effective_message') and update.effective_message:
            await update.effective_message.reply_text(
                "❌ An error occurred while processing your request. Please try again later."
            )
    except:
        pass


def create_user_application() -> Application:
    """
    Create and configure the user bot application.
    
    Returns:
        Configured Application instance
    """
    logger.info("Creating user bot application...")
    
    # Create application
    application = (
        Application.builder()
        .token(USER_BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Setup handlers
    setup_handlers(application)
    
    return application


def get_user_application() -> Application:
    """
    Get the user bot application instance.
    Creates it if it doesn't exist.
    
    Returns:
        Application instance
    """
    global user_application
    
    if user_application is None:
        user_application = create_user_application()
    
    return user_application


async def start_user_bot() -> None:
    """
    Start the user bot.
    This function initializes and runs the bot.
    """
    global user_application
    
    try:
        logger.info("Starting User Bot...")
        
        # Create application
        user_application = create_user_application()
        
        # Start polling
        logger.info("User bot polling started")
        await user_application.run_polling(
            allowed_updates=[
                "message",
                "callback_query",
                "edited_message"
            ],
            drop_pending_updates=True
        )
        
    except Exception as e:
        logger.error(f"Error starting user bot: {e}", exc_info=True)
        raise


async def stop_user_bot() -> None:
    """
    Stop the user bot gracefully.
    """
    global user_application
    
    try:
        if user_application:
            logger.info("Stopping User Bot...")
            await user_application.stop()
            await user_application.shutdown()
            user_application = None
            logger.info("User Bot stopped successfully")
    
    except Exception as e:
        logger.error(f"Error stopping user bot: {e}", exc_info=True)


def run_user_bot() -> None:
    """
    Run the user bot (blocking).
    This is a convenience function for running the bot standalone.
    """
    import asyncio
    
    try:
        asyncio.run(start_user_bot())
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
        asyncio.run(stop_user_bot())
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)


# Entry point for running user bot standalone
if __name__ == "__main__":
    logger.info("="*50)
    logger.info("TELEGRAM FILE DISTRIBUTION SYSTEM - USER BOT")
    logger.info("="*50)
    run_user_bot()