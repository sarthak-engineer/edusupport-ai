from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "support_tickets.csv"


def load_support_tickets() -> pd.DataFrame:
    """Load and normalize the support ticket dataset."""

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Support ticket dataset not found at: {DATA_PATH}"
        )

    df = pd.read_csv(DATA_PATH)

    # Normalize column names.
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # Parse date columns when available.
    for column in ["created_at", "resolved_at"]:
        if column in df.columns:
            df[column] = pd.to_datetime(
                df[column],
                errors="coerce"
            )

    # Normalize string columns.
    string_columns = [
        "ticket_id",
        "category",
        "priority",
        "status",
        "agent_id",
    ]

    for column in string_columns:
        if column in df.columns:
            df[column] = df[column].astype("string").str.strip()

    return df
