"""
Statistics Handler for Admin Bot
Handles user statistics, analytics, and reporting.
"""

from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler
from telegram.constants import ParseMode

from database.operations.users import (
    get_all_users_count,
    get_verified_users_count,
    get_verified_users,
    get_active_users,
    get_user_by_id,
    get_users_joined_today,
    get_users_joined_this_week,
    get_users_joined_this_month
)
from database.operations.files import (
    get_total_files_count,
    get_total_downloads_count,
    get_most_downloaded_files
)
from admin_bot.middleware.auth import admin_only


@admin_only
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show overall system statistics."""
    try:
        # Fetch statistics
        total_users = await get_all_users_count()
        verified_users = await get_verified_users_count()
        total_files = await get_total_files_count()
        total_downloads = await get_total_downloads_count()
        
        # Get user growth stats
        users_today = await get_users_joined_today()
        users_week = await get_users_joined_this_week()
        users_month = await get_users_joined_this_month()
        
        # Calculate percentages
        verified_percentage = (verified_users / total_users * 100) if total_users > 0 else 0
        avg_downloads_per_file = (total_downloads / total_files) if total_files > 0 else 0
        
        stats_message = (
            "📊 *System Statistics*\n\n"
            
            "*👥 User Statistics:*\n"
            f"Total Users: `{total_users:,}`\n"
            f"✅ Verified Users: `{verified_users:,}` ({verified_percentage:.1f}%)\n"
            f"❌ Unverified: `{total_users - verified_users:,}`\n\n"
            
            "*📈 User Growth:*\n"
            f"Today: `+{users_today:,}`\n"
            f"This Week: `+{users_week:,}`\n"
            f"This Month: `+{users_month:,}`\n\n"
            
            "*📁 File Statistics:*\n"
            f"Total Files: `{total_files:,}`\n"
            f"Total Downloads: `{total_downloads:,}`\n"
            f"Avg Downloads/File: `{avg_downloads_per_file:.1f}`\n\n"
            
            f"*📅 Report Generated:*\n"
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("📅 Daily Stats", callback_data="stats_daily"),
                InlineKeyboardButton("🏆 Top Files", callback_data="stats_top_files")
            ],
            [
                InlineKeyboardButton("👤 Active Users", callback_data="stats_active"),
                InlineKeyboardButton("✅ Verified List", callback_data="stats_verified")
            ],
            [InlineKeyboardButton("🔄 Refresh", callback_data="stats_refresh")],
            [InlineKeyboardButton("❌ Close", callback_data="stats_close")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            stats_message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    except Exception as e:
        await update.message.reply_text(
            f"❌ Error fetching statistics: {str(e)}"
        )


@admin_only
async def verified_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all verified users with details."""
    try:
        verified_users = await get_verified_users()
        
        if not verified_users:
            await update.message.reply_text(
                "✅ *Verified Users*\n\n"
                "No verified users at the moment.\n\n"
                "Users become verified after completing the verification process.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Sort by verification expiry (soonest first)
        verified_users.sort(key=lambda x: x.get('expires_at', datetime.max))
        
        message = f"✅ *Verified Users* ({len(verified_users)} total)\n\n"
        
        current_time = datetime.now()
        
        for idx, user in enumerate(verified_users[:50], 1):  # Limit to 50 to avoid message too long
            user_id = user['user_id']
            username = user.get('username', 'N/A')
            expires_at = user.get('expires_at')
            files_accessed = user.get('files_accessed_count', 0)
            
            # Calculate time remaining
            if expires_at:
                time_left = expires_at - current_time
                hours_left = int(time_left.total_seconds() / 3600)
                
                if hours_left < 0:
                    status = "⏰ Expired"
                elif hours_left < 1:
                    mins_left = int(time_left.total_seconds() / 60)
                    status = f"⚠️ {mins_left}m left"
                else:
                    status = f"✅ {hours_left}h left"
            else:
                status = "❓ Unknown"
            
            message += (
                f"{idx}. {status}\n"
                f"   ID: `{user_id}` | @{username}\n"
                f"   Files: {files_accessed}/3\n\n"
            )
        
        if len(verified_users) > 50:
            message += f"\n... and {len(verified_users) - 50} more users"
        
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh", callback_data="verified_refresh")],
            [InlineKeyboardButton("📊 Back to Stats", callback_data="stats_refresh")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    except Exception as e:
        await update.message.reply_text(
            f"❌ Error fetching verified users: {str(e)}"
        )


@admin_only
async def active_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show active users from today."""
    try:
        since_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        active_users = await get_active_users(since_date)
        
        if not active_users:
            await update.message.reply_text(
                "👤 *Active Users Today*\n\n"
                "No active users today yet.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        message = f"👤 *Active Users Today* ({len(active_users)} users)\n\n"
        
        for idx, user in enumerate(active_users[:30], 1):  # Limit to 30
            user_id = user['user_id']
            username = user.get('username', 'N/A')
            last_access = user.get('last_access', 'N/A')
            is_verified = user.get('is_verified', False)
            
            status = "✅" if is_verified else "❌"
            
            if isinstance(last_access, datetime):
                last_access_str = last_access.strftime('%H:%M')
            else:
                last_access_str = 'N/A'
            
            message += (
                f"{idx}. {status} `{user_id}` | @{username}\n"
                f"   Last seen: {last_access_str}\n\n"
            )
        
        if len(active_users) > 30:
            message += f"\n... and {len(active_users) - 30} more users"
        
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    except Exception as e:
        await update.message.reply_text(
            f"❌ Error fetching active users: {str(e)}"
        )


@admin_only
async def daily_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show daily statistics report."""
    try:
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Get today's data
        new_users_today = await get_users_joined_today()
        active_today = await get_active_users(today)
        
        # Get yesterday's data for comparison
        yesterday = today - timedelta(days=1)
        new_users_yesterday = len(await get_active_users(yesterday))
        
        # Calculate growth
        growth = new_users_today - new_users_yesterday
        growth_percent = (growth / new_users_yesterday * 100) if new_users_yesterday > 0 else 0
        growth_indicator = "📈" if growth >= 0 else "📉"
        
        message = (
            f"📅 *Daily Statistics Report*\n"
            f"{datetime.now().strftime('%Y-%m-%d')}\n\n"
            
            f"*Today's Activity:*\n"
            f"👥 New Users: `{new_users_today:,}`\n"
            f"🔥 Active Users: `{len(active_today):,}`\n\n"
            
            f"*Growth vs Yesterday:*\n"
            f"{growth_indicator} {growth:+,} users ({growth_percent:+.1f}%)\n\n"
            
            f"*Quick Stats:*\n"
            f"Total Users: `{await get_all_users_count():,}`\n"
            f"Verified: `{await get_verified_users_count():,}`\n"
            f"Total Files: `{await get_total_files_count():,}`\n\n"
            
            f"Report generated at {datetime.now().strftime('%H:%M:%S')}"
        )
        
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh", callback_data="daily_refresh")],
            [InlineKeyboardButton("📊 Full Stats", callback_data="stats_refresh")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    except Exception as e:
        await update.message.reply_text(
            f"❌ Error generating daily report: {str(e)}"
        )


@admin_only
async def top_files_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show most downloaded files."""
    try:
        top_files = await get_most_downloaded_files(limit=10)
        
        if not top_files:
            await update.message.reply_text(
                "🏆 *Top Downloaded Files*\n\n"
                "No file downloads yet.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        message = "🏆 *Top 10 Downloaded Files*\n\n"
        
        medals = ["🥇", "🥈", "🥉"]
        
        for idx, file in enumerate(top_files, 1):
            medal = medals[idx - 1] if idx <= 3 else f"{idx}."
            post_no = file.get('post_no', 'N/A')
            context_text = file.get('context', 'No title')
            downloads = file.get('download_count', 0)
            
            # Truncate context if too long
            if len(context_text) > 40:
                context_text = context_text[:37] + "..."
            
            message += (
                f"{medal} *Post #{post_no}*\n"
                f"   {context_text}\n"
                f"   📥 {downloads:,} downloads\n\n"
            )
        
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh", callback_data="top_files_refresh")],
            [InlineKeyboardButton("📊 Back to Stats", callback_data="stats_refresh")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            message,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    except Exception as e:
        await update.message.reply_text(
            f"❌ Error fetching top files: {str(e)}"
        )


@admin_only
async def user_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get detailed information about a specific user."""
    if not context.args:
        await update.message.reply_text(
            "❌ Usage: `/userinfo <user_id>`\n\n"
            "Example: `/userinfo 123456789`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    try:
        user_id = int(context.args[0])
        user = await get_user_by_id(user_id)
        
        if not user:
            await update.message.reply_text(
                f"❌ User with ID `{user_id}` not found in database.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        username = user.get('username', 'N/A')
        is_verified = user.get('is_verified', False)
        verified_at = user.get('verified_at')
        expires_at = user.get('expires_at')
        files_accessed = user.get('files_accessed_count', 0)
        last_access = user.get('last_access')
        
        # Format dates
        verified_at_str = verified_at.strftime('%Y-%m-%d %H:%M') if verified_at else 'Never'
        last_access_str = last_access.strftime('%Y-%m-%d %H:%M') if last_access else 'Never'
        
        # Calculate time remaining
        if is_verified and expires_at:
            time_left = expires_at - datetime.now()
            hours_left = int(time_left.total_seconds() / 3600)
            
            if hours_left < 0:
                verification_status = "⏰ Expired"
            else:
                verification_status = f"✅ Active ({hours_left}h remaining)"
        else:
            verification_status = "❌ Not Verified"
        
        message = (
            f"👤 *User Information*\n\n"
            f"*User ID:* `{user_id}`\n"
            f"*Username:* @{username}\n\n"
            
            f"*Verification Status:*\n"
            f"{verification_status}\n"
            f"Verified On: {verified_at_str}\n\n"
            
            f"*Activity:*\n"
            f"Files Accessed: {files_accessed}/3\n"
            f"Last Active: {last_access_str}\n\n"
            
            f"*Actions:*\n"
            f"• /verifyuser {user_id} 24 - Verify for 24h\n"
            f"• /unverifyuser {user_id} - Remove verification\n"
            f"• /resetuserlimit {user_id} - Reset file count"
        )
        
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid user ID. Please provide a numeric user ID."
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Error fetching user info: {str(e)}"
        )


async def stats_close_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Close statistics message."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("✅ Statistics closed.")


# Create stats handler
stats_handler = [
    CommandHandler('stats', stats_command),
    CommandHandler('verifiedusers', verified_users_command),
    CommandHandler('activeusers', active_users_command),
    CommandHandler('dailystats', daily_stats_command),
    CommandHandler('topfiles', top_files_command),
    CommandHandler('userinfo', user_info_command),
]