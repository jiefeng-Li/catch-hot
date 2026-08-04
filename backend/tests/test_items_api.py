"""热点列表、筛选、趋势与任务日志 API 测试（需求 7.4 / 7.5 / 7.6）。"""
from datetime import datetime, timedelta, timezone

import pytest

from backend.app.models import HotItem, Job, Tag
from backend.app.platforms import make_fingerprint


@pytest.fixture()
def seeded(db_session):
    tag = Tag(name="AI", keyword="AI", interval_minutes=60)
    db_session.add(tag)
    db_session.commit()
    db_session.refresh(tag)

    now = datetime.now(timezone.utc)
    for i in range(60):
        db_session.add(HotItem(
            tag_id=tag.id,
            platform="zhihu" if i % 2 == 0 else "github",
            title=f"AI 热点 {i}",
            url=f"https://example.com/item/{i}",
            summary="摘要",
            hot_score=float(i),
            score=float(i),
            meta={"sources": "unit-test"},
            fingerprint=make_fingerprint(f"https://example.com/item/{i}"),
            fetched_at=now - timedelta(minutes=i),
            published_at=now - timedelta(hours=i),
        ))
    db_session.commit()
    return tag


def test_default_limit_50(client, seeded):
    """验收：列表默认返回最近抓取的 50 条。"""
    resp = client.get(f"/api/hot-items?tag_id={seeded.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 60
    assert len(data["items"]) == 50


def test_sort_by_hot(client, seeded):
    resp = client.get(f"/api/hot-items?tag_id={seeded.id}&sort=hot&limit=5")
    scores = [it["hot_score"] for it in resp.json()["items"]]
    assert scores == sorted(scores, reverse=True)


def test_filter_platform_and_keyword(client, seeded):
    resp = client.get(f"/api/hot-items?tag_id={seeded.id}&platform=github")
    assert all(it["platform"] == "github" for it in resp.json()["items"])

    resp = client.get(f"/api/hot-items?tag_id={seeded.id}&keyword=热点 5")
    assert resp.json()["total"] >= 1


def test_trend_and_distribution(client, seeded):
    resp = client.get(f"/api/tags/{seeded.id}/trend?days=7")
    assert resp.status_code == 200
    points = resp.json()
    assert len(points) >= 1
    assert sum(p["count"] for p in points) == 60  # 口径与列表一致

    resp = client.get(f"/api/tags/{seeded.id}/platform-distribution")
    dist = {d["platform"]: d["count"] for d in resp.json()}
    assert dist == {"zhihu": 30, "github": 30}


def test_hot_item_score_and_meta_are_exposed(client, seeded):
    resp = client.get(f"/api/hot-items?tag_id={seeded.id}&limit=1")
    assert resp.status_code == 200
    item = resp.json()["items"][0]
    assert "score" in item
    assert item["score"] == item["hot_score"]
    assert item["meta"] == {"sources": "unit-test"}


def test_reset_data_endpoint(client, seeded, db_session):
    db_session.add(Job(tag_id=seeded.id, platform="zhihu", status="failed"))
    db_session.commit()

    resp = client.delete("/api/admin/reset-data")
    assert resp.status_code == 200
    assert resp.json()["ok"] is True
    assert db_session.query(HotItem).count() == 0
    assert db_session.query(Job).count() == 0


def test_jobs_listing(client, seeded, db_session):
    db_session.add(Job(tag_id=seeded.id, platform="zhihu", status="failed",
                       error_message="TimeoutError: xx", retry_count=2))
    db_session.commit()
    resp = client.get(f"/api/jobs?tag_id={seeded.id}&status=failed")
    assert resp.status_code == 200
    jobs = resp.json()
    assert len(jobs) == 1
    assert jobs[0]["platform"] == "zhihu"
    assert jobs[0]["error_message"]
