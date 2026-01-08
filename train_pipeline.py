import os
import subprocess
import glob

# CONFIGURATION
PLAYERS=["Carlsen","Nakamura","Firouzja","Caruana","Erigaisi","Gukesh","Keymar","Giri","Praggnanandhaa","Wei"] # Add all 10 names (must match filenames in data/raw_pgns/)
BASE_MODEL="tools/maia-chess/models/maia-1900.pb.gz"
EPOCHS=5

def run_command(cmd):
    print(f"[EXEC] {cmd}")
    subprocess.check_call(cmd, shell=True)

#Processing pgns to train
def process_pgns():
    for player in PLAYERS:
        print(f"\n--- Processing {player} ---")
        input_pgn = f"expert_config/data//{player}.pgn"
        output_dir = f"data/training_chunks/{player}"
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        #Clean PGN
        clean_pgn = f"data/raw_pgns/{player}_clean.pgn"
        #No duplicate outputs
        run_command(f"pgn-extract -D -C -N -Worg {input_pgn} > {clean_pgn}")
        # 2. Convert to Training Chunks(moves to tensors)
        run_command(f"./trainingdata-tool --supervised --files-per-dir 100 --output {output_dir} {clean_pgn}")

#Fine-tuning for each player
def train_models():
    for player in PLAYERS:
        print(f"\n--- Training Model for {player} ---")
        training_data_path = f"data/training_chunks/{player}"
        output_weights = f"models/{player}_expert.pb.gz"
        cmd = (
            f"python3 tools/maia-chess/move_prediction/train.py "
            f"--data_dir {training_data_path} "
            f"--base_model {BASE_MODEL} "
            f"--epochs {EPOCHS} "
            f"--output {output_weights}"
        )
        run_command(cmd)

if __name__ == "__main__":
    os.makedirs("data/training_chunks", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    process_pgns()
    train_models()
