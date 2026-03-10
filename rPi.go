package main

import (
	"log/slog"
	"machine"
	"net"
	"net/netip"
	"strconv"
	"time"

	"github.com/soypat/cyw43439"
	"github.com/soypat/cyw43439/examples/cywnet"
	"github.com/soypat/lneto/http/httpraw"
	"github.com/soypat/lneto/tcp"
	"github.com/soypat/lneto/x/xnet"
	"tinygo.org/x/drivers/dht"
)

var sensor dht.Device

const listenPort = 80
const loopSleep = 5 * time.Millisecond

func readDHT() (int16, uint16) {
	temp, hum, err := sensor.Measurements()
	if err != nil {
		return -1, 0
	}
	return temp, hum
}

func handler(conn *tcp.Conn, hdr *httpraw.Header) {
	defer conn.Close()
	const AsRequest = false
	var buf [64]byte
	hdr.Reset(nil)

	remoteAddr, _ := netip.AddrFromSlice(conn.RemoteAddr())
	println("incoming connection:", remoteAddr.String(), "from port", conn.RemotePort())

	for {
		n, err := conn.Read(buf[:])
		if n > 0 {
			hdr.ReadFromBytes(buf[:n])
			needMoreData, err := hdr.TryParse(AsRequest)
			if err != nil && !needMoreData {
				println("parsing HTTP request:", err.Error())
				return
			}
			if !needMoreData {
				break
			}
		}
		closed := err == net.ErrClosed || conn.State() != tcp.StateEstablished
		if closed {
			break
		} else if hdr.BufferReceived() >= 512 {
			println("too much HTTP data")
			return
		}
	}
	// Check requested requestedPage URI.
	var requestedPage page
	uri := hdr.RequestURI()
	switch string(uri) {
	case "/":
		println("Got request!")
		requestedPage = Root
	default:
		println("Unknown page requested:", string(uri))
		requestedPage = pageNotExists
	}

	// Prepare response with same buffer.
	hdr.Reset(nil)
	hdr.SetProtocol("HTTP/1.1")
	if requestedPage == pageNotExists {
		hdr.SetStatus("404", "Not Found")
	} else {
		hdr.SetStatus("200", "OK")
	}
	var body []byte
	switch requestedPage {
	case Root:
		temp, hum := readDHT()
		body = []byte("{\"temperature\": " + strconv.FormatInt(int64(temp), 10) + ", \"humidity\": " + strconv.FormatInt(int64(hum), 10) + "}")
		hdr.Set("Content-Type", "application/json")
	}
	if len(body) > 0 {
		hdr.Set("Content-Length", strconv.Itoa(len(body)))
	}
	responseHeader, err := hdr.AppendResponse(buf[:0])
	if err != nil {
		println("error appending:", err.Error())
	}
	conn.Write(responseHeader)
	if len(body) > 0 {
		_, err := conn.Write(body)
		if err != nil {
			println("writing body:", err.Error())
		}
		time.Sleep(loopSleep)
	}
	// connection closed automatically by defer.
}

type page uint8

const (
	pageNotExists page = iota
	Root               // /
)

var (
	requestedIP = [4]byte{192, 168, 1, 99}
	cystack     *cywnet.Stack
)

func main() {

	for !machine.Serial.DTR() {
		time.Sleep(100 * time.Millisecond)
	}

	// DHT11 setup

	ssid := "Felix’s iPhone"
	pass := "doorBella"

	println("Connecting to WiFi...")

	time.Sleep(2 * time.Second) // Give time to connect to USB and monitor output.

	logger := slog.New(slog.NewTextHandler(machine.Serial, &slog.HandlerOptions{
		Level: slog.LevelInfo,
	}))

	devcfg := cyw43439.DefaultWifiConfig()
	devcfg.Logger = logger
	var err error
	cystack, err = cywnet.NewConfiguredPicoWithStack(ssid, pass, devcfg, cywnet.StackConfig{
		Hostname:              "http-pico",
		MaxTCPPorts:           1,
		EnableRxPacketCapture: true,
		EnableTxPacketCapture: true,
	})
	if err != nil {
		panic("setup failed:" + err.Error())
	}

	go loopForeverStack(cystack)

	dhcpResults, err := cystack.SetupWithDHCP(cywnet.DHCPConfig{
		RequestedAddr: netip.AddrFrom4(requestedIP),
	})
	if err != nil {
		panic("DHCP failed:" + err.Error())
	}
	println("Connected to WiFi!")
	tcpPool, err := xnet.NewTCPPool(xnet.TCPPoolConfig{
		PoolSize:           3,
		QueueSize:          3,
		TxBufSize:          2048,
		RxBufSize:          256,
		EstablishedTimeout: 5 * time.Second,
		ClosingTimeout:     5 * time.Second,
		NewUserData: func() any {
			var hdr httpraw.Header
			buf := make([]byte, 512)
			hdr.Reset(buf)
			return &hdr
		},
		// Logger:             traceLog.WithGroup("tcppool"),
		// ConnLogger:         traceLog,
	})

	if err != nil {
		panic("tcppool create:" + err.Error())
	}
	stack := cystack.LnetoStack()
	listenAddr := netip.AddrPortFrom(dhcpResults.AssignedAddr, listenPort)

	var listener tcp.Listener
	err = listener.Reset(listenPort, tcpPool)
	if err != nil {
		panic("listener reset:" + err.Error())
	}
	err = stack.RegisterListener(&listener)
	if err != nil {
		panic("listener register:" + err.Error())
	}

	logger.Info("listening",
		slog.String("addr", "http://"+listenAddr.String()),
	)

	sensor = dht.New(machine.GPIO0, dht.DHT11)

	for {
		if listener.NumberOfReadyToAccept() == 0 {
			time.Sleep(5 * time.Millisecond)
			tcpPool.CheckTimeouts()
			continue
		}

		conn, httpBuf, err := listener.TryAccept()
		if err != nil {
			logger.Error("listener accept:", slog.String("err", err.Error()))
			time.Sleep(time.Second)
			continue
		}
		go handler(conn, httpBuf.(*httpraw.Header))
	}
}
func loopForeverStack(stack *cywnet.Stack) {
	for {
		send, recv, _ := stack.RecvAndSend()
		if send == 0 && recv == 0 {
			time.Sleep(loopSleep)
		}
	}
}
