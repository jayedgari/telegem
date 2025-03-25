import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import pandas as pd
import google.generativeai as genai

# Replace with your keys
TELEGRAM_TOKEN = "7940858927:AAF34FoEVD4ag_DZfWKUkVar_h93WWXZAtk"
GEMINI_API_KEY = "AIzaSyAitopt7J6IkXFl2hgsUQjOgOEzMMgrEZ0"

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

async def start(update: Update, context):
    await update.message.reply_text('Hello! Send me an Excel file, and I’ll analyze it! 📊')

async def analyze_excel(update: Update, context):
    file = await update.message.document.get_file()
    await file.download_to_drive("user_file.xlsx")
    
    # Read Excel
    df = pd.read_excel("user_file.xlsx")
    sample_data = df.head(5).to_string()  # Show first 5 rows
    
    # Ask Gemini to analyze
    prompt = f"Analyze this Excel data and summarize key insights:\n{sample_data}"
    response = model.generate_content(prompt)
    
    await update.message.reply_text(f"🔍 Analysis Results:\n{response.text}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.FileExtension("xlsx"), analyze_excel))
    app.run_polling()

if __name__ == "__main__":
    main()