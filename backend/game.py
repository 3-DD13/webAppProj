import random
import threading
import time
from flask_socketio import emit, join_room, leave_room


ROOM_ID = "main"
MIN_PLAYERS = 2
TURN_SECONDS = 60
PICK_SECONDS = 15
ROUND_END_DELAY = 5
MAX_SCORE_PER_GUESS = 100
MIN_SCORE_PER_GUESS = 10

WORDS = [
    "apple", "guitar", "elephant", "rocket", "umbrella", "castle", "bicycle", "volcano", "penguin", "sandwich", "robot", "lighthouse", "skateboard", "cactus", "backpack", "speakers", "butterfly" 
]


_lock = threading.Lock()

game_state = {
    "phase": "WAITING",
    "players": {},
    "turn_order": [],
    "drawer_sid": None,
    "word": None,
    "word_hint": None,
    "round_started_at": None,
    "correct_guesses": set(),
    "timer_token": 0,
}

def public_state():
    return {
        "phase": game_state["phase"],
        "players" : [
            {"username": p["username"], "score": p["score"], "sid": sid} for sid, p in game_state["players"].items()
        ],
        "drawer_sid": game_state["drawer_sid"],
        "word_hint": game_state["word_hint"],
    }

def broadcast_state(socketio):
    socketio.emit("game_state", public_state(), room = ROOM_ID)

def make_hint(word):
    return " ".join("_" for _ in word)

def reveal_hint(word, revealed_count):
    chars = list(word)
    indices = list(range(len(chars)))
    random.shuffle(indices)
    shown = set(indices[:revealed_count])
    return " ".join(c if i in shown else "_" for i, c in enumerate(chars))

def start_picking_phase(socketio):
    if not game_state["turn_order"]:
        game_state["phase"] = "WAITING"
        broadcast_state(socketio)
        return
    
    game_state["turn_order"] = (game_state["turn_index"] + 1) % len(game_state["turn_order"])
    drawer_sid = game_state["turn_order"][game_state["turn_index"]]
    if drawer_sid not in game_state["players"]:
        game_state["turn_order"].remove(drawer_sid)
        if game_state["turn_index"] >= len(game_state["turn_order"]):
            game_state["turn_index"] = 0
        return start_picking_phase(socketio)
    
    game_state["phase"] = "PICKING_WORD"
    game_state["drawer_sid"] = drawer_sid
    game_state["word"] = None
    game_state["word_hint"] = None
    game_state["correct_guesses"] = set()

    word_choices = random.sample(WORDS, k = min(3, len(WORDS)))

    socketio.emit(
        "word_choices",
        {"choices": word_choices}, 
        room = drawer_sid,
    )    
    broadcast_state(socketio)

    start_timer(
        socketio,
        seconds = PICK_SECONDS,
        on_expire = lambda: auto_pick_word(socketio, word_choices),
    )

    half = TURN_SECONDS / 2
    def reveal():
        with _lock:
            if game_state["phase"] == "DRAWING" and game_state["word"] == word:
                game_state["word_hint"] = reveal_hint(word, revealed_count=1)
                broadcast_state(socketio)
    threading.Timer(half, reveal).start()

def end_round(socketio, reason):
        with _lock:
            if game_state["phase"] not in ("DRAWING",):
                return
            game_state["phase"] = "ROUND_END"
            word = game_state["word"]
            socketio.emit(
                "round_end",
                {"Word": word, "reason": reason, "scores": public_state()["players"]},
                room = ROOM_ID,
            )
            broadcast_state(socketio)
    
def start_timer(socketio, seconds, on_expire):
    game_state["timer_token"] += 1
    my_token = game_state["timer_token"]

    def fire():
        with _lock:
            if game_state["timer_token"] != my_token:
                return
            on_expire()
    
    threading.Timer(seconds, fire).start()
