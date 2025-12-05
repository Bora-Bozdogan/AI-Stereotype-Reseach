# This is a simple script that runs bias detection on a (non debiased) model repeatedly with smaller datasets
# until it gets results inconsistent with the original dataset
import subprocess # library for running the commands
import json
import os

class DatasetFinder:
    def __init__(self, model, model_name_or_path, persistent_directory=None, repo_path="/Users/borabozdogan/Desktop/research/"):
        self.model = model
        self.model_name_or_path = model_name_or_path
        self.persistent_directory = persistent_directory
        self.repo_path = repo_path
        self.dataset_scores = self.run_test()
        
    def check_consistence(self, subset, tolerance):
        # checks the subset scores against the dataset_scores given
        # returns true if difference below tolerance (percentage), false else
        # compares ICAT scores because that's the main metric, can be modified

        # the dictionaries have the following structure:
        # (pasted here for my own convenience)
        # intrasentence: 
        #   profession:
        #       "Count"
        #       "LM Score"
        #       "SS Score"
        #       "ICAT Score"
        #   race
        #       "Count"
        #       "LM Score"
        #       "SS Score"
        #       "ICAT Score"
        #   religion
        #       "Count"
        #       "LM Score"
        #       "SS Score"
        #       "ICAT Score"
        # overall:
        #       "Count"
        #       "LM Score"
        #       "SS Score"
        #       "ICAT Score"

        # we must compare the ICAT scores of each task, and the overall score
        # if any below tolerance, fail
        
        # get icat scores (0: profession, 1: race, 2: religion, 3: overall)
        dataset_intrasentence = self.dataset_scores["intrasentence"]

        dataset_values = []

        dataset_values.append(dataset_intrasentence["profession"]["ICAT Score"])
        dataset_values.append(dataset_intrasentence["race"]["ICAT Score"])
        dataset_values.append(dataset_intrasentence["religion"]["ICAT Score"])
        dataset_values.append(self.dataset_scores["overall"]["ICAT Score"])
        
        subset_intrasentence = subset["intrasentence"]

        subset_values = []

        subset_values.append(subset_intrasentence["profession"]["ICAT Score"])
        subset_values.append(subset_intrasentence["race"]["ICAT Score"])
        subset_values.append(subset_intrasentence["religion"]["ICAT Score"])
        subset_values.append(subset["overall"]["ICAT Score"])
        
        # absolute percentage difference function to make it easier
        def abs_percent_diff(val, ref):
            return abs(val - ref) / abs(ref)
        
        for base, sub in zip(dataset_values, subset_values):
            if abs_percent_diff(base, sub) > tolerance:
                return False
        
        return True

    def run_test(self, dataset_size=1, clean_files=True):
        # runs a test (stereoset by default), returns the results in a dictionary

        # creates directories
        predictions_dir = f"{self.repo_path}bias-bench/results/prediction_files"
        evaluations_dir = f"{self.repo_path}bias-bench/results/evaluation_files"

        os.makedirs(predictions_dir, exist_ok=True)
        os.makedirs(evaluations_dir, exist_ok=True)

        # compute command
        command_base = "python3 bias-bench/experiments/stereoset.py"
        model = f" --model {self.model}"
        model_name_or_path = f" --model_name_or_path {self.model_name_or_path}"

        persistent_dir_arg = ""
        if self.persistent_directory is not None:
            persistent_dir_arg = f" --persistent_dir {self.persistent_directory}"

        command = f"{command_base}{model}{model_name_or_path}{persistent_dir_arg}"
        # subprocess waits until the command is finished
        subprocess.run(command, shell=True, cwd=self.repo_path)

        # we ran the command, now we must find the predictions file
        # by default, bias-bench saves it under /results/stereoset
        # we scan this to find the most recent created json file
        results_stereoset_dir = f"{self.repo_path}/bias-bench/results/stereoset"

        # sort files by creation time
        all_files = sorted(
            os.listdir(results_stereoset_dir),
            key=lambda f: os.path.getmtime(os.path.join(results_stereoset_dir, f)),
        )

        # get the most recent .json file. This code is meant to run as the only process 
        # that modifies the repo, so when it scans, the latest prediction file is guaranteed
        # to be the newest file. If we run multiple instances of this code on the same repo,
        # a special naming system would be needed.
        prediction_file = None
        for fname in reversed(all_files):
            if fname.endswith(".json"):
                # get the full path to the latest json file
                prediction_file = os.path.join(results_stereoset_dir, fname)
                break

        if prediction_file is None:
            raise RuntimeError("Could not locate prediction file created by stereoset.py")

        # Move the prediction file into prediction_files/
        pred_filename = os.path.basename(prediction_file)
        new_prediction_path = os.path.join(predictions_dir, pred_filename)
        os.replace(prediction_file, new_prediction_path)

        # we have the predictions file, we must evaluate it now
        eval_command_base = "python3 bias-bench/experiments/stereoset_evaluation.py"

        # Create evaluation output path
        eval_output_path = os.path.join(
            evaluations_dir, f"eval_{os.path.splitext(pred_filename)[0]}.json"
        )

        eval_cmd = f"{eval_command_base}"f" --predictions_file {new_prediction_path}"f" --output_file {eval_output_path}"
        
        subprocess.run(eval_cmd, shell=True, cwd=self.repo_path)

        # save the evaluation result into a data structure
        with open(eval_output_path) as f:
            results = json.load(f)

        # if flag True, clean the files. This is instrumental for keeping it clean in 
        # later functions where we iteratively find the smallest valid dataset
        if clean_files:
            try:
                os.remove(new_prediction_path)
            except FileNotFoundError:
                pass

            try:
                os.remove(eval_output_path)
            except FileNotFoundError:
                pass

        # now, we have the json file loaded, we must skip the outermost key,
        # which is the model name, and return the dictionary inside
        model_key = next(iter(results))
        return results[model_key]
    
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

