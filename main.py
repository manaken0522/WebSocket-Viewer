import json
import threading
import time
import websocket

token = ""

def on_open(ws):
	ws.send(json.dumps({"op":2,"d":{"token":token,"capabilities":30717,"properties":{"os":"Windows","browser":"Chrome","device":"","system_locale":"ja-JP","browser_user_agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36","browser_version":"128.0.0.0","os_version":"10","referrer":"","referring_domain":"","referrer_current":"","referring_domain_current":"","release_channel":"stable","client_build_number":327446,"client_event_source":None},"presence":{"status":"unknown","since":0,"activities":[],"afk":False},"compress":False,"client_state":{"guild_versions":{}}}}))
	ws.send(json.dumps({"op":4,"d":{"guild_id":None,"channel_id":None,"self_mute":True,"self_deaf":True,"self_video":False,"flags":2}}))

heartbeat_interval = None
gateway_sequence = None

def on_message(ws, _message):
    print(_message)
    print("-------------------------")
    message = json.loads(_message)
    if "s" in message.keys():
        gateway_sequence = message["s"]
    elif message["op"] == 10:
        heartbeat_interval = message["d"]["heartbeat_interval"]/1000

def send_ping():
    while True:
        if heartbeat_interval != None:
            time.sleep(heartbeat_interval)
            ws.send(json.dumps({"op":1,"d":gateway_sequence}))

threading.Thread(target=send_ping).start()
ws = websocket.WebSocketApp("wss://gateway.discord.gg/?encoding=json&v=9", on_open=on_open, on_message=lambda ws,message:threading.Thread(target=on_message,args=(ws,message)).start())
ws.run_forever()