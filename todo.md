# TODO – AoC Multi-Agent Coding Thesis

## Core System Setup
- [x] Get a fully workable end-to-end system (minimal pipeline runs without crashing)

---

## Dataset Preparation
- [x] Receive / collect dataset for fine-tuning
- [x] Convert dataset to correct format (JSONL)
- [x] Validate dataset structure (input/output pairs)
- [ ] Clean dataset (remove invalid / broken samples / inefficient solutions)

---

## Fine-tuning
- [x] Configure fine-tuning method (LoRA)
- [x] Implement training script
- [x] Ensure training runs on Hábrók without OOM
- [ ] Save model + tokenizer correctly
- [ ] Validate saved checkpoints
- [ ] Evaluate fine-tuned model on small test set
- [ ] Compare fine-tuned vs base model

---

## AoC Evaluation
- [x] Test run the whole pipeline on AoC dataset
- [x] Debug failures in pipeline stages
- [x] Measure pass rate under time constraints
- [x] Log token usage and runtime
- [ ] Analyze common failure cases

---

## Model Comparison Experiments
- [ ] Run full pipeline with:
  - [x] GPT4.1-mini
  - [ ] GPT5.4-nano
  - [ ] Qwen3.5
  - [ ] Fine-tuned Qwen3.5
- [ ] Compare performance across models

---

## Additional Benchmarks
- [ ] Run experiments on HumanEval dataset
- [ ] Run experiments on APPS dataset
- [ ] Compare results with AoC performance

---

## Ablation Study
- [ ] Remove previewing agent
- [ ] Remove planning stage
- [ ] Remove debugging agent
- [ ] Remove previewing and planning agents
- [ ] Remove previewing and debugging agents
- [ ] Remove planning and debugging agents
- [ ] Compare ablation pipelines
- [ ] Analyze contribution

---

## Analysis & Metrics
- [ ] Compute pass@1
- [ ] Measure runtime per task
- [ ] Measure token usage
- [ ] Identify failure categories:
  - [ ] incorrect logic
  - [ ] inefficient algorithm
  - [ ] runtime errors

---

## Thesis Writing

### Introduction
- [ ] Problem statement
- [ ] Motivation (efficiency vs correctness)
- [ ] Research questions

### Background
- [ ] LLMs for code generation
- [ ] Multi-agent systems
- [ ] Algorithmic efficiency & Big-O

### Related Work
- [ ] Single-agent prompting
- [ ] Multi-agent frameworks (e.g., MapCoder)
- [ ] Efficiency benchmarks (BigO(Bench))

### Methodology
- [ ] System architecture (pipeline design)
- [ ] Dataset description
- [ ] Experimental setup
- [ ] Evaluation metrics

### Implementation
- [ ] HPC / Hábrók setup
- [ ] Engineering challenges
- [ ] Dependency issues & solutions
- [ ] Design decisions

### Experiments
- [ ] AoC results
- [ ] Model comparison
- [ ] Ablation study

### Results & Analysis
- [ ] Performance comparison
- [ ] Efficiency insights
- [ ] Failure analysis

### Discussion
- [ ] Interpretation of results
- [ ] Limitations
- [ ] Practical implications

### Conclusion
- [ ] Summary of findings
- [ ] Answer to research question
- [ ] Future work

---

## Final Steps
- [ ] Clean and organize codebase
- [ ] Ensure reproducibility
- [ ] Have thesis peer reviewed