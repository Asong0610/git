import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../core/constants.dart';

class ApiClient {
  static final ApiClient _instance = ApiClient._internal();
  factory ApiClient() => _instance;
  
  late Dio _dio;
  
  ApiClient._internal() {
    _dio = Dio(BaseOptions(
      baseUrl: ApiConstants.baseUrl,
      connectTimeout: ApiConstants.connectTimeout,
      receiveTimeout: ApiConstants.receiveTimeout,
      headers: {
        'Content-Type': 'application/json',
      },
    ));
    
    // 添加拦截器
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        // 添加 Token
        final prefs = await SharedPreferences.getInstance();
        final token = prefs.getString(StorageKeys.accessToken);
        if (token != null && token.isNotEmpty) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        return handler.next(options);
      },
      onResponse: (response, handler) {
        return handler.next(response);
      },
      onError: (error, handler) async {
        // 处理 401 错误（Token 过期）
        if (error.response?.statusCode == 401) {
          // 尝试刷新 Token
          final refreshed = await _refreshToken();
          if (refreshed) {
            // 重试原请求
            final prefs = await SharedPreferences.getInstance();
            final newToken = prefs.getString(StorageKeys.accessToken);
            error.requestOptions.headers['Authorization'] = 'Bearer $newToken';
            final response = await _dio.fetch(error.requestOptions);
            return handler.resolve(response);
          }
        }
        return handler.next(error);
      },
    ));
  }
  
  Future<bool> _refreshToken() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final refreshToken = prefs.getString(StorageKeys.refreshToken);
      if (refreshToken == null || refreshToken.isEmpty) {
        return false;
      }
      
      final response = await _dio.post('/auth/refresh', data: {
        'refresh_token': refreshToken,
      });
      
      if (response.statusCode == 200) {
        final data = response.data;
        await prefs.setString(StorageKeys.accessToken, data['access_token']);
        await prefs.setString(StorageKeys.refreshToken, data['refresh_token']);
        return true;
      }
      return false;
    } catch (e) {
      return false;
    }
  }
  
  // GET 请求
  Future<Response> get(String path, {Map<String, dynamic>? queryParameters}) async {
    return await _dio.get(path, queryParameters: queryParameters);
  }
  
  // POST 请求
  Future<Response> post(String path, {dynamic data}) async {
    return await _dio.post(path, data: data);
  }
  
  // PATCH 请求
  Future<Response> patch(String path, {dynamic data}) async {
    return await _dio.patch(path, data: data);
  }
  
  // PUT 请求
  Future<Response> put(String path, {dynamic data}) async {
    return await _dio.put(path, data: data);
  }
  
  // DELETE 请求
  Future<Response> delete(String path) async {
    return await _dio.delete(path);
  }
}
