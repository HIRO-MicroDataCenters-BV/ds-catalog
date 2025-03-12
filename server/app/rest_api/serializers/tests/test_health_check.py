from ..health_check import HealthCheck


def test_health_check() -> None:
    health_check = HealthCheck(status="OK")
    assert health_check.status == "OK"

    health_check = HealthCheck(status="FAIL")
    assert health_check.status == "FAIL"
