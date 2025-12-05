# STEREOSET DEBIASED commands used

## Debias subspaces

### BertModel

`python3 ./bias-bench/experiments/stereoset_debias.py --model "SentenceDebiasBertForMaskedLM" --bias_direction PUT_HERE --bias_type "gender"`

# Bias Direction 

In `/debias_computations/compute_bias_direction.py`, run it to create bias direction for relevant matrices.

# INLP 



# STEREOSET BASE commands used

## evaluation of all json files

`python3 ./bias-bench/experiments/stereoset_evaluation.py --predictions_dir ./bias-bench/results/stereoset --output_file ./bias-bench/results/stereoset/results-base.json`

+ evaluates all files in results/stereoset and saves it under `results-base.json`

## bert_base_uncased

`python3 ./bias-bench/experiments/stereoset_evaluation.py --predictions_file ./bias-bench/results/stereoset/stereoset_m-BertForMaskedLM_c-bert-base-uncased.json --predictions_dir ./bias-bench/results/stereoset --output_file ./bias-bench/results/stereoset/bert_uncased_results.json`

+ this analyzes the predictions file and saves it in the output file for `bert_base_uncased`

## albert_base_v2

`python3 ./bias-bench/experiments/stereoset.py --model "AlbertForMaskedLM" --model_name_or_path "albert-base-v2"`

+ runs the test on `albert-base-v2`

`python3 ./bias-bench/experiments/stereoset_evaluation.py --predictions_file ./bias-bench/results/stereoset/stereoset_m-AlbertForMaskedLM_c-albert-base-v2.json --predictions_dir ./bias-bench/results/stereoset --output_file ./bias-bench/results/stereoset/albert_base_v2_results.json`

+ runs the evaluation on `albert-base-v2`


## roberta_base

`python3 ./bias-bench/experiments/stereoset.py --model "RobertaForMaskedLM" --model_name_or_path "roberta-base"`

+ runs the test on `roberta-base`

## GPT-2

`python3 ./bias-bench/experiments/stereoset.py --model "GPT2LMHeadModel" --model_name_or_path "gpt2"`

+ runs the test on `gpt2`
