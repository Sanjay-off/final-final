"""
Admin Bot Main Module
Main entry point for the admin bot application.
Initializes and runs the Telegram admin bot.
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
from config.settings import ADMIN_BOT_TOKEN

# Import handlers
from admin_bot.handlers import (
    start_handler,
    upload_handler,
    broadcast_handler,
    channels_handler,
    settings_handler,
    stats_handler,
    verification_handler,
    menu_handler
)

# Import middleware
from admin_bot.middleware import admin_only

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# Global application instance
admin_application = None


def setup_handlers(application: Application) -> None:
    """
    Setup all handlers for the admin bot.
    
    Args:
        application: Telegram application instance
    """
    logger.info("Setting up admin bot handlers...")
    
    # Start and help handlers (from start_handler list)
    for handler in start_handler:
        application.add_handler(handler)
    
    # Upload handler (ConversationHandler)
    application.add_handler(upload_handler)
    
    # Broadcast handler (ConversationHandler)
    application.add_handler(broadcast_handler)
    
    # Channels handlers (includes ConversationHandler and CallbackQueryHandlers)
    if isinstance(channels_handler, list):
        for handler in channels_handler:
            application.add_handler(handler)
    else:
        application.add_handler(channels_handler)
    
    # Settings handlers (includes ConversationHandlers)
    if isinstance(settings_handler, list):
        for handler in settings_handler:
            application.add_handler(handler)
    else:
        application.add_handler(settings_handler)
    
    # Stats handlers
    if isinstance(stats_handler, list):
        for handler in stats_handler:
            application.add_handler(handler)
    else:
        application.add_handler(stats_handler)
    
    # Verification handlers
    if isinstance(verification_handler, list):
        for handler in verification_handler:
            application.add_handler(handler)
    else:
        application.add_handler(verification_handler)
    
    # Menu handlers (CallbackQueryHandlers)
    if isinstance(menu_handler, list):
        for handler in menu_handler:
            application.add_handler(handler)
    else:
        application.add_handler(menu_handler)
    
    logger.info("Admin bot handlers setup complete")


async def post_init(application: Application) -> None:
    """
    Post initialization tasks.
    
    Args:
        application: Telegram application instance
    """
    logger.info("Running post-initialization tasks...")
    
    # Set bot commands
    from admin_bot.keyboards.menu import get_admin_commands
    
    try:
        commands = get_admin_commands()
        await application.bot.set_my_commands(commands)
        logger.info(f"Set {len(commands)} bot commands")
    except Exception as e:
        logger.error(f"Failed to set bot commands: {e}")
    
    # Log bot info
    bot_info = await application.bot.get_me()
    logger.info(f"Admin Bot started: @{bot_info.username} (ID: {bot_info.id})")


async def post_shutdown(application: Application) -> None:
    """
    Post shutdown cleanup tasks.
    
    Args:
        application: Telegram application instance
    """
    logger.info("Running post-shutdown cleanup...")
    logger.info("Admin bot stopped")


def create_admin_application() -> Application:
    """
    Create and configure the admin bot application.
    
    Returns:
        Configured Application instance
    """
    logger.info("Creating admin bot application...")
    
    # Create application
    application = (
        Application.builder()
        .token(ADMIN_BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )
    
    # Setup handlers
    setup_handlers(application)
    
    return application


def get_admin_application() -> Application:
    """
    Get the admin bot application instance.
    Creates it if it doesn't exist.
    
    Returns:
        Application instance
    """
    global admin_application
    
    if admin_application is None:
        admin_application = create_admin_application()
    
    return admin_application


async def start_admin_bot() -> None:
    """
    Start the admin bot.
    This function initializes and runs the bot.
    """
    global admin_application
    
    try:
        logger.info("Starting Admin Bot...")
        
        # Create application
        admin_application = create_admin_application()
        
        # Start polling
        logger.info("Admin bot polling started")
        await admin_application.run_polling(
            allowed_updates=[
                "message",
                "callback_query",
                "edited_message"
            ],
            drop_pending_updates=True
        )
        
    except Exception as e:
        logger.error(f"Error starting admin bot: {e}", exc_info=True)
        raise


async def stop_admin_bot() -> None:
    """
    Stop the admin bot gracefully.
    """
    global admin_application
    
    try:
        if admin_application:
            logger.info("Stopping Admin Bot...")
            await admin_application.stop()
            await admin_application.shutdown()
            admin_application = None
            logger.info("Admin Bot stopped successfully")
    
    except Exception as e:
        logger.error(f"Error stopping admin bot: {e}", exc_info=True)


def run_admin_bot() -> None:
    """
    Run the admin bot (blocking).
    This is a convenience function for running the bot standalone.
    """
    import asyncio
    
    try:
        asyncio.run(start_admin_bot())
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
        asyncio.run(stop_admin_bot())
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)


# Entry point for running admin bot standalone
if __name__ == "__main__":
    logger.info("="*50)
    logger.info("TELEGRAM FILE DISTRIBUTION SYSTEM - ADMIN BOT")
    logger.info("="*50)
    run_admin_bot()