import random
import threading
import time
from flask import Blueprint, jsonify, request


MIN_PLAYERS = 2
TURN_SECONDS = 60
ROUND_END_DELAY = 5
MAX_SCORE_PER_GUESS = 100
MIN_SCORE_PER_GUESS = 10

PLAYER_TIMEOUT_SECONDS = 8

WORDS = [
    "apple", "guitar", "elephant", "rocket", "umbrella", "castle", "bicycle", "volcano", "penguin", "sandwich", "robot", "lighthouse", "skateboard", "cactus", "backpack", "speakers", "butterfly" 
]


lock = threading.Lock()

game_state = {
    "phase": "WAITING",
    "players": {},
    "turn_order": [],
    "turn_index": -1,
    "drawer": None,
    "word": None,
    "word_hint": None,
    "round_started_at": None,
    "phase_changed_at": None,
    "correct_guessers": set(),
    "round_end_info": None,
    "messages": [],
    "timer_token": 0,
    "recent_words": [],
}

AVOID_REPEAT_COUNT = 5

def public_state():
    now = time.time()
    time_remaining = None
    if game_state["phase_changed_at"] is not None:
        if game_state["phase"] == "DRAWING":
            time_remaining = max(0, TURN_SECONDS - (now - game_state["phase_changed_at"]))
        elif game_state["phase"] == "ROUND_END":
            time_remaining = max(0, ROUND_END_DELAY - (now - game_state["phase_changed_at"]))

    return {
        "phase": game_state["phase"],
        "players" : [
            {"username": u, "score": p["score"]} for u, p in game_state["players"].items()
        ],
        "drawer": game_state["drawer"],
        "word_hint": game_state["word_hint"],
        "time_remaining": time_remaining,
        "round_end_info": game_state["round_end_info"],
        "messages": game_state["messages"][-20:],
    }

def personal_state(username):
    result = {}
    if username == game_state["drawer"] and game_state["phase"] == "DRAWING":
        result["my_word"] = game_state["word"]
    return result

def make_hint(word):
    return " ".join("_" for _ in word)

def reveal_hint(word, revealed_count):
    chars = list(word)
    indices = list(range(len(chars)))
    random.shuffle(indices)
    shown = set(indices[:revealed_count])
    return " ".join(c if i in shown else "_" for i, c in enumerate(chars))

def pick_random_word():
    available = [w for w in WORDS if w not in game_state["recent_words"]]
    if not available:
        available = WORDS
    word = random.choice(available)
    game_state["recent_words"].append(word)
    game_state["recent_words"] = game_state["recent_words"][-AVOID_REPEAT_COUNT:]
    return word

def push_message(kind, **fields):
    msg = {"kind": kind, "at": time.time(), **fields}
    game_state["messages"].append(msg)

def drop_stale_players():
    now = time.time()
    stale = [
        u for u, p in game_state["players"].items()
        if now - p["last_seen"] > PLAYER_TIMEOUT_SECONDS
    ]
    for username in stale:
        remove_player(username, reason = "timeout")

def remove_player(username, reason):
    if username not in game_state["players"]:
        return
    del game_state["players"][username]
    if username in game_state["turn_order"]:
        idx = game_state["turn_order"].index(username)
        game_state["turn_order"].remove(username)
        if idx <= game_state["turn_index"] and game_state["turn_index"] > 0:
            game_state["turn_index"] -= 1
    game_state["correct_guessers"].discard(username)
    push_message("player_left", username=username, reason=reason)

    if username == game_state["drawer"]:
        if game_state["phase"] == "DRAWING":
            force_end_round(reason="drawer_left")
            return

    if len(game_state["players"]) < MIN_PLAYERS and game_state["phase"] != "WAITING":
        game_state["phase"] = "WAITING"
        game_state["phase_changed_at"] = time.time()

def begin_drawing_phase():
    if not game_state["turn_order"]:
        game_state["phase"] = "WAITING"
        game_state["phase_changed_at"] = time.time()
        return
    
    game_state["turn_index"] = (game_state["turn_index"] + 1) % len(game_state["turn_order"])
    drawer = game_state["turn_order"][game_state["turn_index"]]
    if drawer not in game_state["players"]:
        game_state["turn_order"].remove(drawer)
        if not game_state["turn_order"]:
            game_state["phase"] = "WAITING"
            game_state["phase_changed_at"] =time.time()
            return
        if game_state["turn_index"] >= len(game_state["turn_order"]):
            game_state["turn_index"] = 0
        return begin_drawing_phase()
    
    word = pick_random_word()
    game_state["phase"] = "DRAWING"
    game_state["phase_changed_at"] = time.time()
    game_state["drawer"] = drawer
    game_state["word"] = word
    game_state["word_hint"] = make_hint(word)
    game_state["round_started_at"] = time.time()
    game_state["correct_guessers"] = set()
    game_state["round_end_info"] = None

    push_message("drawing_started", drawer = drawer)

    start_timer(seconds = TURN_SECONDS, on_expire=lambda: force_end_round(reason = "timeout"))
    half = TURN_SECONDS / 2
    def reveal():
        with lock:
            if game_state["phase"] == "DRAWING" and game_state["word"] == word:
                game_state["word_hint"] = reveal_hint(word, revealed_count=1)
    threading.Timer(half, reveal).start()



def force_end_round(reason):
        with lock:
            if game_state["phase"] != "DRAWING":
                return
            game_state["phase"] = "ROUND_END"
            word = game_state["word"]
            game_state["phase_changed_at"] = time.time()
            game_state["round_end_info"] = {
                "word": word,
                "reason": reason,
                "scores": [
                    {"username": u, "score": p["score"]} for u, p in game_state["players"].items()
                ],
            }
            push_message("round_end", word = word, reason = reason)
            
            def advance():
                with lock:
                    if len(game_state["players"]) < MIN_PLAYERS:
                        game_state["phase"] = "WAITING"
                        game_state["phase_changed_at"] = time.time()
                    else:
                        begin_drawing_phase()
            threading.Timer(ROUND_END_DELAY, advance).start()
    
def start_timer(seconds, on_expire):
    game_state["timer_token"] += 1
    my_token = game_state["timer_token"]

    def fire():
        with lock:
            if game_state["timer_token"] != my_token:
                return
            on_expire()
    
    threading.Timer(seconds, fire).start()

def create_game_blueprint(get_curr_username):
    game_routes = Blueprint("game", __name__, url_prefix="/api/game")

    def require_username():
        username = get_curr_username()
        if not username:
            return None, (jsonify({"error": "Invalid username"}), 401)
        return username, None
    
    @game_routes.route("/join", methods = ["POST"])
    def join():
        username, err = require_username()
        if err:
            return err
        
        with lock:
            drop_stale_players()
            if username not in game_state["players"]:
                game_state["players"][username] = {"score": 0, "last_seen": time.time()}
                game_state["turn_order"].append(username)
                push_message("player_joined", username = username)
            else:
                game_state["players"][username]["last_seen"] = time.time()

            if (game_state["phase"] == "WAITING" and len(game_state["players"]) >= MIN_PLAYERS):
                game_state["turn_index"] = -1
                begin_drawing_phase()
            
            state = public_state()
            state.update(personal_state(username))
        
        return jsonify(state)
    
    @game_routes.route("/state", methods = ["GET"])
    def state():
        username, err = require_username()
        if err:
            return err

        with lock:
            drop_stale_players()

            if username not in game_state["players"]:
                return jsonify({"error": "Not in game"}), 409

            game_state["players"][username]["last_seen"] = time.time()
            result = public_state()
            result.update(personal_state(username))

        return jsonify(result)

    @game_routes.route("/guess", methods = ["POST"])
    def guess():
        username, err = require_username()
        if err:
            return err

        data = request.get_json(silent=True) or {}
        guess_text = data.get("text", "").strip().lower()
        if not guess_text:
            return jsonify({"error": "Empty guess"}), 400

        with lock:
            if username not in game_state["players"]:
                return jsonify({"error": "Not in game"}), 409
            game_state["players"][username]["last_seen"] = time.time()

            if game_state["phase"] != "DRAWING":
                return jsonify({"error": "Not in drawing phase"}), 409
            if username == game_state["drawer"]:
                return jsonify({"error": "The drawer can't guess their own word"}), 403
            if username in game_state["correct_guessers"]:
                return jsonify({"error": "Already guessed correctly this round"}), 409

            word = (game_state["word"] or "").lower()
            is_correct = guess_text == word
            round_just_ended = False

            if is_correct:
                elapsed = time.time() - game_state["round_started_at"]
                fraction_remaining = max(0.0, 1 - (elapsed / TURN_SECONDS)) 
                points = int(
                    MIN_SCORE_PER_GUESS + fraction_remaining * (MAX_SCORE_PER_GUESS - MIN_SCORE_PER_GUESS)
                ) 
                game_state["players"][username]["score"] += points
                game_state["correct_guessers"].add(username)
                push_message("correct_guess", username = username, points = points)

                non_drawers = [u for u in game_state["players"] if u != game_state["drawer"]]
                if non_drawers and all(u in game_state["correct_guessers"] for u in non_drawers):
                    round_just_ended = True
            else:
                push_message("chat_guess", username = username, text = guess_text)

            result = public_state()
            result["correct"] = is_correct

        if round_just_ended:
            force_end_round(reason = "everyone_guessed")

            with lock:
                result = public_state()
                result["correct"] = True
        return jsonify(result)
    
    @game_routes.route("/leave", methods = ["POST"])
    def leave():
        username, err = require_username()
        if err:
            return err
        with lock:
            remove_player(username, reason = "left")
            result = public_state()
        return jsonify(result)
    
    return game_routes
          
