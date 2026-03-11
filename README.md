# HydroponicsPi

This is a school project built at NTI Lund. The goal is to monitor a hydroponics setup using a Raspberry Pi Pico W and a DHT11 sensor. The Pico W runs a small web server that returns sensor data as JSON when you send a GET request to it.

---

## How it works

The Pico W starts its own WiFi access point. When a device connects to it and sends a GET request, it responds with temperature and humidity data in JSON format. No router needed.

Example response:
```json
{"temperature_c": 22, "humidity_percent": 55, "status": "ok"}
```

---

## Requirements

- Raspberry Pi Pico W
- DHT11 sensor
- MicroPython
- Thonny (recommended editor)

---

## Setup

### 1. Flash MicroPython onto the Pico W

1. Download the latest MicroPython firmware for Pico W from [micropython.org/download/RPI_PICO_W](https://micropython.org/download/RPI_PICO_W/)
2. Hold down the **BOOTSEL** button on the Pico W while plugging it into your computer
3. Release the button — it will show up as a USB drive called **RPI-RP2**
4. Drag and drop the `.uf2` file onto it
5. It will reboot automatically with MicroPython installed

### 2. Install Thonny

Download and install Thonny from [thonny.org](https://thonny.org).

After installing:
1. Open Thonny
2. Go to **Tools > Options > Interpreter**
3. Select **MicroPython (Raspberry Pi Pico)**
4. Select the correct COM port

You should see a `>>>` prompt at the bottom. That means it is working.

### 3. Wire the DHT11 sensor

I dont know how to wire it.

### 4. Flash the code

1. Clone this repository:
```
git clone https://github.com/felixgoff/HydroponicsPi.git
```
2. Open `main.py` in Thonny
3. Save it to the Pico W as `main.py`
4. Run it

### 5. Connect and read data

1. On your phone or laptop, connect to the WiFi network called **Bulbasaur**  (no password)
2. Open a browser or send a GET request to:
```
http://192.168.4.1
```
3. You will get back a JSON response with the current temperature and humidity

---


## Todo

- Add water level sensor
- Add light sensor
- Build a proper frontend for the data
- Maybe add more Access Point configuration options

---

## Rules

- Do not vibe code the whole thing
- Using AI for help, suggestions, and understanding what code does is fine. Using it to just generate everything without understanding it is NOT allowed.
- Use a smart AI
# HydroponicsPi

This Github repository is for a school project.
