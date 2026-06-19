import '../api/api_client.dart';
import '../models/device.dart';

class DeviceRepository {
  final ApiClient _api = ApiClient();
  
  // 获取设备列表
  Future<List<Device>> getDevices({
    String? category,
    String? status,
    String? location,
    int page = 1,
    int pageSize = 20,
  }) async {
    try {
      final queryParameters = <String, dynamic>{
        'page': page,
        'page_size': pageSize,
      };
      
      if (category != null && category.isNotEmpty) {
        queryParameters['category'] = category;
      }
      if (status != null && status.isNotEmpty) {
        queryParameters['status'] = status;
      }
      if (location != null && location.isNotEmpty) {
        queryParameters['location'] = location;
      }
      
      final response = await _api.get('/devices', queryParameters: queryParameters);
      
      if (response.statusCode == 200) {
        final items = response.data['items'] as List;
        return items.map((item) => Device.fromJson(item)).toList();
      }
      
      throw Exception('获取设备列表失败');
    } catch (e) {
      rethrow;
    }
  }
  
  // 获取设备详情
  Future<Device> getDeviceByCode(String deviceCode) async {
    try {
      final response = await _api.get('/devices/$deviceCode');
      if (response.statusCode == 200) {
        return Device.fromJson(response.data);
      }
      throw Exception('设备不存在');
    } catch (e) {
      rethrow;
    }
  }
}
