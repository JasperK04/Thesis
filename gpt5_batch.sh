#!/bin/bash
#SBATCH --job-name=gpt5_batch_eval
#SBATCH --output=logs/%a/gpt5_eval.out
#SBATCH --error=logs/%a/gpt5_eval.err
#SBATCH --time=1:15:00
#SBATCH --mem=4G

#SBATCH --array=0-49%10

# Load modules
module load Python/3.11

# Activate environment
source /scratch/$USER/qwen_env/bin/activate

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
    --model "GPT5" \
    --start $START \
    --end $END \
    --local

echo "Finished at $(date)"
