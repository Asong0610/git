"""聚合导出所有 ORM 模型，供 Alembic 与业务层引用。"""

from app.db.models.borrow_order import BorrowOrder
from app.db.models.device import Device
from app.db.models.deposit_ledger import DepositLedger
from app.db.models.fault_ticket import FaultRepairTicket
from app.db.models.user import User

__all__ = ["User", "Device", "BorrowOrder", "DepositLedger", "FaultRepairTicket"]
