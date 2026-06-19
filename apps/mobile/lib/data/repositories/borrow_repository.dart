import 'package:dio/dio.dart';
import '../api/api_client.dart';
import '../models/borrow_order.dart';
import 'package:uuid/uuid.dart';

class BorrowRepository {
  final ApiClient _api = ApiClient();
  final _uuid = const Uuid();
  
  // 借出设备
  Future<BorrowOrder> borrowDevice(String deviceCode, int durationHours) async {
    try {
      final response = await _api.post('/borrows', data: {
        'device_code': deviceCode,
        'duration_hours': durationHours,
        'idempotency_key': _uuid.v4(),
      });
      
      if (response.statusCode == 200) {
        return BorrowOrder.fromJson(response.data);
      }
      
      throw Exception(response.data['message'] ?? '借出失败');
    } catch (e) {
      if (e is DioException && e.response != null) {
        throw Exception(e.response!.data['message'] ?? '借出失败');
      }
      rethrow;
    }
  }
  
  // 归还设备
  Future<Map<String, dynamic>> returnDevice(String orderId) async {
    try {
      final response = await _api.post('/borrows/$orderId/return', data: {
        'idempotency_key': _uuid.v4(),
      });
      
      if (response.statusCode == 200) {
        return response.data;
      }
      
      throw Exception(response.data['message'] ?? '归还失败');
    } catch (e) {
      if (e is DioException && e.response != null) {
        throw Exception(e.response!.data['message'] ?? '归还失败');
      }
      rethrow;
    }
  }
  
  // 获取当前订单
  Future<BorrowOrder?> getCurrentOrder() async {
    try {
      final response = await _api.get('/borrows/current');
      if (response.statusCode == 200 && response.data != null) {
        return BorrowOrder.fromJson(response.data);
      }
      return null;
    } catch (e) {
      return null;
    }
  }
  
  // 获取订单列表
  Future<List<BorrowOrder>> getOrders({String? status, int page = 1, int pageSize = 20}) async {
    try {
      final queryParameters = <String, dynamic>{
        'page': page,
        'page_size': pageSize,
      };
      
      if (status != null && status.isNotEmpty) {
        queryParameters['status'] = status;
      }
      
      final response = await _api.get('/borrows', queryParameters: queryParameters);
      
      if (response.statusCode == 200) {
        final items = response.data['items'] as List;
        return items.map((item) => BorrowOrder.fromJson(item)).toList();
      }
      
      throw Exception('获取订单列表失败');
    } catch (e) {
      rethrow;
    }
  }
}
