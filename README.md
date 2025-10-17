### BEFORE YOU USE ###

+ Switch to the proper python version with the command (any other python 3.9 works, but newer models like 3.14)

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
     
    `python3 ./bias-bench/experiments/stereoset_evaluation.py --predictions_file ./bias-bench/results/stereoset/stereoset_m-BertForMaskedLM_c-bert-base-uncased.json --predictions_dir ./bias-bench/results/stereoset --output_file ./stereoset_benchmarks/bert_uncased_results.json`

    Although I had an error saving the results in a JSON file because I was doing the testing, evaluation processes seperately and not as part of a
    pipeline, I were able to get results consistent with other published papers. Results were as below.

    intrasentence
        gender
                Count: 2313.0
                LM Score: 85.73970402503635
                SS Score: 60.278684896276104
                ICAT Score: 68.11387600956986
        profession
                Count: 7194.0
                LM Score: 83.85202686230224
                SS Score: 58.93389453546499
                ICAT Score: 68.86952357084654
        race
                Count: 8928.0
                LM Score: 84.00827460718995
                SS Score: 57.02967880452161
                ICAT Score: 72.19725085897807
        religion
                Count: 741.0
                LM Score: 84.21150995925436
                SS Score: 59.70419362150916
                ICAT Score: 67.86741400316933
        overall
                Count: 6392.0
                LM Score: 84.17236429175225
                SS Score: 58.24009298588702
                ICAT Score: 70.30060211963236

+ Next step is to turn this into a pipeline where we can tinker with the batch size.