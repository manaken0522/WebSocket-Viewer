package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"time"

	"github.com/gorilla/websocket"
)

func main() {
	flag.Parse()

	token := flag.Arg(0)

	identify := "{\"op\":2,\"d\":{\"token\":\"" + token + "\",\"capabilities\":30717,\"properties\":{\"os\":\"Windows\",\"browser\":\"Chrome\",\"device\":\"\",\"system_locale\":\"ja\",\"browser_user_agent\":\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36\",\"browser_version\":\"131.0.0.0\",\"os_version\":\"10\",\"referrer\":\"\",\"referring_domain\":\"\",\"referrer_current\":\"\",\"referring_domain_current\":\"\",\"release_channel\":\"stable\",\"client_build_number\":356429,\"client_event_source\":null,\"has_client_mods\":false},\"presence\":{\"status\":\"unknown\",\"since\":0,\"activities\":[],\"afk\":false},\"compress\":false,\"client_state\":{\"guild_versions\":{}}}}"

	ws, _, _ := websocket.DefaultDialer.Dial("wss://gateway.discord.gg/?encoding=json&v=9", nil)
	defer ws.Close()

	ws.WriteMessage(websocket.TextMessage, []byte(identify))
	ws.WriteMessage(websocket.TextMessage, []byte("{\"op\":4,\"d\":{\"guild_id\":null,\"channel_id\":null,\"self_mute\":true,\"self_deaf\":false,\"self_video\":false,\"flags\":2}}"))
	ws.WriteMessage(websocket.TextMessage, []byte("{\"op\":3,\"d\":{\"status\":\"online\",\"since\":0,\"activities\":[],\"afk\":false}}"))

	var (
		sequence           int
		heartbeat_interval int
	)

	// heartbeat
	go func() {
		for {
			if sequence != 0 && heartbeat_interval != 0 {
				time.Sleep(time.Duration(heartbeat_interval) * time.Millisecond)
				ws.WriteMessage(websocket.PongMessage, []byte("{\"op\":1,\"d\":"+string(rune(sequence))+"}"))
			}
		}
	}()

	// receive
	for {
		_, message, _ := ws.ReadMessage()
		if message != nil {
			var f *os.File

			f, _ = os.Open("websocket.log")
			pastlog := make([]byte, 1024*1024)
			n, _ := f.Read(pastlog)
			f.Close()

			log := string(pastlog[:n]) + string(message) + "\n\n"

			f, _ = os.Create("websocket.log")
			f.Write([]byte(log))
			f.Close()

			fmt.Println(string(message))

			var messageInterface interface{}
			json.Unmarshal(message, &messageInterface)

			s := messageInterface.(map[string]interface{})["s"]
			if s != nil {
				sequence = int(s.(float64))
			}

			opcode := int(messageInterface.(map[string]interface{})["op"].(float64))
			switch opcode {
			case 10:
				heartbeat_interval = int(messageInterface.(map[string]interface{})["d"].(map[string]interface{})["heartbeat_interval"].(float64))
				fmt.Println(heartbeat_interval)
			}
		}
	}
}
