#!/bin/bash
#SBATCH --job-name=gpt_test
#SBATCH --output=test/test.out
#SBATCH --error=test/test.err
#SBATCH --time=1:30:00
#SBATCH --mem=16G

#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=j.kleine.4@student.rug.nl

echo "Starting job on $(hostname)"
echo "Time: $(date)"

# Load modules
module load Python/3.11

# Activate environment
source /scratch/$USER/qwen_env/bin/activate

# Move to project directory
cd /home6/$USER/Thesis

# Run your script
python src/main.py \
  --model "GPT4" \
  --end 1 \
  --local \
  --temperature 0.3

echo "Finished at $(date)"
