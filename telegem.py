import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import pandas as pd
import google.generativeai as genai

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure API keys from Railway environment variables
TELEGRAM_TOKEN = "7940858927:AAF34FoEVD4ag_DZfWKUkVar_h93WWXZAtk"
GEMINI_API_KEY = "AIzaSyAitopt7J6IkXFl2hgsUQjOgOEzMMgrEZ0"
# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('📊 Hello! Send me an Excel file (.xlsx) to analyze!')

async def analyze_excel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Download the file
        file = await update.message.document.get_file()
        await file.download_to_drive("user_file.xlsx")
        
        # Read Excel with error handling
        try:
            df = pd.read_excel("user_file.xlsx", nrows=100)  # Limit to 100 rows for safety
            sample_data = df.head(5).to_string()
        except Exception as e:
            await update.message.reply_text(f"❌ Error reading Excel file: {str(e)}")
            return

        # Query Gemini
        prompt = f"Analyze this Excel data and summarize key insights in bullet points:\n{sample_data}"
        response = model.generate_content(prompt)
        
        await update.message.reply_text(f"🔍 Analysis Results:\n{response.text}")

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        await update.message.reply_text("⚠️ Something went wrong. Please try again!")

def main():
    # Get port from Railway or default to 8080
    PORT = int(os.environ.get("PORT", 8080))
    
    # Create Telegram application
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.FileExtension("xlsx"), analyze_excel))
    
    # Start webhook for Railway
    railway_url = os.environ.get('RAILWAY_STATIC_URL', 'your-project-name.up.railway.app')
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=f"https://{railway_url}/{TELEGRAM_TOKEN}"
    )

if __name__ == "__main__":
    main()
