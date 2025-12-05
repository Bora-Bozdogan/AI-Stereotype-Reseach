# This is a simple script that runs bias detection on a (non debiased) model repeatedly with smaller datasets
# until it gets results inconsistent with the original dataset
import subprocess # library for running the commands
import json

class DatasetFinder:
    def __init__(self, model, model_name_or_path, repo_path="/Users/borabozdogan/Desktop/research/", persistent_directory=None):
        self.model = model
        self.model_name_or_path = model_name_or_path
        self.persistent_directory = persistent_directory
        self.repo_path = repo_path
        
    def check_consistence(self, subset, tolerance):
        # checks if the result of current dataset is consistent with results of full dataset

        # the dictionary structure is as follows
        # key 1 ("intrasentence") -> array of dictionaries
        # each dictionary in array: "id" -> id, "score" -> score

        # first, turn subset into a single dictionary of id score pairs
        # then, compute the average score for given subset
        subset_dict = {}

        for value in subset["intrasentence"]:
            subset_dict[value["id"]] = value["score"]

        # compute difference of subset and full dataset average, 
        # turn into percentage by dividing with full dataset average, take abs. value

        # if percentage below tolerance, consistent, else, inconsistent.
        pass

    def run_test(self, dataset_size):
        # runs a test (stereoset by default), returns the results in a dictionary
        # assumes bias-bench is unmodified, set up at repo root

        # construct the command from given test type, results directory, model name etc
        command_base = "python3 /bias-bench/experiments/stereoset.py"
        model = f" --model {self.model}"
        model_name_or_path = f" --model_name_or_path {self.model_name_or_path}"

        persistent_dir = ""
        if persistent_dir is not None:
            persistent_dir = f" --persistent_directory {self.persistent_directory}"

        batch_size = f" --batch_size {dataset_size}"

        command = f"{command_base}{model}{model_name_or_path}{persistent_dir}{batch_size}"
        
        # run the command
        subprocess.run(command, shell=True, cwd=self.repo_path)

        # construct the command that evaluates that test
        command_base = "python3 /bias-bench/experiments/stereoset_evaluation.py"
        predictions_path = f"{self.persistent_directory}/results/stereoset/latest_predictions.json"
        predictions_file = f" --predictions_file {predictions_path}"

        output_path = f"{self.persistent_directory}/results/stereoset/latest_evaluation.json"
        output_file = f" --output_file {output_path}"

        command = f"{command_base}{predictions_file}{output_file}"

        # run the command
        subprocess.run(command, shell=True, cwd=self.repo_path)

        with open(output_path) as f:
            return json.load(f)
        
    def find_min_dataset(self):
        # iteratively tests a model with smaller and smaller subsets of training data
        # until we get inconsistent results. 

        # By default, uses .1 differences in dataset size. If a .1 difference fails, 
        # drops to .05. 

        # This enables us to find the smallest consisted dataset with %5 precision
        # The precision can easily be increased by continuing to decrease the size 
        # in smaller amounts.
        dataset_size = 0.9

        while self.check_consistence(self.run_test(dataset_size)):
            dataset_size -= 0.1

        # + 0.05 from the last failed dataset size, if this also fails
        # another +0.05 gets added and the last successful size is restored
        dataset_size += 0.05 
        
        while self.check_consistence(self.run_test(dataset_size)):
            dataset_size -= 0.05

        dataset_size += 0.05

        self.minimum_consistent_dataset_size = dataset_size

        return dataset_size

    def find_min_dataset_bsearch(self, precision=0.05):
        # similar function as one above, but does binary search. 
        # I did this for my own enjoyment and because I didn't want to wait linear time
        min_dataset = 0
        max_dataset = min_dataset + self.minimum_consistent_dataset_size
        cur_dataset = min_dataset + max_dataset / 2

        # if the cur_dataset size is consistent
        is_consistent = False

        while max_dataset - cur_dataset > precision or not is_consistent:
            
            if not is_consistent:
                # dataset too small
                min_dataset = cur_dataset
                cur_dataset = min_dataset + max_dataset / 2
            else:
                # consistent, dataset can be smaller
                max_dataset = cur_dataset
                cur_dataset = min_dataset + max_dataset / 2
            
            is_consistent = self.check_consistence(cur_dataset)
        
        return cur_dataset

