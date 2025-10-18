from pathlib import PurePath
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from sklearn import metrics
import argparse
import json
import sys

# Terminal command to run classifier:
# > python simple_classifier.py --train_path <training_file_path> --eval_path <evaluation_file_path>

class Classifier:
    def __init__(self, train_path, test_path):
        with open(PurePath(train_path)) as train:
            self.training_data = json.load(train)

        with open(PurePath(test_path)) as test:
            self.testing_data = json.load(test)

        # Extract the relevant data from json file
        self.training_sentences = [literature_dict["text"] for literature_dict in self.training_data]
        self.training_labels = [literature_dict["author"] for literature_dict in self.training_data]

        self.eval_sentences = [literature_dict["text"] for literature_dict in self.testing_data]
        self.eval_labels = [literature_dict["author"] for literature_dict in self.testing_data]

        # Create model pipeline
        self.model = make_pipeline(TfidfVectorizer(), LogisticRegression())


    def training(self):
        # Train on training sentences using Logistic Regression
        self.model.fit(self.training_sentences, self.training_labels)



    def evaluation(self):
        # Run the trained LogisticRegression model on evaluation sentences
        predicted_labels = self.model.predict(self.eval_sentences)

        # Evaluate performance using Precision, Recall and F1-Score (Seaborn heat map?)
        precision = metrics.precision_score(self.eval_labels, predicted_labels)
        print(f'Precision: {precision}')
        recall = metrics.recall_score(self.eval_labels, predicted_labels)
        print(f'Recall: {recall}')
        f1_score = metrics.f1_score(self.eval_labels, predicted_labels)
        print(f'F1-Score: {f1_score}')



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_path", type=str, help="Path to classifier training data", required=True)
    parser.add_argument("--eval_path", type=str, help="Path to classifier evaluation data", required=True)
    args = parser.parse_args(sys.argv[1:])
    classifier = Classifier(args.train_path, args.eval_path)
    classifier.training()
    classifier.evaluation()
