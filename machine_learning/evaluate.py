"""Tiny evaluator: train on `training_data.csv` and print the classification report.

Usage:
  python evaluate.py

Prints a compact table for 'comfortable' and 'uncomfortable'.
"""

from pathlib import Path
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix


def main():
    data = pd.read_csv(Path(__file__).parent / 'training_data.csv')
    X = data[['temperature', 'humidity', 'pressure']].values
    y = (data['status'] == 'Comfortable').astype(int).values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42)

    clf = RandomForestClassifier(
        n_estimators=10, max_depth=5, random_state=42)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    report = classification_report(
        y_test, y_pred, digits=3, labels=[1, 0],
        target_names=['comfortable', 'uncomfortable'])
    cm = confusion_matrix(y_test, y_pred)
    fi = clf.feature_importances_
    importances = [round(float(x), 3) for x in fi]

    # Build full output string
    output = (
        report + "\n"
        "Confusion matrix:\n" +
        str(cm) + "\n\n"
        "Feature importances (temperature, humidity, pressure):\n" +
        str(importances) + "\n")

    # Save to file
    output_path = Path(__file__).parent / "results.txt"
    with open(output_path, "w") as f:
        f.write(output)

    # Also print to console (optional)
    print(output)


if __name__ == '__main__':
    main()
