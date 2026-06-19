import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/models/device.dart';
import '../data/repositories/device_repository.dart';

// Device Repository Provider
final deviceRepositoryProvider = Provider<DeviceRepository>((ref) {
  return DeviceRepository();
});

// 设备列表状态
final deviceListProvider = StateNotifierProvider<DeviceListNotifier, DeviceListState>((ref) {
  return DeviceListNotifier(ref.watch(deviceRepositoryProvider));
});

class DeviceListState {
  final bool isLoading;
  final List<Device> devices;
  final String? error;
  
  DeviceListState({
    this.isLoading = false,
    this.devices = const [],
    this.error,
  });
  
  DeviceListState copyWith({
    bool? isLoading,
    List<Device>? devices,
    String? error,
  }) {
    return DeviceListState(
      isLoading: isLoading ?? this.isLoading,
      devices: devices ?? this.devices,
      error: error,
    );
  }
}

class DeviceListNotifier extends StateNotifier<DeviceListState> {
  final DeviceRepository _deviceRepository;
  
  DeviceListNotifier(this._deviceRepository) : super(DeviceListState());
  
  Future<void> loadDevices({String? category, String? status}) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final devices = await _deviceRepository.getDevices(
        category: category,
        status: status,
      );
      state = state.copyWith(isLoading: false, devices: devices);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }
}

// 设备详情
final deviceDetailProvider = FutureProvider.family<Device, String>((ref, deviceCode) async {
  final repository = ref.watch(deviceRepositoryProvider);
  return await repository.getDeviceByCode(deviceCode);
});
