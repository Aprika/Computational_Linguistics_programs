from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
import argparse
import json
import sys

class Classifier:
    def __init__(self, train_path, test_path):
        with open(train_path) as train:
            self.training_data = json.load(train)

        with open(test_path) as test:
            self.testing_data = json.load(test)

    def training(self):
        example_sentences = [literature_dict["text"] for literature_dict in self.training_data]
        vectorizer = TfidfVectorizer(tokenizer=lambda text: text.split(), stop_words='german')



    def evaluation(self):
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_path", type=str, help="Path to classifier training data", required=True)
    parser.add_argument("--eval_path", type=str, help="Path to classifier evaluation data", required=True)
    args = parser.parse_args(sys.argv[1:])
    classifier = Classifier(args.train_path, args.eval_path)
    classifier.training()
    classifier.evaluation()
