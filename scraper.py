from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import re
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from datetime import datetime, timezone
import mysql.connector
import csv




def scrape_corner(value, corner_name): ##Scrapping de una zona especifica del mapa 
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    key = "livemapMapPosition"

    driver.get("https://www.waze.com/es-419/live-map/")
    time.sleep(5)
    driver.execute_script(f"window.localStorage.setItem('{key}','{value}')")
    time.sleep(5)
    driver.refresh()
    time.sleep(7) 

    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, "html.parser")
    alerts = []

    for marker in soup.find_all("div"):
        classes = marker.get("class", [])
        if not classes:
            continue
        for cls in classes:
            if "wm-alert-icon--" in cls or "wm-alert-cluster-icon--" in cls:
                alert_type = cls.replace("wm-alert-icon--", "").replace("wm-alert-cluster-icon--", "")
                alerts.append({
                    "type": alert_type,
                    "corner": corner_name,
                    "timestamp": time.time()
                })
                break  

    return alerts

def scrape_waze_alerts_parallel(): #coordenadas para el scraping 
    corners = {
        "Maipu": '{ "value": "-70.73620319366456,-33.49867548541488,-70.68998336791994,-33.46545873876678", "expires": 1734649008597, "version": "0.0.0" }',
        "Cochali": '{ "value": "-70.74238300323488,-33.42742998368805,-70.69616317749025,-33.39418593758076", "expires": 1734650266912, "version": "0.0.0" }',
        "Providencia": '{ "value": "-70.58376789093019,-33.42220062164151,-70.53754806518556,-33.38895457380163", "expires": 1734650297264, "version": "0.0.0" }',
        "Pudahuel": '{ "value": "-70.59226512908937,-33.48851136814119,-70.54604530334474,-33.45529072371885", "expires": 1734650320123, "version": "0.0.0" }'
    }

    alerts = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(scrape_corner, value, name) for name, value in corners.items()]
        for future in futures:
            try:
                result = future.result()
                alerts.extend(result)
            except Exception as e:
                print(f" Error en hilo de scraping: {e}")
    return alerts

def main():
     
     #conexion con la base de datos que se creo en el docker
    conexion =  mysql.connector.connect( 
        host='base',
        user='usuario',
        password='pass123',
        database='mi_base'
    )

    total_alertas = 0

    while total_alertas < 10000: 
        alertas = scrape_waze_alerts_parallel()
        total_alertas += len(alertas)

        if not alertas:
         print("No hay alertas para guardar.")

        print(f"Total de alertas recibidas: {len(alertas)}")
    
        grouped = defaultdict(list)
        now = datetime.now(timezone.utc)
        window_start = now.replace(second=0, microsecond=0)
        window_end = now.replace(second=59, microsecond=999999)
    
        for alert in alertas:
            key = (alert['type'], alert['corner'])
            grouped[key].append(alert)
    
        total_guardadas = 0
        cursor = conexion.cursor()
        for (alert_type, corner), items in grouped.items():
            count = len(items)
            query = """
            INSERT INTO alerts (window_start, window_end, type, corner, count)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (window_start, window_end, alert_type, corner, count))
            total_guardadas += 1
        conexion.commit()
        cursor.close()

        print(f"Acumuladas: {total_alertas}/{10000}")
        time.sleep(2)

    print("Alertas guardadas en base de datos")
        
    cursor = conexion.cursor()
    cursor.execute("SELECT window_start, window_end, type, corner, count FROM alerts")

    with open('alerts.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['window_start', 'window_end', 'type', 'corner', 'count'])
        for row in cursor.fetchall():
            writer.writerow(row)

    cursor.close()
    print("CSV exportado =  'alerts.csv'")

if __name__ == "__main__":
    main()

