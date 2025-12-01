"""
Verification Handler for Admin Bot
Handles manual user verification, unverification, and limit resets.
"""

from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler
from telegram.constants import ParseMode

from database.operations.users import (
    get_user_by_id,
    verify_user_manually,
    unverify_user,
    reset_user_file_limit,
    update_user_verification
)
from database.operations.logs import log_admin_action
from admin_bot.middleware.auth import admin_only


@admin_only
async def verify_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manually verify a user for specified hours."""
    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ *Invalid Usage*\n\n"
            "Usage: `/verifyuser <user_id> <hours>`\n\n"
            "Examples:\n"
            "• `/verifyuser 123456789 24` - Verify for 24 hours\n"
            "• `/verifyuser 987654321 48` - Verify for 48 hours\n"
            "• `/verifyuser 555555555 168` - Verify for 1 week (168h)\n\n"
            "💡 Standard verification period is 24 hours.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    try:
        user_id = int(context.args[0])
        hours = int(context.args[1])
        
        # Validate hours
        if hours < 1:
            await update.message.reply_text(
                "❌ Hours must be at least 1.\n\n"
                "Use a positive number for hours."
            )
            return
        
        if hours > 8760:  # 365 days
            await update.message.reply_text(
                "❌ Maximum verification period is 8760 hours (365 days).\n\n"
                "Please use a shorter duration."
            )
            return
        
        # Check if user exists
        user = await get_user_by_id(user_id)
        
        if not user:
            # Ask to create user
            keyboard = [
                [
                    InlineKeyboardButton("✅ Yes, Create & Verify", callback_data=f"verify_create_{user_id}_{hours}"),
                    InlineKeyboardButton("❌ Cancel", callback_data="verify_cancel")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"⚠️ *User Not Found*\n\n"
                f"User ID `{user_id}` is not in the database yet.\n\n"
                "This might be because:\n"
                "• User hasn't started the User Bot yet\n"
                "• User ID is incorrect\n\n"
                "Do you want to create this user and verify them?",
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Calculate expiry
        verified_at = datetime.now()
        expires_at = verified_at + timedelta(hours=hours)
        
        # Verify user
        result = await verify_user_manually(
            user_id=user_id,
            hours=hours,
            verified_by=update.effective_user.id
        )
        
        if result:
            username = user.get('username', 'N/A')
            
            # Log action
            await log_admin_action(
                admin_id=update.effective_user.id,
                action='verify_user',
                details={
                    'user_id': user_id,
                    'username': username,
                    'hours': hours
                }
            )
            
            await update.message.reply_text(
                "✅ *User Verified Successfully!*\n\n"
                f"*User ID:* `{user_id}`\n"
                f"*Username:* @{username}\n"
                f"*Duration:* {hours} hours\n"
                f"*Verified At:* {verified_at.strftime('%Y-%m-%d %H:%M')}\n"
                f"*Expires At:* {expires_at.strftime('%Y-%m-%d %H:%M')}\n\n"
                "User can now access up to 3 files during this period.",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.message.reply_text(
                "❌ Failed to verify user. Please try again or check logs."
            )
    
    except ValueError:
        await update.message.reply_text(
            "❌ *Invalid Input*\n\n"
            "Both user_id and hours must be numbers.\n\n"
            "Example: `/verifyuser 123456789 24`",
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Error: {str(e)}"
        )


@admin_only
async def unverify_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove verification from a user."""
    if not context.args:
        await update.message.reply_text(
            "❌ *Invalid Usage*\n\n"
            "Usage: `/unverifyuser <user_id>`\n\n"
            "Example:\n"
            "• `/unverifyuser 123456789`\n\n"
            "This will remove the user's verification status.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    try:
        user_id = int(context.args[0])
        
        # Check if user exists
        user = await get_user_by_id(user_id)
        
        if not user:
            await update.message.reply_text(
                f"❌ User with ID `{user_id}` not found in database.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        if not user.get('is_verified', False):
            await update.message.reply_text(
                f"⚠️ User `{user_id}` is not currently verified.\n\n"
                "No action needed.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Unverify user
        result = await unverify_user(user_id)
        
        if result:
            username = user.get('username', 'N/A')
            
            # Log action
            await log_admin_action(
                admin_id=update.effective_user.id,
                action='unverify_user',
                details={
                    'user_id': user_id,
                    'username': username
                }
            )
            
            await update.message.reply_text(
                "✅ *User Unverified Successfully!*\n\n"
                f"*User ID:* `{user_id}`\n"
                f"*Username:* @{username}\n\n"
                "User will need to verify again to access files.",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.message.reply_text(
                "❌ Failed to unverify user. Please try again."
            )
    
    except ValueError:
        await update.message.reply_text(
            "❌ User ID must be a number.\n\n"
            "Example: `/unverifyuser 123456789`",
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Error: {str(e)}"
        )


@admin_only
async def reset_user_limit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset a user's file access limit."""
    if not context.args:
        await update.message.reply_text(
            "❌ *Invalid Usage*\n\n"
            "Usage: `/resetuserlimit <user_id>`\n\n"
            "Example:\n"
            "• `/resetuserlimit 123456789`\n\n"
            "This will reset the user's file access count to 0/3.\n"
            "User must still be verified to access files.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    try:
        user_id = int(context.args[0])
        
        # Check if user exists
        user = await get_user_by_id(user_id)
        
        if not user:
            await update.message.reply_text(
                f"❌ User with ID `{user_id}` not found in database.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        current_count = user.get('files_accessed_count', 0)
        
        if current_count == 0:
            await update.message.reply_text(
                f"⚠️ User `{user_id}` already has 0 files accessed.\n\n"
                "No reset needed.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Reset limit
        result = await reset_user_file_limit(user_id)
        
        if result:
            username = user.get('username', 'N/A')
            
            # Log action
            await log_admin_action(
                admin_id=update.effective_user.id,
                action='reset_user_limit',
                details={
                    'user_id': user_id,
                    'username': username,
                    'previous_count': current_count
                }
            )
            
            await update.message.reply_text(
                "✅ *File Access Limit Reset!*\n\n"
                f"*User ID:* `{user_id}`\n"
                f"*Username:* @{username}\n"
                f"*Previous Count:* {current_count}/3\n"
                f"*New Count:* 0/3\n\n"
                "User can now access 3 more files (if verified).",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.message.reply_text(
                "❌ Failed to reset user limit. Please try again."
            )
    
    except ValueError:
        await update.message.reply_text(
            "❌ User ID must be a number.\n\n"
            "Example: `/resetuserlimit 123456789`",
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Error: {str(e)}"
        )


@admin_only
async def extend_verification_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Extend a user's verification period."""
    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ *Invalid Usage*\n\n"
            "Usage: `/extendverification <user_id> <additional_hours>`\n\n"
            "Examples:\n"
            "• `/extendverification 123456789 24` - Add 24 hours\n"
            "• `/extendverification 987654321 12` - Add 12 hours\n\n"
            "This extends the existing verification period.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    try:
        user_id = int(context.args[0])
        additional_hours = int(context.args[1])
        
        # Validate hours
        if additional_hours < 1:
            await update.message.reply_text(
                "❌ Additional hours must be at least 1."
            )
            return
        
        # Check if user exists and is verified
        user = await get_user_by_id(user_id)
        
        if not user:
            await update.message.reply_text(
                f"❌ User with ID `{user_id}` not found in database.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        if not user.get('is_verified', False):
            await update.message.reply_text(
                f"⚠️ User `{user_id}` is not currently verified.\n\n"
                "Use `/verifyuser` to verify them first.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Get current expiry
        current_expires_at = user.get('expires_at')
        
        if not current_expires_at:
            await update.message.reply_text(
                "❌ User verification data is incomplete.\n\n"
                "Please use `/verifyuser` to re-verify.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Calculate new expiry
        new_expires_at = current_expires_at + timedelta(hours=additional_hours)
        
        # Update user
        result = await update_user_verification(
            user_id=user_id,
            expires_at=new_expires_at
        )
        
        if result:
            username = user.get('username', 'N/A')
            
            # Log action
            await log_admin_action(
                admin_id=update.effective_user.id,
                action='extend_verification',
                details={
                    'user_id': user_id,
                    'username': username,
                    'additional_hours': additional_hours
                }
            )
            
            await update.message.reply_text(
                "✅ *Verification Extended!*\n\n"
                f"*User ID:* `{user_id}`\n"
                f"*Username:* @{username}\n"
                f"*Additional Time:* +{additional_hours} hours\n"
                f"*Previous Expiry:* {current_expires_at.strftime('%Y-%m-%d %H:%M')}\n"
                f"*New Expiry:* {new_expires_at.strftime('%Y-%m-%d %H:%M')}\n\n"
                "User's verification period has been extended.",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.message.reply_text(
                "❌ Failed to extend verification. Please try again."
            )
    
    except ValueError:
        await update.message.reply_text(
            "❌ *Invalid Input*\n\n"
            "Both user_id and hours must be numbers.\n\n"
            "Example: `/extendverification 123456789 24`",
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Error: {str(e)}"
        )


@admin_only
async def bulk_verify_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verify multiple users at once."""
    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ *Invalid Usage*\n\n"
            "Usage: `/bulkverify <hours> <user_id1> <user_id2> ...`\n\n"
            "Example:\n"
            "• `/bulkverify 24 123456789 987654321 555555555`\n\n"
            "This verifies all listed users for the specified hours.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    try:
        hours = int(context.args[0])
        user_ids = [int(uid) for uid in context.args[1:]]
        
        if not user_ids:
            await update.message.reply_text(
                "❌ Please provide at least one user ID."
            )
            return
        
        if len(user_ids) > 50:
            await update.message.reply_text(
                "❌ Maximum 50 users per bulk operation."
            )
            return
        
        status_msg = await update.message.reply_text(
            f"⏳ Verifying {len(user_ids)} users for {hours} hours...\n\n"
            "Please wait..."
        )
        
        success_count = 0
        failed_count = 0
        failed_users = []
        
        for user_id in user_ids:
            try:
                result = await verify_user_manually(
                    user_id=user_id,
                    hours=hours,
                    verified_by=update.effective_user.id
                )
                
                if result:
                    success_count += 1
                else:
                    failed_count += 1
                    failed_users.append(user_id)
            except:
                failed_count += 1
                failed_users.append(user_id)
        
        # Log bulk action
        await log_admin_action(
            admin_id=update.effective_user.id,
            action='bulk_verify',
            details={
                'hours': hours,
                'total_users': len(user_ids),
                'success': success_count,
                'failed': failed_count
            }
        )
        
        result_message = (
            "✅ *Bulk Verification Complete!*\n\n"
            f"*Duration:* {hours} hours\n"
            f"*Total Users:* {len(user_ids)}\n"
            f"*Successful:* {success_count}\n"
            f"*Failed:* {failed_count}\n"
        )
        
        if failed_users:
            result_message += f"\n*Failed User IDs:*\n"
            for uid in failed_users[:10]:  # Show first 10
                result_message += f"`{uid}` "
            if len(failed_users) > 10:
                result_message += f"\n... and {len(failed_users) - 10} more"
        
        await status_msg.edit_text(
            result_message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    except ValueError:
        await update.message.reply_text(
            "❌ All arguments must be numbers.\n\n"
            "Example: `/bulkverify 24 123456789 987654321`",
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Error: {str(e)}"
        )


# Create verification handler
verification_handler = [
    CommandHandler('verifyuser', verify_user_command),
    CommandHandler('unverifyuser', unverify_user_command),
    CommandHandler('resetuserlimit', reset_user_limit_command),
    CommandHandler('extendverification', extend_verification_command),
    CommandHandler('bulkverify', bulk_verify_command),
]