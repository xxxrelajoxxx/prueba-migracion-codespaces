from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import urllib.parse
import os
import shutil
import time

def main():
    # --- 1. CONFIGURACIÓN DE DATOS Y RUTAS (ADAPTADO A CODESPACES) ---
    usuario = "david.taipe.pe"
    password = "Relajo692015"
    
    # Rutas relativas dentro del contenedor de Linux en GitHub Codespaces
    # Guardará los reportes en una carpeta 'Data' dentro de tu repositorio
    ruta_destino_final = os.path.join(os.getcwd(), "Data")
    # Carpeta temporal de descargas dentro del espacio de trabajo
    carpeta_descargas = os.path.join(os.getcwd(), "descargas_temporales")
    
    if not os.path.exists(carpeta_descargas):
        os.makedirs(carpeta_descargas)

    # Escapar caracteres especiales en la contraseña
    password_safe = urllib.parse.quote(password)
    
    url_host = "rslsur.ajegroup.com"
    url_path = "/PEReports/report/Reporte%20Flete"
    url_con_login = f"https://{usuario}:{password_safe}@{url_host}{url_path}"

    nombre_original = "Reporte Flete.xlsx" 
    nuevo_nombre = "Reporte Flete.xlsx"

    # --- 2. CÁLCULO DE FECHAS ---
    hoy = datetime.now()
    fecha_inicial = hoy - timedelta(days=60)
    fmt_inicio = fecha_inicial.strftime('%d/%m/%Y')
    fmt_final = hoy.strftime('%d/%m/%Y')

    # --- CONFIGURACIÓN HEADLESS (OBLIGATORIA PARA LA NUBE) ---
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new') 
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080') 
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # Habilitar descargas en modo Headless dentro de Linux
    prefs = {
        "download.default_directory": carpeta_descargas,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)

    driver = None

    try:
        print(f"🚀 Iniciando Chrome en la nube... Rango: {fmt_inicio} al {fmt_final}")
        
        # En Codespaces NO usamos 'Service(ruta_driver)'. El driver de Linux se detecta solo.
        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, 80)

        driver.get(url_con_login)
        time.sleep(20) # Espera carga ReportViewer

        # Intento de conexión
        try:
            driver.switch_to.frame(0)
            print("✔ Foco cambiado al reporte.")
        except Exception as e:
            if "ERR_NAME_NOT_RESOLVED" in str(e):
                print("\n❌ ERROR: No se reconoce el dominio 'rslsur.ajegroup.com'.")
                print("⚠ NOTA IMPORTANTE: Al estar en la nube de GitHub, este servidor necesita")
                print("acceso público a la URL o configurar una VPN hacia la red de la empresa.")
                return 
            raise e
        
        # --- 3. LIMPIAR CARPETA DE DESCARGAS ---
        print("🧹 Limpiando archivos previos en Descargas temporales...")
        for archivo in os.listdir(carpeta_descargas):
            if "Reporte Flete" in archivo:
                try:
                    os.remove(os.path.join(carpeta_descargas, archivo))
                    print(f"Eliminado temporal previo: {archivo}")
                except Exception as e:
                    print(f"No se pudo eliminar {archivo}: {e}")

        # 4. TEXTBOX 1: Fecha Inicial
        print(f"✍ Ingresando fecha inicial: {fmt_inicio}")
        text_box1 = driver.find_element(By.ID, 'ReportViewerControl_ctl04_ctl05_txtValue')
        text_box1.clear()
        time.sleep(1)
        text_box1.send_keys(fmt_inicio)
        text_box1.send_keys(Keys.ENTER)

        # 5. TEXTBOX 2: Fecha Final
        print(f"✍ Ingresando fecha final: {fmt_final}")
        text_box2 = driver.find_element(By.ID, 'ReportViewerControl_ctl04_ctl07_txtValue')
        text_box2.clear()
        time.sleep(1)
        text_box2.send_keys(fmt_final)
        text_box2.send_keys(Keys.ENTER)

        # Buscar y ejecutar reporte
        Result_Search = wait.until(EC.element_to_be_clickable((By.ID, "ReportViewerControl_ctl04_ctl00")))
        time.sleep(5)
        Result_Search.click()
        print("⏳ Procesando reporte en el servidor (Esperando 100s)...")
        time.sleep(100)

        # Exportar
        boton_exportar = driver.find_element(By.ID, "ReportViewerControl_ctl05_ctl04_ctl00_ButtonImg")
        boton_exportar.click()

        try:
            opcion_excel = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@title='Excel']")))
            opcion_excel.click()
            print("📥 Exportación a Excel iniciada.")
        except:
            opcion_excel = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Excel")))
            opcion_excel.click()

        print("📥 Descargando archivo...")
        time.sleep(35)

        # Mover archivo al destino final localizado en el repositorio
        ruta_temp = os.path.join(carpeta_descargas, nombre_original)
        ruta_final_completa = os.path.join(ruta_destino_final, nuevo_nombre)
        
        if os.path.exists(ruta_temp):
            if not os.path.exists(ruta_destino_final): 
                os.makedirs(ruta_destino_final)
            shutil.move(ruta_temp, ruta_final_completa)
            print(f"🎉 ¡Éxito! Archivo guardado en repositorio: {ruta_final_completa}")
        else:
            print("❌ Error: El archivo no se encontró en las descargas de la nube.")

    except Exception as e:
        print(f"❌ Error durante la ejecución: {e}")
        if driver: 
            driver.save_screenshot("error_debug.png")
            print("📸 Captura de pantalla de error guardada como 'error_debug.png'.")
        
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
