import 'package:shared_preferences/shared_preferences.dart';
import '../api/api_client.dart';
import '../models/user.dart';
import '../../core/constants.dart';

class AuthRepository {
  final ApiClient _api = ApiClient();
  
  // 发送验证码
  Future<String?> sendSmsCode(String phone) async {
    try {
      final response = await _api.post('/auth/sms-code', data: {'phone': phone});
      if (response.statusCode == 200) {
        return response.data['debug_code'] as String?;
      }
      return null;
    } catch (e) {
      rethrow;
    }
  }
  
  // 登录
  Future<User> login(String phone, String smsCode) async {
    try {
      final response = await _api.post('/auth/login', data: {
        'phone': phone,
        'sms_code': smsCode,
      });
      
      if (response.statusCode == 200) {
        final data = response.data;
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString(StorageKeys.accessToken, data['access_token']);
        await prefs.setString(StorageKeys.refreshToken, data['refresh_token']);
        
        // 获取用户信息
        return await getProfile();
      }
      throw Exception('登录失败');
    } catch (e) {
      rethrow;
    }
  }
  
  // 获取用户信息
  Future<User> getProfile() async {
    try {
      final response = await _api.get('/users/me');
      if (response.statusCode == 200) {
        final user = User.fromJson(response.data);
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString(StorageKeys.userId, user.id);
        await prefs.setString(StorageKeys.phone, user.phone);
        return user;
      }
      throw Exception('获取用户信息失败');
    } catch (e) {
      rethrow;
    }
  }
  
  // 更新昵称
  Future<User> updateNickname(String nickname) async {
    try {
      final response = await _api.patch('/users/me', data: {'nickname': nickname});
      if (response.statusCode == 200) {
        return User.fromJson(response.data);
      }
      throw Exception('更新失败');
    } catch (e) {
      rethrow;
    }
  }
  
  // 押金充值
  Future<User> topUpDeposit(String amount) async {
    try {
      final response = await _api.post('/users/me/deposit/topup', data: {'amount': amount});
      if (response.statusCode == 200) {
        return User.fromJson(response.data);
      }
      throw Exception('充值失败');
    } catch (e) {
      rethrow;
    }
  }
  
  // 登出
  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(StorageKeys.accessToken);
    await prefs.remove(StorageKeys.refreshToken);
    await prefs.remove(StorageKeys.userId);
    await prefs.remove(StorageKeys.phone);
  }
  
  // 检查是否已登录
  Future<bool> isLoggedIn() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString(StorageKeys.accessToken);
    return token != null && token.isNotEmpty;
  }
}
