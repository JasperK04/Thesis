#!/bin/bash
#SBATCH --job-name=ablation_eval
#SBATCH --cpus-per-task=6
#SBATCH --time=8:00:00
#SBATCH --mem=8G
#SBATCH --array=0-17%1

module load Python/3.11

source /scratch/$USER/qwen_env/bin/activate

cd /home6/$USER/Thesis

BATCH_SIZE=10
SKIP_SIZE=20

START=$(( SLURM_ARRAY_TASK_ID * (BATCH_SIZE + SKIP_SIZE) ))
END=$(( START + BATCH_SIZE ))

strategies=("r" "rp" "rd" "p" "pd" "d")

echo "Running $START -> $END"

for strat in "${strategies[@]}"; do
    python src/main.py \
        --model "GPT5" \
        --strategy "$strat" \
        --start "$START" \
        --end "$END" \
        --local \
        > logs/ablation_${strat}_${START}_${END}.out 2>&1 &
done

wait

echo "Finished at $(date)"