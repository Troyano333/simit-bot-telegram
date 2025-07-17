# bot.py (VERSIÓN CORREGIDA PARA ASYNCIO)

import logging
import asyncio # <--- IMPORTANTE: Añadimos la librería asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Importamos tu scraper, que no necesita cambios
from simit_scraper import consultar_simit

# Por favor, considera regenerar este token después de que funcione, ya que es público.
BOT_TOKEN = "7611758198:AAHQY6qVhK1Fsf4vMPXHHDdEHI039ZydyN8"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 ¡Hola! Envíame tu cédula y te diré si tienes comparendos en el SIMIT.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cedula = update.message.text.strip()
    if not cedula.isdigit():
        await update.message.reply_text("❌ Por favor, envíame solo tu número de cédula (solo números).")
        return

    await update.message.reply_text("🔎 Consultando en el SIMIT... (Esto puede tardar un momento)")

    try:
        # --- ¡AQUÍ ESTÁ LA CORRECCIÓN CLAVE! ---
        # Le decimos a asyncio que ejecute la función síncrona "consultar_simit"
        # en un hilo separado para no bloquear el bot.
        resultado = await asyncio.to_thread(consultar_simit, cedula)
        
        await update.message.reply_text(resultado)
        
    except Exception as e:
        logging.error(f"Error al consultar el SIMIT: {e}")
        await update.message.reply_text("⚠️ No se pudo obtener información del SIMIT. Revisa si el sitio web está funcionando.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Bot iniciado. Esperando mensajes...")
    app.run_polling()

if __name__ == '__main__':
    main()