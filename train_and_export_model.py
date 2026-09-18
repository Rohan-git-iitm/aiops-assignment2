# Trains TF-IDF + Naive Bayes on the spam dataset and saves it for the API
import argparse
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/spam_dataset.csv")
    parser.add_argument("--out", default="data/model.joblib")
    args = parser.parse_args()

    df = pd.read_csv(args.data)
    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["label"], test_size=0.2, random_state=42, stratify=df["label"])

    model = make_pipeline(TfidfVectorizer(), MultinomialNB())
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    print(f"accuracy={accuracy_score(y_test, preds):.4f}")

    joblib.dump(model, args.out)
    print(f"saved model to {args.out}")


if __name__ == "__main__":
    main()
