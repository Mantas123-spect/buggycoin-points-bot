import logging
import os
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from google.oauth2 import service_account
import gspread
from dotenv import load_dotenv

# --- Load .env ---
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# --- Google Sheets setup ---
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# Naujas būdas: paimame JSON tekstą iš env kintamojo
json_data = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
info = json.loads(json_data)
creds = service_account.Credentials.from_service_account_info(info, scopes=scope)
client = gspread.authorize(creds)
sheet = client.open("BuggyCoin Points").sheet1

# --- Points logic ---
TASK_POINTS = {
    "meme": 200,
    "invite": 300,
    "share": 500
}

# --- Start command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🐞 Welcome to BuggyCoin Points Bot!\n\n"
        "Earn points (BUG) by completing tasks:\n"
        "🖼 Post a meme → +200 BUG\n"
        "👥 Invite a friend → +300 BUG\n"
        "🔗 Share on social media → +500 BUG\n\n"
        "Commands:\n"
        "/submit - Submit your proof (screenshot or link)\n"
        "/mypoints - Check your points\n\n"
        "Let's build the Buggy Army! 🚀"
    )
    await update.effective_chat.send_message(msg)

# --- Submit command ---
async def submit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username or update.effective_user.first_name

    if not context.args:
        await update.message.reply_text("⚠️ Please specify the task type (meme/invite/share). Example: /submit meme")
        return

    task_type = context.args[0].lower()

    if task_type not in TASK_POINTS:
        await update.effective_chat.send_message("❌ Invalid task type. Use: meme, invite, or share.")
        return

    points = TASK_POINTS[task_type]

    try:
        user_cells = sheet.findall(username)
        if user_cells:
            row = user_cells[0].row
            current_points = int(sheet.cell(row, 4).value or 0)
            sheet.update_cell(row, 4, current_points + points)
            tasks_done = int(sheet.cell(row, 3).value or 0)
            sheet.update_cell(row, 3, tasks_done + 1)
        else:
            sheet.append_row([username, "", 1, points, ""])
    except Exception as e:
        await update.message.reply_text(f"❌ Error updating sheet: {e}")
        return

    await update.message.reply_text(f"✅ Task '{task_type}' submitted successfully! You earned {points} BUG Points.")

# --- MyPoints command ---
async def mypoints(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username or update.effective_user.first_name

    try:
        user_cells = sheet.findall(username)
        if user_cells:
            row = user_cells[0].row
            points = sheet.cell(row, 4).value
            await update.message.reply_text(f"🎯 You have a total of {points} BUG Points.")
        else:
            await update.message.reply_text("🤔 You don't have any points yet. Start submitting tasks!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error reading sheet: {e}")

# --- Main ---
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("submit", submit))
    app.add_handler(CommandHandler("mypoints", mypoints))

    print("🤖 Bot is running... Press Ctrl+C to stop.")
    app.run_polling()
