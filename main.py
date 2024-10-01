import json
import threading
import time
import tkinter
import websocket
from tkinter import ttk

messages = []
heartbeat_interval = None
gateway_sequence = None

def on_open(ws, token):
	ws.send(json.dumps({"op":2,"d":{"token":token,"capabilities":30717,"properties":{"os":"Windows","browser":"Chrome","device":"","system_locale":"ja-JP","browser_user_agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36","browser_version":"128.0.0.0","os_version":"10","referrer":"","referring_domain":"","referrer_current":"","referring_domain_current":"","release_channel":"stable","client_build_number":327446,"client_event_source":None},"presence":{"status":"unknown","since":0,"activities":[],"afk":False},"compress":False,"client_state":{"guild_versions":{}}}}))
	ws.send(json.dumps({"op":4,"d":{"guild_id":None,"channel_id":None,"self_mute":True,"self_deaf":True,"self_video":False,"flags":2}}))

def on_message(_message, tree):
    message = json.loads(_message)
    if "s" in message.keys():
        gateway_sequence = message["s"]
        messages.append(_message)
        tree.insert(parent="", index="end", values=[message["op"], message["s"], message["t"], json.dumps(message["d"])[0:29]])
    elif message["op"] == 10:
        heartbeat_interval = message["d"]["heartbeat_interval"]/1000

def send_ping(ws):
    while True:
        if heartbeat_interval != None:
            time.sleep(heartbeat_interval)
            ws.send(json.dumps({"op":1,"d":gateway_sequence}))

def start():
    ws = websocket.WebSocketApp("wss://gateway.discord.gg/?encoding=json&v=9", on_open=lambda ws:threading.Thread(target=on_open,args=(ws,token_var.get())).start(), on_message=lambda _,message:threading.Thread(target=on_message,args=(message,treeview)).start())
    threading.Thread(target=send_ping, args=(ws,)).start()
    threading.Thread(target=ws.run_forever).start()

def draw_message(event):
    message_text.delete(0., tkinter.END)
    message_text.insert(0., messages[int(treeview.focus()[1:], 16)-1])

window = tkinter.Tk()
token_var = tkinter.StringVar()
window.title("WebSocket Viewer")
window.geometry("1000x600")
window.resizable(False, False)

ttk.Label(text="WebSocket Viewer", font=("normal", 25)).grid(column=0, row=0)
ttk.Entry(textvariable=token_var, width=90).grid(column=1, row=0)

header = ttk.Frame()
header.grid(column=1, row=1)
ttk.Button(master=header, text="Start", width=15, command=start).grid(column=1, row=1)

treeview = ttk.Treeview(columns=["op", "s", "t", "d"], height=25)
treeview.grid(column=0, row=2)
treeview.column("#0",width=0, stretch="no")
treeview.column("op", width=50)
treeview.column("s", width=75)
treeview.column("t", width=150)
treeview.column("d", width=150)
treeview.heading("op", text="opcode",anchor="center")
treeview.heading("s", text="Suequence", anchor="center")
treeview.heading("t", text="Event name",anchor="center")
treeview.heading("d", text="Event data", anchor="center")
treeview.bind("<<TreeviewSelect>>", draw_message)

message_var = tkinter.StringVar()
message_text = tkinter.Text(width=80, height=36)
message_text.grid(column=1, row=2)

window.mainloop()
