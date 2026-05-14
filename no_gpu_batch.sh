#!/bin/bash
#SBATCH --job-name=gpt_batch_eval
#SBATCH --output=logs/%a/gpt_eval.out
#SBATCH --error=logs/%a/gpt_eval.err
#SBATCH --time=3:00:00
#SBATCH --mem=16G

#SBATCH --array=0-49%10

#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=j.kleine.4@student.rug.nl

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
    --model "GPT4" \
    --start $START \
    --end $END \
    --local

echo "Finished at $(date)"
