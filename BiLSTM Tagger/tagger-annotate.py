from Data import Data
import torch

# System call: python tagger-train.py train_data.txt dev_data.txt parameter_file.txt --num_epochs=20
# --num_words=10000 --emb_size=200 --lstm_size=400 --hidden_size=400
# --dropout_rate=0.3 --learning_rate=0.0001

parfile = "parameter_file"
data = Data(parfile+".io")
model = torch.load(parfile+".pt")
