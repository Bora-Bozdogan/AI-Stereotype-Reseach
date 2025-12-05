from dataset_finder import DatasetFinder

finder = DatasetFinder(model="BertForMaskedLM", model_name_or_path="bert-base-uncased")

result = finder.run_test(clean_files=False)

print(result)