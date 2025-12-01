# import necessary libraries
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
from sklearn.decomposition import PCA
import os, json

## PARAMETERS

# set model name and output file location, name
model_name = "bert-base-uncased"
output_file_name = "gender_bias_direction.json"
output_file_location = "debias_computations/results/"

# keywords for each end of bias
keywords_a = ["Male", "Man", "He", "Boy", "King"]
keywords_b = ["Female", "Woman", "She", "Girl", "Queen"]

## FUNCTION

# load tokenizer, model, put model into eval mode
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)
model.eval() # eval function makes it so that it's consistent across different runs, removes probabilistic features

def get_embeddings(word):
    # given a word, gets embedding of it
    tokens = tokenizer(word, return_tensors="pt") # tokens, in pytorch tensors suitable for model
    with torch.no_grad(): # we only care about result, not gradients that lead to it
        out = model(**tokens) # compute embeddings
    # below is converted to numpy array for computing differences
    return out.last_hidden_state[0,0].detach().cpu().numpy() # CLS embedding of first word given, embedding of the sentence basically
    
# create an array of differences for each pair's embeddings
differences = [] # differences array holds difference vectors for each word pair embeddings
for a, b in zip(keywords_a, keywords_b):
    embedding_a = get_embeddings(a)
    embedding_b = get_embeddings(b)
    differences.append(embedding_a - embedding_b)
differences = np.vstack(differences) # becomes one 2d array instead of a list of arrays, pca expects this

# do PCA analysis on difference of keyword arrays and get the first dimension
pca = PCA(n_components=1) # only get first pca, since we want a vector
pca.fit(differences)
result = pca.components_[0]
 
# save in a file
os.makedirs(output_file_location, exist_ok=True)
full_path = os.path.join(output_file_location, output_file_name)

with open(full_path, "w") as f:
    json.dump(result.tolist(), f)

