from backend.app.database import SessionLocal
from backend.app.models import HotItem
from backend.app.services.crawler import _compute_composite_score

def main():
    db = SessionLocal()
    items = db.query(HotItem).all()
    updated = 0
    for it in items:
        try:
            score = _compute_composite_score(it, it.hot_score)
            if score != (it.score or 0):
                it.score = score
                updated += 1
        except Exception as e:
            print('error computing for', it.id, e)
    db.commit()
    print('updated', updated)

if __name__ == '__main__':
    main()
