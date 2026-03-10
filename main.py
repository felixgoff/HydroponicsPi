import network
import socket
import dht
import machine
from machine import Pin
import time
import json

# WiFi credentials
SSID = "Bulbasaur"

# Choose mode: True = Access Point, False = Station (connect to existing WiFi)
AP_MODE = True

# DHT11 setup on GPIO 0
sensorBase = dht.DHTBase(Pin(0, Pin.OUT, Pin.PULL_DOWN))
sensor = dht.DHT11(Pin(0, Pin.OUT, Pin.PULL_DOWN))

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
        sensor.measure()
        return {
            "temperature_c": sensor.temperature(),
            "humidity_percent": sensor.humidity(),
            "status": "ok"
        }
    except Exception as e:
        return {
            str(e)
        }

def handle_request(conn):
    request = conn.recv(1024).decode()
    
    # Only respond to GET /
    if "GET /" in request:
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

# Main
print(read_sensors())
if AP_MODE:
    ip = start_ap()

server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('0.0.0.0', 80))  # Listen on ALL interfaces
server.listen(1)

while True:
    conn, addr = server.accept()
    print("Request from:", addr)
    handle_request(conn)