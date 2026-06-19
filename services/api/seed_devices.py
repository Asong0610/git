"""种子数据：插入测试设备。"""

import os
import sys
from decimal import Decimal

sys.path.insert(0, os.path.dirname(__file__))

from app.db.session import SessionLocal
from app.db.models.device import Device


TEST_DEVICES = [
    {"device_code": "DEV001", "name": "共享充电宝", "category": "充电宝", "location": "图书馆一楼", "hourly_rate": Decimal("2.50")},
    {"device_code": "DEV002", "name": "共享充电宝", "category": "充电宝", "location": "图书馆二楼", "hourly_rate": Decimal("2.50")},
    {"device_code": "DEV003", "name": "单反相机", "category": "相机", "location": "学生会活动室", "hourly_rate": Decimal("15.00")},
    {"device_code": "DEV004", "name": "平板电脑 iPad", "category": "平板", "location": "教学楼A201", "hourly_rate": Decimal("5.00")},
    {"device_code": "DEV005", "name": "平板电脑 iPad", "category": "平板", "location": "教学楼B302", "hourly_rate": Decimal("5.00")},
    {"device_code": "DEV006", "name": "移动投影仪", "category": "投影仪", "location": "多功能厅", "hourly_rate": Decimal("20.00")},
    {"device_code": "DEV007", "name": "无线话筒", "category": "音响", "location": "礼堂", "hourly_rate": Decimal("3.00")},
    {"device_code": "DEV008", "name": "运动相机 GoPro", "category": "相机", "location": "体育器材室", "hourly_rate": Decimal("10.00")},
    {"device_code": "DEV009", "name": "蓝牙音箱", "category": "音响", "location": "操场器材室", "hourly_rate": Decimal("4.00")},
    {"device_code": "DEV010", "name": "笔记本电脑", "category": "电脑", "location": "创客空间", "hourly_rate": Decimal("8.00")},
]


def seed():
    db = SessionLocal()
    try:
        created = 0
        for device_data in TEST_DEVICES:
            existing = db.query(Device).filter(Device.device_code == device_data["device_code"]).first()
            if existing:
                print(f"  跳过: {device_data['device_code']} 已存在")
                continue
            device = Device(**device_data)
            db.add(device)
            created += 1

        db.commit()
        print(f"种子数据完成: 新增 {created} 台设备，共 {len(TEST_DEVICES)} 台")
    except Exception as e:
        db.rollback()
        print(f"错误: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    # 加载 .env
    env_file = os.path.join(os.path.dirname(__file__), "..", "deploy", ".env")
    if os.path.exists(env_file):
        with open(env_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()

    print("正在插入测试设备...")
    seed()
