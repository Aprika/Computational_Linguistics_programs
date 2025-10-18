from pathlib import PurePath
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from sklearn import metrics
import argparse
import json
import numpy as np
import sys

# Terminal command to run classifier:
# > python simple_classifier.py --train_path <training_file_path> --eval_path <evaluation_file_path>

class Classifier:
    def __init__(self, train_path, test_path):
        """
        Reads input JSON files, extracts sentences and labels. Sets up sklearn pipeline.
        :param train_path: training file path (JSON file)
        :param test_path: evaluation file path (JSON file)
        :return: None
        """
        self.training_sentences = []
        self.training_labels = []
        with open(PurePath(train_path), encoding="utf-8") as train:
            for train_line in train:
                training_data = json.loads(train_line)
                self.training_sentences.append(training_data["text"])
                self.training_labels.append(training_data["author"])

        self.eval_sentences = []
        self.eval_labels = []
        with open(PurePath(test_path), encoding="utf-8") as test:
            for eval_line in test:
                testing_data = json.loads(eval_line)
                self.eval_sentences.append(testing_data["text"])
                self.eval_labels.append(testing_data["author"])

        # Create model pipeline
        self.model = make_pipeline(TfidfVectorizer(), LogisticRegression())


    def training(self):
        """
        Trains sklearn pipeline on author classification training data.
        :return: None
        """
        # Train on training sentences using Logistic Regression
        self.model.fit(self.training_sentences, self.training_labels)


    def evaluation(self):
        """
        Runs the trained LogisticRegression model on evaluation sentences. Prints out evaluation metrics for each author.
        :return: None
        """
        # Make numpy array of authors in the evaluation set
        eval_label_set = np.array(list(set(self.eval_labels)))

        predicted_labels = self.model.predict(self.eval_sentences)

        # Evaluate performance using Precision, Recall and F1-Score for all labels
        precision, recall, f1_score, _ = metrics.precision_recall_fscore_support(self.eval_labels, predicted_labels, average=None,labels=eval_label_set)
        print(f'\nPrecision: {np.column_stack((eval_label_set, precision))}')
        print(f'\nRecall: {np.column_stack((eval_label_set, recall))}')
        print(f'\nF1-Score: {np.column_stack((eval_label_set, f1_score))}')



if __name__ == '__main__':
    # Define arguments to be passed in command line
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_path", type=str, help="Path to classifier training data", required=True)
    parser.add_argument("--eval_path", type=str, help="Path to classifier evaluation data", required=True)
    args = parser.parse_args(sys.argv[1:])

    # Run the classification functions
    classifier = Classifier(args.train_path, args.eval_path)
    classifier.training()
    classifier.evaluation()
