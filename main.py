import network
import socket
import dht
import machine
from machine import Pin, ADC, PWM
import time
import json
import _thread

# WiFi credentials
SSID = "Bulbasaur"

# Choose mode: True = Access Point, False = Station (connect to existing WiFi)
AP_MODE = True


Rpin = PWM(Pin(15, Pin.OUT))
Gpin = PWM(Pin(14, Pin.OUT))
Bpin = PWM(Pin(13, Pin.OUT))

Rpin.freq(1000)
Gpin.freq(1000)
Bpin.freq(1000)

waterSignal = ADC(Pin(26))
waterPower = Pin(1, Pin.OUT)
# DHT11 setup on GPIO 0
sensorBase = dht.DHTBase(Pin(0, Pin.OUT, Pin.PULL_DOWN))
sensor = dht.DHT11(Pin(0, Pin.OUT, Pin.PULL_DOWN))
def UpdateStatus(temp, hum, water):
    status = False
    print(water)
    if (water > 15 and water < 30):
        status = True
    if (status):
        Rpin.duty_u16(0)
        Gpin.duty_u16(65535)
        Bpin.duty_u16(0)
    else:
        value = 0
        if water < 20:
            value = 1 - water/15*5
        else:
            value = water/30*5 - 1
        value = max(0, min(1, value))*65535  # Clamp to [0, 1] and convert to 16-bit
        print(value)
        Rpin.duty_u16(int(value))
        Gpin.duty_u16(int(65535 - value))
        Bpin.duty_u16(0)
def start_ap():
    wlan = network.WLAN(network.AP_IF)

    # some ports use 'ssid'/'key', others use 'essid'/'password' — try both
    try:
        wlan.config(ssid=SSID, security=0, key="")
    except Exception as e:
        print("AP config failed:", e)


    time.sleep(1)
    wlan.ifconfig(('192.168.4.1', '255.255.255.0', '192.168.0.1', '8.8.8.8'))
    ip = wlan.ifconfig()[0]
    print("Access Point started:", SSID)
    print("AP IP:", ip)
    return ip

def read_sensors():
    try:
        waterPower.value(1)  # Power on the water sensor
        time.sleep_ms(10)  # Wait for the sensor to stabilize
        sensor.measure()
        water = waterSignal.read_u16() // 256  # Convert to 8-bit value (0-255)
        temp = sensor.temperature()
        hum = sensor.humidity()
        if water < 5:
            water = 0
        waterPower.value(0)  # Power off the water sensor to save energy
        return {
            "water_level": water,
            "temperature_c": temp,
            "humidity_percent": hum,
            "status": "ok"
        }
    except Exception as e:
        return {
            "water_level": 0,
            "temperature_c": 0,
            "humidity_percent": 0,
            "status": "error",
            "message": str(e)
        }
    

def handle_request(conn):
    request = conn.recv(1024).decode()
    
    # Only respond to GET /api
    if "GET /api" in request:
        data = read_sensors()
        body = json.dumps(data)
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: application/json\r\n"
            "Content-Length: {}\r\n"
            "\r\n"
            "{}"
        ).format(len(body), body)
    else:
        response = "HTTP/1.1 404 Not Found\r\n\r\n"
    
    conn.send(response.encode())
    conn.close()

def server_thread():
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 80))
    server.listen(2)
    print("HTTP server running on :80")

    while True:
        try:
            conn, addr = server.accept()
            print("Request from:", addr)
            handle_request(conn)
        except Exception as e:
            print("HTTP error:", e)

# Main
print(read_sensors())
if AP_MODE:
    ip = start_ap()

_thread.start_new_thread(server_thread, ())
print("Server thread started")

while True:
    g = read_sensors()
    UpdateStatus(g["temperature_c"], g["humidity_percent"], g["water_level"])
    time.sleep_ms(100)