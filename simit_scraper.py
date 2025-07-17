# simit_scraper.py (VERSIÓN FINAL CON ESTRATEGIA DE CARGA OPTIMIZADA)

from playwright.sync_api import sync_playwright, expect, TimeoutError
import re

def formatear_resultados(cedula: str, filas_tabla: list) -> str:
    """Toma los datos de la tabla y los convierte en un mensaje de texto formateado."""
    
    if not filas_tabla:
        return f"🚨 La cédula {cedula} tiene comparendos, pero no se pudo leer el detalle de la tabla. Verifica en: https://www.fcm.org.co/simit"

    mensaje_final = f"🚨 ¡Atención! La cédula *{cedula}* tiene los siguientes acuerdos de pago registrados:\n"
    encabezados = ["Número acuerdo", "Secretaria", "Valor acuerdo", "Pendiente", "Cuota", "Valor a pagar"]
    
    for i, fila in enumerate(filas_tabla):
        mensaje_final += f"\n--- *Acuerdo #{i+1}* ---\n"
        celdas = fila.locator("td").all()
        
        if len(celdas) >= len(encabezados):
            for j, encabezado in enumerate(encabezados):
                texto_celda = celdas[j].inner_text().strip()
                mensaje_final += f"*{encabezado}:* {texto_celda}\n"
        else:
            mensaje_final += "_(No se pudo leer el detalle de esta fila)_\n"
            
    mensaje_final += "\n\nConsulta más detalles o realiza pagos en el sitio oficial."
    return mensaje_final

def consultar_simit(cedula: str) -> str:
    """Consulta el SIMIT y extrae los detalles de la tabla de comparendos si existe."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
            page = context.new_page()

            page.set_default_timeout(90000)

            # Cambiamos 'networkidle' por 'domcontentloaded' para una carga más rápida y fiable.
            page.goto("https://www.fcm.org.co/simit/#/home-public", wait_until="domcontentloaded", timeout=180000)

            # Esperar a que la página sea funcional.
            spinner_locator = page.locator(".spinner")
            expect(spinner_locator).to_be_hidden(timeout=90000)

            try:
                page.get_by_role("button", name="Cerrar.").click(force=True, timeout=5000)
            except TimeoutError:
                pass

            page.get_by_role("textbox", name=re.compile("Número de identificación")).fill(cedula)
            page.get_by_role("button", name=re.compile("Consultar estado de cuenta")).click(force=True)
            
            seccion_resultados = page.locator(".iq-estado-section")
            expect(seccion_resultados).to_be_visible()
            
            html_resultados = seccion_resultados.inner_html().lower()

            if "no posee a la fecha pendientes de pago" in html_resultados:
                browser.close()
                return f"✅ ¡Excelentes noticias! La cédula *{cedula}* no tiene comparendos ni acuerdos de pago registrados en el SIMIT."

            try:
                tabla = seccion_resultados.locator("table.table-responsive")
                expect(tabla).to_be_visible()
                filas = tabla.locator("tbody > tr").all()
                resultado = formatear_resultados(cedula, filas)
                
            except TimeoutError:
                resultado = f"🚨 La cédula *{cedula}* parece tener comparendos, pero no se encontró una tabla de acuerdos de pago. Verifica directamente en el sitio web."
            
            browser.close()
            return resultado

    except Exception as e:
        print(f"❌ Error consultando el SIMIT: {e}")
        return "⚠️ Ocurrió un error. El sitio del SIMIT tardó demasiado en responder o está caído. Esto puede deberse a una conexión lenta. Intenta de nuevo más tarde."
