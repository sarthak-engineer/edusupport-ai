from app.anomalies.detector import AnomalyDetector


def test_anomaly_detector_returns_list():
    detector = AnomalyDetector()

    result = detector.detect()

    assert isinstance(result, list)


def test_anomaly_summary():
    detector = AnomalyDetector()

    result = detector.summary()

    assert "total_anomalies" in result
    assert "by_type" in result


def test_anomalies_have_required_fields():
    detector = AnomalyDetector()

    result = detector.detect()

    for anomaly in result:
        assert "ticket_id" in anomaly
        assert "anomaly_type" in anomaly
        assert "severity" in anomaly
        assert "reason" in anomaly
