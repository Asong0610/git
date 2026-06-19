"""全局 JSON 编码器：Decimal 输出为字符串。"""

import json
from decimal import Decimal
from datetime import datetime, date


class AppJSONEncoder(json.JSONEncoder):
    """自定义 JSON 编码器，处理 Decimal、datetime 等类型。"""

    def default(self, obj):
        if isinstance(obj, Decimal):
            return format(obj, "f")
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)


def custom_json_dumps(v):
    return json.dumps(v, cls=AppJSONEncoder, ensure_ascii=False)
