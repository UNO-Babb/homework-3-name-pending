from flask import Flask, jsonify, request, render_template
import random
import json

app = Flask(__name__)

# Game settings and initializations
NUM_TILES = 50  # Number of tiles on the board
FINAL_TILE = NUM_TILES - 1  # The final tile players must reach with an item to win
ATTRIBUTES = ['red', 'blue', 'green']  # Attribute options for pieces and zones
players = {}
zones = {}  # Tile zones with attributes
items = random.sample(range(NUM_TILES), 3)  # Place items randomly on the board
# Keep track of the current player
current_player = 1

# Initialize random attributes for zones
for i in range(NUM_TILES):
    if random.random() < 0.2:  # 20% of tiles are zones with attributes
        zones[i] = random.choice(ATTRIBUTES)

def roll_dice():
    return random.randint(1, 6)

def get_adjacent_tiles(position):
    """Simulate hexagonal adjacency logic, simplified here as linear movement."""
    return [max(0, position - 1), min(NUM_TILES - 1, position + 1)]

@app.route("/")
def index():
    return render_template("index.html")  # Render the main game board

@app.route('/start_game', methods=['POST'])
def start_game():
    player_count = request.json.get('player_count', 2)
    for i in range(player_count):
        players[i] = {
            'position': 0,
            'attribute': random.choice(ATTRIBUTES),
            'items': []
        }
    return jsonify({"status": "Game started", "players": players, "zones": zones, "items": items})

@app.route('/roll_dice', methods=['POST'])
def roll_and_move():
    player_id = request.json['player_id']
    roll = roll_dice()
    player = players[player_id]
    current_position = player['position']
    possible_moves = get_adjacent_tiles(current_position)

    return jsonify({
        "roll": roll,
        "possible_moves": possible_moves,
        "current_position": current_position
    })

@app.route('/move_piece', methods=['POST'])
def move_piece():
    player_id = request.json['player_id']
    new_position = request.json['new_position']
    player = players[player_id]
    player_attr = player['attribute']
    
    # Win condition
    if new_position == FINAL_TILE:
        if player['items']:
            return jsonify({"status": "Player wins!", "player_id": player_id})
        else:
            player['position'] = 0
            player['items'] = []
            return jsonify({"status": "No items! Sent back to start", "position": 0})

    # Check if new position has a zone attribute and apply rules
    if new_position in zones:
        zone_attr = zones[new_position]
        if zone_attr == player_attr:
            player['position'] = new_position  # Safe move
        elif (player_attr, zone_attr) in [('red', 'green'), ('green', 'blue'), ('blue', 'red')]:
            player['position'] = new_position
            del zones[new_position]  # Neutralize the zone
        else:
            player['position'] = 0
            player['items'] = []
            return jsonify({"status": "Sent back to start by zone", "position": 0})
    else:
        player['position'] = new_position

    # Check if player landed on an item
    if new_position in items:
        player['items'].append(new_position)
        items.remove(new_position)
        new_item_pos = random.choice([i for i in range(NUM_TILES) if i not in items])
        items.append(new_item_pos)

    return jsonify({"status": "Moved", "position": new_position, "items": player['items']})

@app.route('/save_game', methods=['POST'])
def save_game():
    save_data = {"players": players, "zones": zones, "items": items}
    with open("game_save.json", "w") as f:
        json.dump(save_data, f)
    return jsonify({"status": "Game saved"})

@app.route('/load_game', methods=['POST'])
def load_game():
    global players, zones, items
    try:
        with open("game_save.json", "r") as f:
            save_data = json.load(f)
            players = save_data["players"]
            zones = save_data["zones"]
            items = save_data["items"]
        return jsonify({"status": "Game loaded", "players": players, "zones": zones, "items": items})
    except FileNotFoundError:
        return jsonify({"status": "No saved game found"})
    
@app.route('/add_tile')
def add_tile():
    global current_player
    color = 'purple' if current_player == 1 else 'brown'  # Alternate between purple and brown
    current_player = 2 if current_player == 1 else 1  # Switch to the other player
    return jsonify(color=color)

if __name__ == "__main__":
    app.run(debug=True)
