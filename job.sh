#!/bin/bash
#SBATCH --job-name=qwen_test
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err
#SBATCH --gres=gpu:1
#SBATCH --time=02:00:00
#SBATCH --mem=16G

echo "Starting job on $(hostname)"
echo "Time: $(date)"

# Load modules
module load Python/3.11
module load CUDA/12.1

# Activate environment
source /scratch/$USER/qwen_env/bin/activate

# Load environment variables
source /home6/$USER/Thesis/env.sh

# Move to project directory
cd /home6/$USER/Thesis

# Run your script
python test_qwen.py

echo "Finished at $(date)"
