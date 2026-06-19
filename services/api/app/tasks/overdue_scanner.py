"""逾期订单扫描任务：将超过 due_at 的 active 订单标记为 overdue。"""

import time
from datetime import datetime

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models.borrow_order import BorrowOrder


def scan_overdue_orders() -> int:
    """扫描并标记逾期订单，返回更新数量。"""
    db: Session = SessionLocal()
    try:
        now = datetime.utcnow()
        stmt = select(BorrowOrder).where(
            and_(
                BorrowOrder.status == "active",
                BorrowOrder.due_at < now,
            )
        )
        overdue_orders = list(db.execute(stmt).scalars().all())

        for order in overdue_orders:
            order.status = "overdue"

        if overdue_orders:
            db.commit()

        return len(overdue_orders)
    except Exception as e:
        db.rollback()
        print(f"[overdue_scanner] 错误: {e}")
        return 0
    finally:
        db.close()


def run_scanner_loop(interval_seconds: int = 60):
    """循环执行扫描任务。"""
    print(f"[overdue_scanner] 启动，扫描间隔 {interval_seconds}s")
    while True:
        try:
            count = scan_overdue_orders()
            if count > 0:
                print(f"[overdue_scanner] {datetime.utcnow().isoformat()} 标记了 {count} 个逾期订单")
        except Exception as e:
            print(f"[overdue_scanner] 异常: {e}")
        time.sleep(interval_seconds)


if __name__ == "__main__":
    run_scanner_loop()
