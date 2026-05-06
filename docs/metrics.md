# Metrics

## Precision

Business meaning: share of flagged transactions that are actually synthetic fraud. Formula: `true_positives / (true_positives + false_positives)`. Inputs: model predictions and `fraud_label`. Interpretation: higher precision means less investigator waste and less customer friction. Example: `0.40` means 40 percent of fraud predictions are labeled fraud.

## Recall

Business meaning: share of known fraud captured by the model. Formula: `true_positives / (true_positives + false_negatives)`. Inputs: model predictions and `fraud_label`. Interpretation: higher recall means stronger fraud capture. Example: `0.70` means 70 percent of labeled fraud was caught.

## F1 Score

Business meaning: balance between precision and recall. Formula: `2 * precision * recall / (precision + recall)`. Inputs: precision and recall. Interpretation: useful when both missed fraud and false positives matter.

## ROC AUC

Business meaning: ranking quality across thresholds. Formula: area under true-positive-rate versus false-positive-rate curve. Inputs: labels and fraud probabilities. Interpretation: closer to `1.0` means better general ranking.

## PR AUC

Business meaning: fraud-focused ranking quality under class imbalance. Formula: area under precision-recall curve. Inputs: labels and fraud probabilities. Interpretation: often more useful than ROC AUC for rare fraud.

## Fraud Capture Rate Top 1/5/10 Percent

Business meaning: share of all fraud found in the highest-risk slice of transactions. Formula: `fraud labels in top N percent by score / total fraud labels`. Inputs: fraud probabilities and labels. Interpretation: useful for alert-capacity planning.

## False Positive Rate

Business meaning: share of legitimate transactions incorrectly flagged. Formula: `false_positives / (false_positives + true_negatives)`. Inputs: predictions and labels. Interpretation: lower values mean less customer friction.

## Population Stability Index

Business meaning: distribution shift between baseline and current feature populations. Formula: `sum((actual_pct - expected_pct) * ln(actual_pct / expected_pct))` across bins. Inputs: baseline and current feature values. Interpretation: below `0.10` is low drift, `0.10-0.25` warrants review, above `0.25` is high drift.

## Mean Shift

Business meaning: change in average feature value. Formula: `current_mean - baseline_mean`. Inputs: numeric feature values. Interpretation: large shifts can signal data or behavior changes.

## Missing Rate Change

Business meaning: change in feature null rate. Formula: `current_missing_rate - baseline_missing_rate`. Inputs: feature null counts. Interpretation: rising missingness can indicate ingestion or upstream quality problems.

## Feature Store Quality Score

Business meaning: compact indicator of feature table health. Formula: weighted score from feature group missingness, zero-variance penalties, and point-in-time validation pass rate. Inputs: feature table, feature definitions, validation report. Interpretation: closer to `100` means features are complete, variable, and point-in-time safe.

## Alert Queue Quality Score

Business meaning: operational usefulness of generated fraud alerts. Formula: weighted blend of alert precision estimate and alert volume sanity. Inputs: scored transactions, labels, risk bands, reason codes. Interpretation: higher means alerts are both meaningful and manageable.

## Monitoring Summary Score

Business meaning: health of current scoring population. Formula: `100 - high_drift_penalties - medium_drift_penalties - score_shift_penalty`. Inputs: PSI, mean shift, missing-rate change, fraud score shift. Interpretation: lower scores indicate more monitoring risk.
