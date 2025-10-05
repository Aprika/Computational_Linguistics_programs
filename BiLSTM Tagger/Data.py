import pickle
import random as rnd
from collections import Counter


def read_data(file):
    all_sentences, sent = [], []
    with open(file, 'r', encoding='utf-8') as f:
        for line in f:
            split_line = line.strip().split("\t")
            if len(split_line) == 2:
                sent.append(split_line)
            else:
                # list of pairs --> pair of lists
                all_sentences.append(list(zip(*sent)))
                sent = []
    return all_sentences


def run_test():
    trainfile, devfile = "train_data", "dev_data"
    numWords = 50000
    data = Data(trainfile, devfile, numWords)
    print(data.trainSentences)

    for words, tags in data.trainSentences:
        wordIDs = data.words2IDs(words)
        tagIDs = data.tag2IDs(tags)

    for words, _ in data.devSentences:
        wordIDs = data.words2IDs(words)
        # bestTagIDs = annotate(wordIDs)  # This version will be uncommented after implementation
        bestTagIDs = []
        num_tags = data.numTags
        for word in wordIDs:
            bestTagIDs.append(rnd.randrange(num_tags))
        bestTags = data.IDs2tags(bestTagIDs)



class Data:
    def __init__(self, *args):
        if len(args) == 1:
            self.init_test(*args)
        else:
            self.init_train(*args)

    def init_train(self, training, development, num_words):
        """
        Constructor function of the class Data. Reads in the training and development Data, creates an index for the num_words most frequent words and an index for all tags.
        :param training:
        :param development:
        :param num_words:
        """
        # These attributes will be created here
        self.trainSentences = read_data(training)
        self.devSentences = read_data(development)

        # These attributes apply only to the training Data
        word_counts = Counter(w for words, _ in self.trainSentences for w in words)
        wordlist, _ = zip(*Counter(word_counts).most_common(num_words))
        self.word_index = {word: idx for idx, word in enumerate(wordlist, start=1)}
        self.tag_list = sorted(set(t for _, tags in self.trainSentences for t in tags))
        self.tag_index = {tag: idx for idx, tag in enumerate(self.tag_list)}
        self.numTags = len(self.tag_list)

    def init_test(self, parfile):
        with open(parfile, "rb") as f:
            d = pickle.load(f)
        self.trainSentences = d["trainSentences"]
        self.devSentences = d["devSentences"]
        self.word_index = d["word_index"]
        self.tag_list = d["tag_list"]
        self.tag_index = d["tag_index"]
        self.numTags = d["numTags"]

    def sentences(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                yield line.strip().split(' ')


    def words2IDs(self, words):
        """
        Converts a list of words into a list of word indices.
        :param words:
        :return:
        """
        return [self.word_index.get(word, 0) for word in words]


    def tag2IDs(self, tags):
        """
        Converts a list of tags into a list of tag indices.
        :param tags:
        :return:
        """
        return [self.tag_index.get(tag, -1) for tag in tags]

    def IDs2tags(self, tag_IDs):
        """
        Converts a list of tag indices back into a list of tags.
        :param tag_IDs:
        :return:
        """
        tag_list = []
        for idx in tag_IDs:
            tag_list.append(self.tag_list[idx])
        return tag_list

    def save(self, parfile):
        with open(parfile, "wb") as f:
            pickle.dump({"trainSentences": self.trainSentences,
                         "devSentences": self.devSentences,
                         "word_index": self.word_index,
                         "tag_list": self.tag_list,
                         "tag_index": self.tag_index,
                         "numTags": self.numTags}, f)


if __name__ == '__main__':
    run_test()
