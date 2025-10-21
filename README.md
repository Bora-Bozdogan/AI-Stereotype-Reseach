### BEFORE YOU USE ###

+ Switch to the proper python version with the command (any other python 3.9 works, but not newer models like 3.14)

    `pyenv global 3.9.20`

    pyenv must be set up for this step, so please follow the github page for instructions
    
    https://github.com/pyenv/pyenv?tab=readme-ov-file#installation

+ Create a virtual environment under venv, and activate it with the command below (you must be on root, 'research', not in `bias-bench`)

    `source venv/bin/activate`

### Other notes ###

+ Required data for BiasBench is located in `/bias-bench/data/text`
    Change that to root directory `./data/text` if BiasBench fails to function.

+ bias-bench folder and venv files are not committed, please set up bias-bench at root directory by following the link below

    `https://github.com/McGill-NLP/bias-bench?tab=readme-ov-file`

### Bias-Bench notes ###

+ I, so far, ran the default `stereoset.py` with regular arguments, which does intrasentence evaluation on `bert_base_uncased` model. 
    Then, I evaluated the resulting json file with the command below:
     
    `python3 ./bias-bench/experiments/stereoset_evaluation.py --predictions_file ./bias-bench/results/stereoset/stereoset_m-BertForMaskedLM_c-bert-base-uncased.json --predictions_dir ./bias-bench/results/stereoset --output_file ./bias-bench/results/stereoset/bert_uncased_results.json`

+ Next step is to turn this into a pipeline where we can tinker with the batch size.