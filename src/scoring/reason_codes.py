from __future__ import annotations

DESCRIPTIONS = {
    "HIGH_VELOCITY_CUSTOMER": "Customer has unusually high recent transaction velocity.",
    "NEW_DEVICE_HIGH_VALUE": "High-value purchase from a newly observed device.",
    "INTERNATIONAL_MISMATCH": "Customer, merchant, or IP country mismatch.",
    "RISKY_MERCHANT": "Merchant risk score or category is elevated.",
    "AMOUNT_OUTLIER": "Transaction amount is high relative to customer history.",
    "MULTIPLE_FAILED_AUTHS": "Multiple failed authorizations in the recent window.",
    "NIGHT_TRANSACTION_BURST": "Transaction occurred during night-risk hours.",
    "DEVICE_LINKED_TO_MULTIPLE_CUSTOMERS": "Device is linked to multiple recent customers.",
}


def risk_band(probability: float) -> str:
    """Assign a fraud risk band."""
    if probability >= 0.85:
        return "critical"
    if probability >= 0.60:
        return "high"
    if probability >= 0.30:
        return "medium"
    return "low"


def recommended_action(band: str) -> str:
    """Map risk band to action."""
    return {
        "low": "approve",
        "medium": "step_up_authentication",
        "high": "manual_review",
        "critical": "decline",
    }[band]


def generate_reason_codes(row: dict[str, object]) -> list[str]:
    """Generate deterministic reason codes."""
    codes: list[str] = []
    if float(row.get("customer_txn_count_1h", 0)) >= 5:
        codes.append("HIGH_VELOCITY_CUSTOMER")
    if int(row.get("new_device_flag", 0)) == 1 and float(row.get("amount", 0)) >= 500:
        codes.append("NEW_DEVICE_HIGH_VALUE")
    if int(row.get("international_mismatch_flag", 0)) == 1:
        codes.append("INTERNATIONAL_MISMATCH")
    if float(row.get("merchant_risk_score", 0)) >= 0.35 or int(row.get("risky_merchant_category_flag", 0)) == 1:
        codes.append("RISKY_MERCHANT")
    if float(row.get("amount_zscore_customer", 0)) >= 3:
        codes.append("AMOUNT_OUTLIER")
    if float(row.get("customer_failed_auth_count_24h", 0)) >= 2:
        codes.append("MULTIPLE_FAILED_AUTHS")
    if int(row.get("night_transaction_flag", 0)) == 1:
        codes.append("NIGHT_TRANSACTION_BURST")
    if float(row.get("device_distinct_customers_24h", 0)) >= 2:
        codes.append("DEVICE_LINKED_TO_MULTIPLE_CUSTOMERS")
    return codes[:3] or ["LOW_RISK_BASELINE"]


def descriptions(codes: list[str]) -> list[str]:
    """Return human-readable reason descriptions."""
    return [DESCRIPTIONS.get(code, "No major deterministic risk trigger.") for code in codes]
