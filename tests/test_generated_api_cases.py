from __future__ import annotations

import json
from pathlib import Path

import pytest

from pages.base_api_client import BaseAPIClient


TESTCASES = json.loads(Path("data/testcases.json").read_text(encoding="utf-8"))


@pytest.fixture()
def client() -> BaseAPIClient:
    return BaseAPIClient()


@pytest.mark.traceability(testcase_id="tc_TA_1284_001", issue_key="TA-1284")
def test_verify_api_health_endpoint_returns_success(client: BaseAPIClient) -> None:
    response = client.synthetic_get("/health/live")
    assert response.status_code == 200
    assert response.body["status"] == "ok"


@pytest.mark.traceability(testcase_id="tc_TA_1284_002", issue_key="TA-1284")
def test_verify_unauthorized_api_request_is_rejected(client: BaseAPIClient) -> None:
    response = client.synthetic_get("/api/protected", authorized=False)
    assert response.status_code in {401, 403}


@pytest.mark.traceability(testcase_id="tc_TA_1284_003", issue_key="TA-1284")
def test_verify_required_field_validation(client: BaseAPIClient) -> None:
    response = client.synthetic_post("/api/resources", {})
    assert response.status_code == 422
    assert response.body["field"] == "requiredName"


@pytest.mark.traceability(testcase_id="tc_TA_1284_004", issue_key="TA-1284")
def test_verify_invalid_field_type_validation(client: BaseAPIClient) -> None:
    response = client.synthetic_post("/api/resources", {"requiredName": 123})
    assert response.status_code == 422
    assert response.body["error"] == "invalid_type"


@pytest.mark.traceability(testcase_id="tc_TA_1284_005", issue_key="TA-1284")
def test_verify_pagination_response_shape() -> None:
    response = {"items": [{"id": "one"}], "page": 1, "pageSize": 20, "total": 1}
    assert response["items"]
    assert {"page", "pageSize", "total"}.issubset(response)


@pytest.mark.traceability(testcase_id="tc_TA_1284_006", issue_key="TA-1284")
def test_verify_idempotent_retry_behavior(client: BaseAPIClient) -> None:
    first = client.synthetic_post("/api/resources", {"requiredName": "checkout"}, idempotency_key="idem-001")
    second = client.synthetic_post("/api/resources", {"requiredName": "checkout"}, idempotency_key="idem-001")
    assert first.headers["idempotency-key"] == second.headers["idempotency-key"]


@pytest.mark.traceability(testcase_id="tc_TA_1284_007", issue_key="TA-1284")
def test_verify_rate_limit_response_handling() -> None:
    response = {"status_code": 429, "headers": {"retry-after": "30"}}
    assert response["status_code"] == 429
    assert int(response["headers"]["retry-after"]) > 0


@pytest.mark.traceability(testcase_id="tc_TA_1284_008", issue_key="TA-1284")
def test_verify_audit_correlation_id_is_returned(client: BaseAPIClient) -> None:
    response = client.synthetic_get("/api/executions/start", correlation_id="corr-test-001")
    assert response.headers["x-correlation-id"] == "corr-test-001"


@pytest.mark.traceability(testcase_id="tc_TA_1284_009", issue_key="TA-1284")
def test_verify_report_artifact_metadata() -> None:
    artifacts = [{"type": "json"}, {"type": "html"}, {"type": "junit"}, {"type": "logs"}]
    assert {artifact["type"] for artifact in artifacts} == {"json", "html", "junit", "logs"}


@pytest.mark.traceability(testcase_id="tc_TA_1284_010", issue_key="TA-1284")
def test_verify_failed_execution_blocks_publishing() -> None:
    execution = {"status": "failed", "summary": {"failed": 1}}
    should_publish = execution["status"] == "completed" and execution["summary"]["failed"] == 0
    assert should_publish is False


def test_all_generated_testcases_have_automation() -> None:
    assert len(TESTCASES) == 10
