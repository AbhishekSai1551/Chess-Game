from flask import Flask, render_template, request, jsonify
import chess
import chess.engine
import os
import sys

app = Flask(__name__)

#INitial configuration
GAME_CONFIG = {
    'mode': None,
    'opponent': None, # Default set to stockfish, changes to player when selecting opponent 
    'elo': None,
    'model_path': None
}

STOCKFISH_PATH = "./engines/stockfish"
LC0_PATH = "./engines/lc0"

ELO_MAP = {
    '1': ('easy', 1350),
    '2': ('medium', 1700),
    '3': ('hard', 2100),
    '4': ('expert', None)
}

TOP_PLAYERS = {
    '1': 'Carlsen',
    '2': 'Nakamura',
    '3': 'Caruana',
    '4': 'Keymer',
    '5': 'Erigaisi',
    '6': 'Giri',
    '7': 'Firouzja',
    '8': 'Praggnanandhaa',
    '9': 'Gukesh',
    '10': 'Wei'
}

def get_engine_move(fen):
    """Decides which engine to query based on GAME_CONFIG."""
    board_state = chess.Board(fen)
    
    #Expert mode
    if GAME_CONFIG['mode'] == 'expert':
        if not os.path.exists(LC0_PATH):
            return None, f"Lc0 engine not found at {LC0_PATH}"
        
        # Check for specific player weights
        weights = GAME_CONFIG['model_path']
        if not os.path.exists(weights):
             return None, f"Model weights not found: {weights}"
        try:
            with chess.engine.SimpleEngine.popen_uci(LC0_PATH) as engine:
                engine.configure({"WeightsFile": weights})
                result = engine.play(board_state, chess.engine.Limit(nodes=800)) # Quick move
                return result.move.uci(), None
        except Exception as e:
            return None, str(e)
    #Stockfish
    else:
        if not os.path.exists(STOCKFISH_PATH):
            return None, f"Stockfish engine not found at {STOCKFISH_PATH}"
            
        try:
            with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
                # Configure Elo for difficulty
                engine.configure({"UCI_LimitStrength": True, "UCI_Elo": GAME_CONFIG['elo']})
                result = engine.play(board_state, chess.engine.Limit(time=0.5))
                return result.move.uci(), None
        except Exception as e:
            return None, str(e)

@app.route('/')
def index():
    return render_template('index.html', 
                           mode=GAME_CONFIG['mode'].upper(), 
                           opponent=GAME_CONFIG['opponent'])

@app.route('/move', methods=['POST'])
def move():
    data = request.json
    fen = data.get('fen')
    current_board = chess.Board(fen)
    
    if current_board.is_game_over():
        return jsonify({'game_over': True, 'result': current_board.result()})

    ai_move, error = get_engine_move(fen)
    
    if error:
        print(f"Engine Error: {error}")
        return jsonify({'error': error}), 500
        
    return jsonify({
        'ai_move': ai_move,
        'game_over': False
    })

def terminal_setup():
    print("\n" + "="*40)
    print(" CHESS SYSTEM SETUP")
    print("="*40)
    print("Select Difficulty Mode:")
    print("1. Easy")
    print("2. Medium")
    print("3. Hard")
    print("4. Expert")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice not in ELO_MAP:
        print("Invalid choice. Defaulting to Easy.")
        choice = '1'
        
    mode_name, elo = ELO_MAP[choice]
    GAME_CONFIG['mode'] = mode_name
    GAME_CONFIG['elo'] = elo
    
    if mode_name == 'expert':
        print("\nSelect Player to Mimic:")
        for k, v in TOP_PLAYERS.items():
            print(f"{k}. {v}")
            
        p_choice = input("\nEnter player number (1-10): ").strip()
        if p_choice not in TOP_PLAYERS:
            p_choice = '1'
            
        player_name = TOP_PLAYERS[p_choice]
        GAME_CONFIG['opponent'] = player_name
        GAME_CONFIG['model_path'] = os.path.abspath(f"models/{player_name}_expert.pb.gz")
        print(f"\n[SETUP] Mode: Expert | Opponent: {player_name}")
        print(f"[SETUP] Loading weights from: {GAME_CONFIG['model_path']}")
    else:
        GAME_CONFIG['opponent'] = "Stockfish"
        print(f"\n[SETUP] Mode: {mode_name.upper()} | Engine: Stockfish (Elo {elo})")

    print("\nStarting Web Server...")
    print("Open your browser at: http://127.0.0.1:5000")
    print("="*40 + "\n")

if __name__ == '__main__':
    terminal_setup()
    app.run(debug=True, use_reloader=False, port=5000)
