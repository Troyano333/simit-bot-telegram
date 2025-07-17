    # bot.py (VERSIÓN LISTA PARA RAILWAY)

    import logging
    import asyncio
    import os # <--- IMPORTANTE: Añadimos la librería os para variables de entorno
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

    # Importamos tu scraper
    from simit_scraper import consultar_simit

    # --- ¡CORRECCIÓN CLAVE! ---
    # Obtenemos el token del bot de una variable de entorno.
    # DEBES configurar BOT_TOKEN en Railway.
    BOT_TOKEN = os.environ.get("BOT_TOKEN")

    # Asegúrate de que el token esté presente
    if not BOT_TOKEN:
        logging.error("❌ Error: La variable de entorno BOT_TOKEN no está configurada.")
        exit(1) # Salir si el token no está configurado

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
            # Ejecutamos la función síncrona "consultar_simit" en un hilo separado
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
    
