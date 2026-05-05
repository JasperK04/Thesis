# TODO – AoC Multi-Agent Coding Thesis

## Core System Setup
- [ ] Get a fully workable end-to-end system (minimal pipeline runs without crashing)

---

## Dataset Preparation
- [ ] Receive / collect dataset for fine-tuning
- [ ] Convert dataset to correct format (JSONL)
- [ ] Validate dataset structure (input/output pairs)
- [ ] Clean dataset (remove invalid / broken samples / inefficient solutions)

---

## Fine-tuning
- [ ] Configure fine-tuning method (LoRA)
- [ ] Implement training script
- [ ] Ensure training runs on Hábrók without OOM
- [ ] Save model + tokenizer correctly
- [ ] Validate saved checkpoints
- [ ] Evaluate fine-tuned model on small test set
- [ ] Compare fine-tuned vs base model

---

## Pipeline Implementation

---

## AoC Evaluation
- [ ] Prepare AoC dataset subset
- [ ] Test run the whole pipeline on AoC dataset
- [ ] Debug failures in pipeline stages
- [ ] Measure pass rate under time constraints
- [ ] Log token usage and runtime
- [ ] Analyze common failure cases

---

## Model Comparison Experiments
- [ ] Run full pipeline with:
  - [ ] ChatGPT model
  - [ ] Qwen3.6
  - [ ] Qwen3-coder
  - [ ] Fine-tuned Qwen3.6
  - [ ] (Optional) Gemini model
- [ ] Compare performance across models
- [ ] Compare efficiency (timeouts vs passes)
- [ ] Compare token cost / runtime

---

## Additional Benchmarks
- [ ] Run experiments on HumanEval dataset
- [ ] Run experiments on APPS dataset
- [ ] Compare results with AoC performance

---

## Ablation Study
- [ ] Remove previewing agent → evaluate impact
- [ ] Remove planning stage → evaluate impact
- [ ] Remove debugging agent → evaluate impact
- [ ] Compare single-agent vs multi-agent pipeline
- [ ] Analyze contribution

---

## Analysis & Metrics
- [ ] Compute pass@1
- [ ] Track TIMEOUT rate
- [ ] Measure runtime per task
- [ ] Measure token usage
- [ ] Analyze complexity patterns (naive vs optimized solutions)
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
- [ ] Additional benchmarks (HumanEval, APPS)
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