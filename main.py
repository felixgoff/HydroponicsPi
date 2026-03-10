import network
import time

SSID = "Wifi"
PASSWORD = "12345678"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

print("Scanning for networks...")
networks = wlan.scan()
for n in networks:
    print("Found:", n[0])

print("Connecting to:", SSID)
wlan.connect(SSID, PASSWORD)

for i in range(20):
    print("Status:", wlan.status())
    if wlan.isconnected():
        print("Connected! IP:", wlan.ifconfig()[0])
        break
    time.sleep(1)

if not wlan.isconnected():
    print("Failed! Final status:", wlan.status())