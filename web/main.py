import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from enum import Enum
from typing import List, Optional

from db import Neo4JDB, TemplateRequests

app = FastAPI()
app.mount("/js", StaticFiles(directory="js"), name="js")
clients = {}
db = Neo4JDB()

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
            print(f"[WS {uid}] received : {data}")
            action = data.get("action")
            print(f"[WS {uid}] action : {action}")

            # --- Créer un utilisateur ---
            if action == "create_user":
                
                name = data.get("name")
                age = data.get("age")
                contaminated = False

                # Insérer dans Neo4j
                db.run_cypher(
                    TemplateRequests.ADD_USER.value,
                    {
                        "id": uid,
                        "first_name": name,
                        "last_name": "",
                        "age": age,
                        "has_covid": contaminated
                    }
                )

                # On renvoie les infos au client
                await websocket.send_json({
                    "msg": "user_created",
                    "user": {
                        "name": name,
                        "last_name": "",
                        "age": age,
                        "contaminated": contaminated
                    }
                })

            # --- Vérifier état / récupérer infos depuis la DB ---
            elif action in ("check_status", "get_info"):
                
                result = db.run_cypher(
                    TemplateRequests.GET_USER.value,
                    {"id": uid}
                )

                print(f"[WS {uid}] result : {result}")

                if result:
                    record = result[0]
                    await websocket.send_json({
                        "msg": "user_info",
                        "user": {
                            "name": record["first_name"],
                            "last_name": record["last_name"],
                            "age": record["age"],
                            "contaminated": record["has_covid"]
                        }
                    })
                else:
                    await websocket.send_json({
                        "msg": "error",
                        "detail": "Aucun utilisateur créé en DB"
                    })

    except WebSocketDisconnect:
        clients.pop(uid, None)
        print(f"Client {uid} disconnected")
