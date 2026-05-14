#!/bin/bash
#SBATCH --job-name=qwen_ft_batch_eval
#SBATCH --output=logs/%a/qwen_ft_eval.out
#SBATCH --error=logs/%a/qwen_ft_eval.err
#SBATCH --gres=gpu:2
#SBATCH --time=12:00:00
#SBATCH --mem=32G

#SBATCH --array=0-49%8

# Load modules
module load Python/3.11
module load CUDA/12.1

# Activate environment
source /scratch/$USER/qwen_env/bin/activate

# Load environment variables
source /home6/$USER/Thesis/env.sh

# Move to project directory
cd /home6/$USER/Thesis


# Batch Assignemt
TOTAL=500
JOBS=50

CHUNK=$(( (TOTAL + JOBS - 1) / JOBS ))

START=$(( SLURM_ARRAY_TASK_ID * CHUNK ))
END=$(( START + CHUNK ))

if [ "$END" -gt "$TOTAL" ]; then
    END=$TOTAL
fi

echo "Running items $START to $END"

python src/main.py \
    --model "qwenft" \
    --start $START \
    --end $END \
    --temperature 0.3 \
    --local

echo "Finished at $(date)"
