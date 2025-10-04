from Data import Data
from TaggerModel import TaggerModel
import argparse
import sys
import random as rnd
import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


parser = argparse.ArgumentParser()
parser.add_argument("training_file", type=str)
parser.add_argument("development_file", type=str)
parser.add_argument("parameter_file", type=str)
parser.add_argument("--num_epochs", default=20, help="Number of training epochs", type=int)
parser.add_argument("--num_words", default=10000, help="Maximum number of words to be mapped to IDs", type=int)
parser.add_argument("--emb_size", default=200, help="Output size for the embedding layer", type=int)
parser.add_argument("--lstm_size", default=400, help="Output size for the LSTM layer", type=int)
parser.add_argument("--hidden_size", default=400, help="Output size for the hidden layers", type=int)
parser.add_argument("--dropout_rate", default=0.3, help="Dropout rate", type=float)
parser.add_argument("--learning_rate", default=0.0001, help="Learning rate", type=float)


args = parser.parse_args(sys.argv[1:])
data = Data(args.training_file, args.development_file, args.num_words)
parfile = args.parameter_file
data.save(parfile+".io")
tagger_model = TaggerModel(data.numTags, args.num_words, args.emb_size, args.lstm_size, args.hidden_size, args.dropout_rate).to(device)

loss_fn = torch.nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(tagger_model.parameters(), lr=args.learning_rate)

best_accuracy = 0


with open(parfile, "w", encoding="utf-8") as f:
    for epoch in range(args.num_epochs):
        model_loss = 0.0

        tagger_model.train()
        rnd.shuffle(data.trainSentences)

        for words, tags in data.trainSentences:
            word_ids = torch.LongTensor(data.words2IDs(words))
            tag_ids = torch.LongTensor(data.tag2IDs(tags))
            predict_tags = tagger_model(word_ids)
            optimizer.zero_grad()
            loss = loss_fn(predict_tags, tag_ids)
            loss.backward()
            optimizer.step()

        tagger_model.eval()

        correct = 0
        total = 0
        for dev_sents in data.devSentences:
            dev_word_ids, dev_tags = dev_sents
            total += len(dev_word_ids)
            dev_word_ids = torch.LongTensor(dev_word_ids)
            dev_tags = torch.LongTensor(dev_tags)

            dev_predict_tags = tagger_model(dev_word_ids)
            dev_predict_tags = torch.argmax(dev_predict_tags)
            correct += (dev_predict_tags == dev_tags).sum().item()

        accuracy = 100 * correct / total

        with open("logfile.txt", "a", encoding="utf-8") as logfile:
            logfile.write(f"Epoch {epoch+1}: {accuracy}")

        if accuracy > best_accuracy:
            best_accuracy = accuracy
            torch.save(tagger_model, parfile)
