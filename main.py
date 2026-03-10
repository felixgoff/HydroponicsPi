import network
import socket
import dht
import machine
import time
import json

# WiFi credentials
SSID = "RaspberryPi-http"
PASSWORD = "pico" 

# Choose mode: True = Access Point, False = Station (connect to existing WiFi)
AP_MODE = True

# DHT11 setup on GPIO 0
sensor = dht.DHT11(machine.Pin(0))

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    
    print("Connecting to WiFi...")
    while not wlan.isconnected():
        time.sleep(0.5)
        print("status:", wlan.status())
    
    print("Connected!")
    ip = wlan.ifconfig()[0]
    print("Open this in your browser: http://" + ip)
    return ip

def start_ap():
    wlan = network.WLAN(network.AP_IF)
    wlan.active(True)

    # auth: 0=open, otherwise try common constants, fallback to 3 (WPA2)
    auth = getattr(network, "AUTH_WPA_WPA2_PSK", getattr(network, "SEC_WPA_WPA2", 3))

    # use password only if it's at least 8 chars (WPA2 requirement)
    pwd = PASSWORD if PASSWORD and len(PASSWORD) >= 8 else ""

    # some ports use 'ssid'/'key', others use 'essid'/'password' — try both
    try:
        wlan.config(ssid=SSID, key=pwd, authmode=auth, channel=6, hidden=False)
    except Exception:
        try:
            wlan.config(essid=SSID, password=pwd, authmode=auth, channel=6, hidden=False)
        except Exception as e:
            print("AP config failed:", e)

    time.sleep(1)
    ip = wlan.ifconfig()[0]
    print("Access Point started:", SSID)
    print("AP IP:", ip)
    if pwd == "":
        print("Open AP (no password). Set PASSWORD to a 8+ char string for WPA2.")
    else:
        print("AP running with WPA2 password.")
    print("Connect your phone/computer to the AP and open: http://" + ip)
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
            e
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
else:
    ip = connect_wifi()

server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('0.0.0.0', 80))  # Listen on ALL interfaces
server.listen(1)
print("Server running at http://" + ip)

while True:
    conn, addr = server.accept()
    print("Request from:", addr)
    handle_request(conn)