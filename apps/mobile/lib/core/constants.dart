/// API 配置
class ApiConstants {
  // 云服务器地址
  static const String baseUrl = 'http://111.231.77.186:8000/api/v1';

  static const Duration connectTimeout = Duration(seconds: 10);
  static const Duration receiveTimeout = Duration(seconds: 15);
}

/// 存储键
class StorageKeys {
  static const String accessToken = 'access_token';
  static const String refreshToken = 'refresh_token';
  static const String userId = 'user_id';
  static const String phone = 'phone';
}

/// 设备状态
class DeviceStatus {
  static const String available = 'available';
  static const String borrowed = 'borrowed';
  static const String maintenance = 'maintenance';
}

/// 订单状态
class OrderStatus {
  static const String active = 'active';
  static const String overdue = 'overdue';
  static const String returned = 'returned';
  static const String cancelled = 'cancelled';
}
