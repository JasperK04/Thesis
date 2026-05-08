## Issues encountered

- **GPU memory limitations**
  - Single GPU (e.g., ~40GB) insufficient for large models → OOM errors

- **Job scheduling constraints**
  - Jobs must be submitted via scheduler 
  - Because at least 2 GPU's are required im queued quite long 

- **Environment inconsistency**
  - Cluster uses shared Linux environment -> version mismatches between nodes  
  - Limited control over system libraries (e.g., GLIBC issues) 
  This issue is about using `fast linear attention` and `causal conv1d` which kept breaking because incompatible GLIBC versions  

- **CUDA / PyTorch compatibility**
  - Matching CUDA version, drivers, and PyTorch builds is fragile  
  - Precompiled wheels often incompatible with cluster setup  

- **Memory inefficiency**
  - Fine-tuning large the model requires crazy amounts of VRAM (at least 4 GPU's - 4x40GB)   

- **Prompt / pipeline design complexity**
  - Getting the pipeline to actually produce any output was more difficult than expected
  - The local models produce output that includes the input, causing prompt accumulation over the pipeline causing the model to get confuzed (bug that I found after way to long)
  - Qwen is inconsistent with using `<think>...</think>`, sometimes the opening tag is there and sometimes its not. according to the devs this is normal.

- **Parsing issues XML**
  - I went to many iterations of XML parsing because it kept crashing on malformed XML
  - Same issue with the `<think>` tags

- **Slow iteration cycles**
  - Each experiment requires job submission + waiting  
  - Debugging becomes expensive in time   

- **MAPcoder**
  - Learning the structure of the system dessigned by Islam et al was difficult
  - There are a lot of minor things i had to change
    - Some personal code style preferences
    - Others like code execution had to be redone because i dont have a server for that so it has to be done locally (subprocess)

- **Finetuning**
  - Takes much more memory then expected, where using the model works with about 60gb, fine tuning takes more then dubbel that.

- **Time constraints**
  - First succesfull experiment took 56 minutes to finish for a single problem. therefore i will be downgrading to Qwen3.5-9B instead of Qwen3.6-27B