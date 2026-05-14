#!/bin/bash
#SBATCH --job-name=finetune_qwen
#SBATCH --output=tune/%x_%j.out
#SBATCH --error=tune/%x_%j.err
#SBATCH --gres=gpu:rtx_pro_6000:4
#SBATCH --time=12:00:00
#SBATCH --mem=32G

#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=j.kleine.4@student.rug.nl

echo "Starting job on $(hostname)"
echo "Time: $(date)"

# Load modules
module load Python/3.11
module load CUDA/12.6.0

# Activate environment
source /scratch/$USER/tune_env/bin/activate

# Load environment variables
source /home6/$USER/Thesis/env.sh

# Move to project directory
cd /home6/$USER/Thesis

# Run your script
python finetune.py

echo "Finished at $(date)"
