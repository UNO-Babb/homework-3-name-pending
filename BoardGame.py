#Example Flask App for a hexaganal tile game
#Logic is in this python file

# Write a flask app board game that use hexagon tiles instead of square tiles which allow pieces on the board to move in any direction. The board game will have 3 unique attributes that are dangerous for certain pieces. These attributes should be applied to groups of tiles called zones. The pieces will also have these attributes, which if a piece and a zone that piece is going to travel to are the same, that piece will be safe. If a piece and a zone have opposite attributes they are two outcomes. If the piece contains an attribute that is strong against the zone's attribute. That zone is neutralized and acts as any normal tile. If it is the other way around, the piece is sent back to the beginning. These three attributes can be color coded red, blue and green. This game will also have a dice rolling mechanic. For example, if a dice rolls 3, a piece is moved by 3 tiles in any direction the player wants. Along the board game, there should be spots where if a piece lands on that tile, it creates a zone of that pieces attribute. To beat the game, a piece must reach the final tile. This tile can be colored yellow. However, there is another requirement. Pieces must collect an item. There will be 3 of these items placed on random tiles. There are no restrictions on how many items a piece can get. If a piece is sent back to the beginning, that piece will lose those items, and those items are place in new spots. If a piece reaches the final tile and does not have an item, they are sent back to the beginning.

from flask import Flask, jsonify, request, render_template
import random

app = Flask(__name__)
@app.route("/")
def index():
    return render_template('index.html')

# Initialize board with hexagonal tiles and zones
NUM_TILES = 50  # adjust as needed for board size
FINAL_TILE = NUM_TILES - 1  # The final tile where players must reach with an item

# Define the attributes as colors
ATTRIBUTES = ['red', 'blue', 'green']
# Zones and pieces will have an attribute
zones = {}  # Stores tile and its attribute
pieces = {}  # Stores each piece’s position, attribute, and collected items

# Place items randomly on the board
items = random.sample(range(NUM_TILES), 3)

# Initialize zones with random attributes
for i in range(NUM_TILES):
    if random.random() < 0.2:  # 20% of tiles are special zones
        zones[i] = random.choice(ATTRIBUTES)

# Helper functions
def roll_dice():
    return random.randint(1, 6)

def get_adjacent_tiles(position):
    """Returns the list of hexagon-adjacent tiles."""
    # Assuming some adjacency logic for hex tiles, we'll simulate here.
    return [max(0, position - 1), min(NUM_TILES - 1, position + 1)]

@app.route('/start_game', methods=['POST'])
def start_game():
    player_count = request.json.get('player_count', 2)
    # Initialize players on the starting tile with attributes and empty items
    for i in range(player_count):
        pieces[i] = {
            'position': 0,
            'attribute': random.choice(ATTRIBUTES),
            'items': []
        }
    return jsonify({"status": "Game started", "pieces": pieces, "zones": zones, "items": items})

@app.route('/roll_dice', methods=['POST'])
def roll_and_move():
    player_id = request.json['player_id']
    roll = roll_dice()
    piece = pieces[player_id]
    current_position = piece['position']

    # Get possible moves (adjacent tiles based on roll)
    # Here we simplify to linear movement for illustration
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

    piece = pieces[player_id]
    piece_attr = piece['attribute']
    current_position = piece['position']

    # Check if moving to final tile and check win condition
    if new_position == FINAL_TILE:
        if piece['items']:
            return jsonify({"status": "Player wins!", "player_id": player_id})
        else:
            # Send back to start if no items
            piece['position'] = 0
            piece['items'] = []  # Drop items
            return jsonify({"status": "No items! Sent back to start", "position": 0})

    # Check if the new tile is a zone and apply rules
    if new_position in zones:
        zone_attr = zones[new_position]
        if zone_attr == piece_attr:
            # Safe zone
            piece['position'] = new_position
        elif (piece_attr, zone_attr) in [('red', 'green'), ('green', 'blue'), ('blue', 'red')]:
            # Piece is strong against zone
            piece['position'] = new_position
            del zones[new_position]  # Neutralize zone
        else:
            # Zone is strong, send piece back to start
            piece['position'] = 0
            piece['items'] = []  # Drop items
            return jsonify({"status": "Sent back to start by zone", "position": 0})

    else:
        # Move normally if no zone
        piece['position'] = new_position

    # Check if piece landed on an item
    if new_position in items:
        piece['items'].append(new_position)
        items.remove(new_position)
        # Reassign the item to a random new tile
        new_item_pos = random.choice([i for i in range(NUM_TILES) if i not in items])
        items.append(new_item_pos)

    return jsonify({"status": "Moved", "position": new_position, "items": piece['items']})

if __name__ == '__main__':
    app.run(debug=True)
