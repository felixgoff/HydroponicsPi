package main

import (
	"log/slog"
	"machine"
	"time"
)

func main() {
	for !machine.Serial.DTR() {
		time.Sleep(100 * time.Millisecond)
	}
	logger := slog.New(slog.NewTextHandler(machine.Serial, &slog.HandlerOptions{
		Level: slog.LevelInfo,
	}))
	logger.Info("Hello, world!")
}
