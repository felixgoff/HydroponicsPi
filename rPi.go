package main

import (
	"machine"
	"net/http"
	"time"

	"tinygo.org/x/drivers/dht"
	"tinygo.org/x/drivers/net/link"
)

var sensor dht.Device

func connectWifi() {

	ssid := "ACAGuest"
	pass := "FramtidNu"

	println("Connecting to WiFi...")
	err := link.Connect(ssid, pass)
	if err != nil {
		println("Error connecting to WiFi:", err.Error())
		return
	}
	println("Connected to WiFi!")
}

func readDHT() (int16, int16) {
	temp, hum, err := sensor.p
	if err != nil {
		return -1, -1
	}
	return temp, hum
}

func handler(w http.ResponseWriter, r *http.Request) {
	t, h := readDHT()
	w.Write([]byte("temp="))
	w.Write([]byte(string(t)))
	w.Write([]byte(" humidity="))
	w.Write([]byte(string(h)))
}

func main() {

	// DHT11 setup
	sensor = dht.New(machine.GPIO15, dht.DHT11)

	// connect wifi
	connectWifi()

	http.HandleFunc("/", handler)
	http.ListenAndServe(":80", nil)

	for {
		time.Sleep(time.Hour)
	}
}
