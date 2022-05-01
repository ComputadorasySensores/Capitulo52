import network, urequests, utime, machine
from machine import RTC, I2C, Pin
from ssd1306 import SSD1306_I2C

ssid = "Nombre de tu red WiFi" # No olvides colocar el nombre tu red WiFi
password = "Tu Contraseña"  # No olvides colocar tu contraseña
url = "http://worldtimeapi.org/api/timezone/America/Argentina/Buenos_Aires" # zonas en: http://worldtimeapi.org/timezones

print("Conectando ...")
oled = SSD1306_I2C(128, 64, I2C(0,scl=Pin(22), sda=Pin(21)))
oled.fill(0)
oled.text("Conectando ...", 0, 0)
oled.show()

rtc = RTC()

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(ssid, password)

while not wifi.isconnected():
    pass

print("IP:", wifi.ifconfig()[0], "\n")
oled.text("Conectado con IP: ", 0, 35)
oled.text(" " + str(wifi.ifconfig()[0]), 0, 45)
oled.show()

ultima_peticion = 0
intervalo_peticiones = 60  # en segundos

while True:
    
    if not wifi.isconnected():
        print("fallo de conexión a WiFi")
        #machine.reset()
    
    if (utime.time() - ultima_peticion) >= intervalo_peticiones:
        response = urequests.get(url)
    
        if response.status_code == 200:
            print("Respuesta:\n", response.text)
            
            datos_objeto = response.json()
            fecha_hora = str(datos_objeto["datetime"])
            año = int(fecha_hora[0:4])
            mes = int(fecha_hora[5:7])
            día = int(fecha_hora[8:10])
            hora = int(fecha_hora[11:13])
            minutos = int(fecha_hora[14:16])
            segundos = int(fecha_hora[17:19])
            sub_segundos = int(round(int(fecha_hora[20:26]) / 10000))
        
            rtc.datetime((año, mes, día, 0, hora, minutos, segundos, sub_segundos))
            ultima_peticion = utime.time()
            print("RTC actualizado\n")
   
        else:
            print("respuesta no válida: RTC no actualizado")
    
    fecha_pantalla = "Fecha:{2:02d}/{1:02d}/{0:4d}".format(*rtc.datetime())
    hora_pantalla = "Hora: {4:02d}:{5:02d}:{6:02d}".format(*rtc.datetime())

    oled.fill(0)
    oled.text("ESP32 Reloj Web", 0, 5)
    oled.text(fecha_pantalla, 0, 25)
    oled.text(hora_pantalla, 0, 45)
    oled.show()
    
    utime.sleep(0.1)
