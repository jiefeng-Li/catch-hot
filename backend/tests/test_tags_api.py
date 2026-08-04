"""标签管理 API 测试（对应需求 7.1 验收标准）。"""


def test_create_and_list_tag(client):
    resp = client.post("/api/tags", json={
        "name": "AI 编程工具",
        "keyword": "AI 编程",
        "platforms": ["zhihu", "bilibili"],
        "interval_minutes": 30,
    })
    assert resp.status_code == 201
    tag = resp.json()
    assert tag["enabled"] is True

    # 验收：创建后立即可在列表中看到
    resp = client.get("/api/tags")
    assert resp.status_code == 200
    names = [t["name"] for t in resp.json()]
    assert "AI 编程工具" in names


def test_create_tag_with_multiple_keywords(client):
    resp = client.post("/api/tags", json={
        "name": "多关键词标签",
        "keywords": ["OpenAI", "Claude"],
        "platforms": ["zhihu"],
        "interval_minutes": 30,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["keywords"] == ["OpenAI", "Claude"]
    assert data["keyword"] == "OpenAI, Claude"


def test_update_tag(client):
    tag = client.post("/api/tags", json={"name": "t1", "keyword": "k1"}).json()
    resp = client.put(f"/api/tags/{tag['id']}", json={"keyword": "k2", "interval_minutes": 120})
    assert resp.status_code == 200
    assert resp.json()["keyword"] == "k2"
    assert resp.json()["interval_minutes"] == 120


def test_toggle_tag(client):
    tag = client.post("/api/tags", json={"name": "t1", "keyword": "k1"}).json()
    resp = client.post(f"/api/tags/{tag['id']}/toggle")
    assert resp.json()["enabled"] is False
    resp = client.post(f"/api/tags/{tag['id']}/toggle")
    assert resp.json()["enabled"] is True


def test_delete_is_logical(client):
    tag = client.post("/api/tags", json={"name": "t1", "keyword": "k1"}).json()
    resp = client.delete(f"/api/tags/{tag['id']}")
    assert resp.status_code == 204
    # 默认列表不可见
    assert tag["id"] not in [t["id"] for t in client.get("/api/tags").json()]
    # 历史数据保留（逻辑删除）
    assert tag["id"] in [t["id"] for t in client.get("/api/tags?include_deleted=true").json()]


def test_invalid_platform_rejected(client):
    resp = client.post("/api/tags", json={
        "name": "t1", "keyword": "k1", "platforms": ["not_exist"]
    })
    assert resp.status_code == 422


def test_get_missing_tag_404(client):
    assert client.get("/api/tags/9999").status_code == 404
