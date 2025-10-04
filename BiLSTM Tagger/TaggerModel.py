from Data import Data
import torch
import os

def run_test():
    cwd = os.getcwd()
    trainfile, devfile = os.path.join(cwd, "train_data"), os.path.join(cwd, "dev_data")
    numWords = 50000
    data = Data(trainfile, devfile, numWords)

    for words, tags in data.trainSentences:
        wordIDs = data.words2IDs(words)
        tagIDs = data.tag2IDs(tags)

    numWords = 50000
    embSize = 200
    lstmSize = 400
    hiddenSize = 200
    dropoutRate = 0.3
    tagger = TaggerModel(data.numTags, numWords, embSize, lstmSize,
                         hiddenSize, dropoutRate)

    # Should automatically call forward method.
    tagLogits = tagger(torch.LongTensor(wordIDs))

class TaggerModel(torch.nn.Module):
    def __init__(self, num_tags, num_words, emb_size, lstm_size, hidden_size, dropout):
        """
        Constructor for the tagger neural network
        """
        super().__init__()
        self.num_words = num_words
        # num_words+1 wegen dem unknown-Token
        self.embedding = torch.nn.Embedding(num_words + 1, emb_size)
        self.bi_lstm = torch.nn.LSTM(emb_size, lstm_size, bidirectional=True)
        self.hidden_layer = torch.nn.Linear(lstm_size * 2, hidden_size)
        self.output_layer = torch.nn.Linear(hidden_size, num_tags)

        # Eine Dropout-Instanz reicht aus:
        self.dropout = torch.nn.Dropout(dropout)


    def forward(self, input_ids):
        """
        Method to utilize the neural network to predict the tags
        :return:
        """
        embedded = self.embedding(input_ids)
        if self.training:
            embedded = self.dropout(embedded)
        bi_lstm, _ = self.bi_lstm(embedded)
        if self.training:
            bi_lstm = self.dropout(bi_lstm)
        hidden = torch.nn.functional.tanh(self.hidden_layer(bi_lstm))
        if self.training:
            hidden = self.dropout(hidden)
        output = self.output_layer(hidden)
        return output



if __name__ == '__main__':
    run_test()
