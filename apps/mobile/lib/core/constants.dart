import 'package:flutter/foundation.dart' show kIsWeb;

/// API 配置
class ApiConstants {
  // Web 环境使用相对路径（同域 Nginx 代理），原生环境使用服务器 IP 直连
  // 域名 asong0610.xyz 未备案，运营商会在 TLS 握手时根据 SNI 拦截
  static const String baseUrl =
      kIsWeb ? '/api/v1' : 'https://111.231.77.186/api/v1';

  // 原生环境需手动设置 Host 头，让 Nginx 匹配到正确的虚拟主机
  static const String? hostHeader =
      kIsWeb ? null : 'asong0610.xyz';

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
  static const String returned = 'returned';
  static const String cancelled = 'cancelled';
}
