# Metrics

## Precision

Share of predicted fraud transactions that are actually labeled fraud.

## Recall

Share of labeled fraud transactions captured by the model.

## F1 Score

Harmonic mean of precision and recall.

## ROC AUC

Ranking quality across all classification thresholds.

## PR AUC

Fraud-focused ranking quality under class imbalance.

## Fraud Capture Rate Top 5 Percent

Share of all fraud labels found in the highest-risk 5 percent of scored transactions.

## False Positive Rate

Share of non-fraud transactions incorrectly predicted as fraud.

## Population Stability Index

Distribution shift between baseline and current feature populations. Values above 0.10 deserve review; values above 0.25 indicate material drift in this V0.1 project.
