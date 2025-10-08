from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import random

app = FastAPI()
app.mount("/js", StaticFiles(directory="js"), name="js")

# mémoire temporaire : {user_id: {"name": ..., "age": ..., "contaminated": bool}}
users = {}
clients = {}

@app.get("/")
def get_home():
    with open("index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    uid = id(websocket)
    clients[uid] = websocket

    try:
        while True:
            data = await websocket.receive_json()
            # Si le client envoie ses infos
            if data.get("action") == "create_user":
                name = data.get("name")
                age = data.get("age")
                users[uid] = {"name": name, "age": age, "contaminated": random.choice([True, False])}
                await websocket.send_json({
                    "msg": "user_created",
                    "user": users[uid]
                })

            # Si le client demande son état de contamination
            elif data.get("action") == "check_status":
                user = users.get(uid)
                if user:
                    await websocket.send_json({
                        "msg": "status",
                        "contaminated": user["contaminated"]
                    })
    except WebSocketDisconnect:
        users.pop(uid, None)
        clients.pop(uid, None)
        print(f"Client {uid} disconnected")

