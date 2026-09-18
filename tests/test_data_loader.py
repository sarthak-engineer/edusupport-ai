from app.data.loader import load_support_tickets


def test_load_support_tickets():
    df = load_support_tickets()

    assert not df.empty
    assert len(df) == 500
    assert "ticket_id" in df.columns
    assert "created_at" in df.columns
    assert "status" in df.columns
