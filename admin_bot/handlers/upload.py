"""
Upload Handler for Admin Bot
Handles ZIP file uploads, metadata collection, and posting to channels.
"""

import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters
)
from telegram.constants import ParseMode
from telegram.error import TelegramError

from database.operations.files import add_file, get_file_by_post_no
from database.operations.settings import get_setting
from admin_bot.middleware.auth import admin_only
from config.settings import PRIVATE_STORAGE_CHANNEL_ID, PUBLIC_GROUP_ID, USER_BOT_USERNAME

# Conversation states
UPLOAD_FILE, POST_NO, CONTEXT, EXTRA_MESSAGE = range(4)


@admin_only
async def upload_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the file upload process."""
    await update.message.reply_text(
        "📤 *Upload New File*\n\n"
        "Step 1/4: Send me the ZIP file you want to upload.\n\n"
        "⚠️ *Requirements:*\n"
        "• File must be in ZIP format\n"
        "• Maximum size: 2GB\n"
        "• File will be stored in private channel\n\n"
        "Send /cancel to cancel.",
        parse_mode=ParseMode.MARKDOWN
    )
    
    return UPLOAD_FILE


async def receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and validate the uploaded file."""
    message = update.message
    
    # Check if document is present
    if not message.document:
        await message.reply_text(
            "❌ Please send a file as a document (not compressed).\n\n"
            "Send /cancel to cancel."
        )
        return UPLOAD_FILE
    
    document = message.document
    
    # Validate file type
    if not document.file_name.lower().endswith('.zip'):
        await message.reply_text(
            "❌ Invalid file format!\n\n"
            "Please send a ZIP file (.zip extension).\n\n"
            "Send /cancel to cancel."
        )
        return UPLOAD_FILE
    
    # Check file size (2GB limit)
    max_size = 2 * 1024 * 1024 * 1024  # 2GB in bytes
    if document.file_size > max_size:
        await message.reply_text(
            f"❌ File too large!\n\n"
            f"Maximum size: 2GB\n"
            f"Your file: {document.file_size / (1024**3):.2f}GB\n\n"
            "Please upload a smaller file or /cancel"
        )
        return UPLOAD_FILE
    
    # Show uploading message
    status_msg = await message.reply_text(
        "⏳ *Uploading file to private storage channel...*\n\n"
        "Please wait, this may take a moment.",
        parse_mode=ParseMode.MARKDOWN
    )
    
    try:
        # Forward/Upload file to private storage channel
        storage_message = await context.bot.send_document(
            chat_id=PRIVATE_STORAGE_CHANNEL_ID,
            document=document.file_id,
            caption=f"📦 Uploaded by Admin\nFile: {document.file_name}\nSize: {document.file_size / (1024**2):.2f} MB\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        # Store file details in context
        context.user_data['file_id'] = document.file_id
        context.user_data['file_name'] = document.file_name
        context.user_data['file_size'] = document.file_size
        context.user_data['storage_message_id'] = storage_message.message_id
        
        await status_msg.edit_text(
            "✅ *File uploaded successfully!*\n\n"
            f"File Name: `{document.file_name}`\n"
            f"File Size: `{document.file_size / (1024**2):.2f} MB`\n\n"
            "Step 2/4: Send me the Post Number.\n\n"
            "Example: `12345`\n\n"
            "Send /cancel to cancel.",
            parse_mode=ParseMode.MARKDOWN
        )
        
        return POST_NO
    
    except TelegramError as e:
        await status_msg.edit_text(
            f"❌ *Upload Failed!*\n\n"
            f"Error: {str(e)}\n\n"
            "Please make sure:\n"
            "• Admin Bot is added to the private channel\n"
            "• Bot has permission to send messages\n"
            "• Channel ID is correct in settings\n\n"
            "Use /upload to try again.",
            parse_mode=ParseMode.MARKDOWN
        )
        return ConversationHandler.END
    
    except Exception as e:
        await status_msg.edit_text(
            f"❌ Unexpected error: {str(e)}\n\n"
            "Use /upload to try again."
        )
        return ConversationHandler.END


async def receive_post_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and validate post number."""
    post_no_text = update.message.text.strip()
    
    # Validate numeric
    if not post_no_text.isdigit():
        await update.message.reply_text(
            "❌ Invalid post number!\n\n"
            "Please send a numeric value (e.g., 12345)\n\n"
            "Send /cancel to cancel."
        )
        return POST_NO
    
    post_no = int(post_no_text)
    
    # Check if post number already exists
    existing_file = await get_file_by_post_no(post_no)
    if existing_file:
        await update.message.reply_text(
            f"⚠️ Post number `{post_no}` already exists!\n\n"
            "Please choose a different number or /cancel",
            parse_mode=ParseMode.MARKDOWN
        )
        return POST_NO
    
    # Store post number
    context.user_data['post_no'] = post_no
    
    await update.message.reply_text(
        f"✅ Post Number: `{post_no}`\n\n"
        "Step 3/4: Send me the Context/Title.\n\n"
        "This will be displayed in the post header.\n\n"
        "Example: `Premium Course - Python Programming`\n\n"
        "Send /cancel to cancel.",
        parse_mode=ParseMode.MARKDOWN
    )
    
    return CONTEXT


async def receive_context(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive post context/title."""
    context_text = update.message.text.strip()
    
    if len(context_text) < 3:
        await update.message.reply_text(
            "❌ Context too short! Minimum 3 characters.\n\n"
            "Send /cancel to cancel."
        )
        return CONTEXT
    
    if len(context_text) > 200:
        await update.message.reply_text(
            "❌ Context too long! Maximum 200 characters.\n\n"
            "Send /cancel to cancel."
        )
        return CONTEXT
    
    # Store context
    context.user_data['context'] = context_text
    
    await update.message.reply_text(
        f"✅ Context saved!\n\n"
        "Step 4/4: Send me the Extra Message.\n\n"
        "This will be shown in a quote block below the context.\n\n"
        "Example: `Complete tutorial with source code`\n\n"
        "Send /cancel to cancel.",
        parse_mode=ParseMode.MARKDOWN
    )
    
    return EXTRA_MESSAGE


async def receive_extra_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive extra message and create the post."""
    extra_message = update.message.text.strip()
    
    if len(extra_message) < 3:
        await update.message.reply_text(
            "❌ Extra message too short! Minimum 3 characters.\n\n"
            "Send /cancel to cancel."
        )
        return EXTRA_MESSAGE
    
    if len(extra_message) > 300:
        await update.message.reply_text(
            "❌ Extra message too long! Maximum 300 characters.\n\n"
            "Send /cancel to cancel."
        )
        return EXTRA_MESSAGE
    
    # Store extra message
    context.user_data['extra_message'] = extra_message
    
    # Show confirmation
    keyboard = [
        [
            InlineKeyboardButton("✅ Confirm & Post", callback_data="upload_confirm"),
            InlineKeyboardButton("❌ Cancel", callback_data="upload_cancel")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    post_no = context.user_data['post_no']
    context_text = context.user_data['context']
    file_name = context.user_data['file_name']
    file_size = context.user_data['file_size']
    
    preview_message = (
        "📋 *Upload Preview*\n\n"
        f"*Post Number:* {post_no}\n"
        f"*Context:* {context_text}\n"
        f"*Extra Message:* {extra_message}\n"
        f"*File:* {file_name}\n"
        f"*Size:* {file_size / (1024**2):.2f} MB\n\n"
        "Confirm to post this to the public group?"
    )
    
    await update.message.reply_text(
        preview_message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return EXTRA_MESSAGE


async def confirm_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm and finalize the upload."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "upload_cancel":
        await query.edit_message_text("❌ Upload cancelled. File remains in storage channel.")
        context.user_data.clear()
        return ConversationHandler.END
    
    # Get stored data
    post_no = context.user_data['post_no']
    context_text = context.user_data['context']
    extra_message = context.user_data['extra_message']
    file_id = context.user_data['file_id']
    file_name = context.user_data['file_name']
    storage_message_id = context.user_data['storage_message_id']
    admin_id = query.from_user.id
    
    # Get password from settings
    password_setting = await get_setting('file_password')
    password = password_setting['setting_value'] if password_setting else 'default123'
    
    try:
        # Create download link
        # Encode post_no in base64 for the deep link
        import base64
        deep_link_data = f"get-{post_no}"
        encoded_data = base64.b64encode(deep_link_data.encode()).decode()
        download_link = f"https://t.me/{USER_BOT_USERNAME}?start={encoded_data}"
        
        # Format the post message
        post_message = (
            f"Post - {{{post_no}}} 💀\n\n"
            f"Context:{{{context_text}}}\n\n"
            f"❝ {extra_message} ❞"
        )
        
        # Create download button
        keyboard = [[InlineKeyboardButton("⬇️ DOWNLOAD ⬇️", url=download_link)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send to public group
        public_message = await context.bot.send_message(
            chat_id=PUBLIC_GROUP_ID,
            text=post_message,
            reply_markup=reply_markup
        )
        
        # Save to database
        await add_file(
            post_no=post_no,
            context=context_text,
            extra_message=extra_message,
            file_id=file_id,
            file_name=file_name,
            storage_message_id=storage_message_id,
            public_message_id=public_message.message_id,
            password=password,
            created_by=admin_id
        )
        
        await query.edit_message_text(
            "✅ *Upload Completed Successfully!*\n\n"
            f"*Post Number:* {post_no}\n"
            f"*Posted to Public Group*\n"
            f"*Stored in Private Channel*\n"
            f"*Password:* `{password}`\n\n"
            "Users can now download this file!",
            parse_mode=ParseMode.MARKDOWN
        )
    
    except Exception as e:
        await query.edit_message_text(
            f"❌ *Error posting to public group:*\n\n"
            f"{str(e)}\n\n"
            "File is saved in storage channel but post failed.\n"
            "Please check bot permissions in public group.",
            parse_mode=ParseMode.MARKDOWN
        )
    
    # Clear user data
    context.user_data.clear()
    
    return ConversationHandler.END


async def cancel_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel upload process."""
    context.user_data.clear()
    await update.message.reply_text(
        "❌ Upload cancelled.\n\n"
        "Use /upload to start again."
    )
    return ConversationHandler.END


# Create upload conversation handler
upload_handler = ConversationHandler(
    entry_points=[CommandHandler('upload', upload_command)],
    states={
        UPLOAD_FILE: [
            MessageHandler(filters.Document.ALL, receive_file)
        ],
        POST_NO: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_post_no)
        ],
        CONTEXT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_context)
        ],
        EXTRA_MESSAGE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_extra_message),
            CallbackQueryHandler(confirm_upload, pattern='^upload_')
        ]
    },
    fallbacks=[CommandHandler('cancel', cancel_upload)],
    name="upload_conversation",
    persistent=False
)