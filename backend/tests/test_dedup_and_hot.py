"""去重与热度归一化测试（对应需求 7.3 验收标准）。"""
from backend.app.models import Tag
from backend.app.platforms import BasePlatform, RawItem, make_fingerprint, normalize_url
from backend.app.services.crawler import save_items


def _make_tag(db):
    tag = Tag(name="t", keyword="k", interval_minutes=60)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


class _StubPlatform(BasePlatform):
    name = "stub"


def test_url_normalization():
    a = normalize_url("HTTPS://Example.COM/path/?utm_source=x&id=1#frag")
    b = normalize_url("https://example.com/path?id=1")
    assert a == b
    assert make_fingerprint(a) == make_fingerprint(b)


def test_same_url_saved_once(db_session):
    """验收：相同链接内容在同一标签下仅保留 1 条。"""
    tag = _make_tag(db_session)
    platform = _StubPlatform()

    items = [RawItem(title="标题A", url="https://a.com/p?id=1", raw_hot=10.0)]
    fetched1, saved1 = save_items(db_session, tag, platform.name, items)
    db_session.commit()

    # 同链接（带跟踪参数）再次抓取 -> 去重
    items2 = [RawItem(title="标题A-改", url="https://a.com/p?id=1&utm_source=share", raw_hot=20.0)]
    fetched2, saved2 = save_items(db_session, tag, platform.name, items2)
    db_session.commit()

    assert (fetched1, saved1) == (1, 1)
    assert (fetched2, saved2) == (1, 0)


def test_similar_title_deduped(db_session):
    tag = _make_tag(db_session)
    items = [
        RawItem(title="AI 编程工具迎来大更新，体验全面提升", url="https://a.com/1"),
        RawItem(title="AI 编程工具迎来大更新，体验全面提升！", url="https://b.com/2"),
    ]
    fetched, saved = save_items(db_session, tag, "stub", items)
    db_session.commit()
    assert fetched == 2
    assert saved == 1  # 标题高度相似被去重


def test_hot_normalization():
    p = _StubPlatform()
    scores = [p.normalize_hot(v, [100.0, 200.0, 300.0]) for v in [100.0, 200.0, 300.0]]
    assert scores[0] == 0.0
    assert scores[2] == 100.0
    assert 40 < scores[1] < 60
    # 无热度字段 -> 默认值，可正常展示（验收标准）
    assert p.normalize_hot(None, [100.0]) == 0.0


def test_no_hot_field_still_displayed(db_session):
    tag = _make_tag(db_session)
    items = [RawItem(title="无热度内容", url="https://a.com/x", raw_hot=None)]
    _, saved = save_items(db_session, tag, "stub", items)
    db_session.commit()
    assert saved == 1
