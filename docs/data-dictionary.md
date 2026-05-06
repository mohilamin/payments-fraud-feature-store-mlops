# Data Dictionary

## payment_transactions

- `transaction_id`: synthetic transaction key.
- `customer_id`: synthetic customer key.
- `account_id`: synthetic account key.
- `merchant_id`: synthetic merchant key.
- `device_id`: synthetic device key.
- `transaction_timestamp`: synthetic event time.
- `amount`: transaction amount.
- `currency`: fake transaction currency.
- `payment_channel`: channel such as card-present or card-not-present.
- `fraud_label`: deterministic synthetic fraud label.

## transaction_features

The feature table contains point-in-time customer, merchant, device, and transaction risk features used for training and scoring.
