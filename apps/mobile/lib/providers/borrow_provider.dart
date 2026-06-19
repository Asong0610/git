import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/models/borrow_order.dart';
import '../data/repositories/borrow_repository.dart';

// Borrow Repository Provider
final borrowRepositoryProvider = Provider<BorrowRepository>((ref) {
  return BorrowRepository();
});

// 当前订单状态
final currentOrderProvider = StateNotifierProvider<CurrentOrderNotifier, CurrentOrderState>((ref) {
  return CurrentOrderNotifier(ref.watch(borrowRepositoryProvider));
});

class CurrentOrderState {
  final bool isLoading;
  final BorrowOrder? order;
  final String? error;
  
  CurrentOrderState({
    this.isLoading = false,
    this.order,
    this.error,
  });
  
  CurrentOrderState copyWith({
    bool? isLoading,
    BorrowOrder? order,
    String? error,
  }) {
    return CurrentOrderState(
      isLoading: isLoading ?? this.isLoading,
      order: order ?? this.order,
      error: error,
    );
  }
}

class CurrentOrderNotifier extends StateNotifier<CurrentOrderState> {
  final BorrowRepository _borrowRepository;
  
  CurrentOrderNotifier(this._borrowRepository) : super(CurrentOrderState());
  
  Future<void> loadCurrentOrder() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final order = await _borrowRepository.getCurrentOrder();
      state = state.copyWith(isLoading: false, order: order);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }
  
  Future<bool> borrowDevice(String deviceCode) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final order = await _borrowRepository.borrowDevice(deviceCode);
      state = state.copyWith(isLoading: false, order: order);
      return true;
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
      return false;
    }
  }
  
  Future<Map<String, dynamic>?> returnDevice(String orderId) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final result = await _borrowRepository.returnDevice(orderId);
      state = CurrentOrderState(); // 清空当前订单
      return result;
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
      return null;
    }
  }
  
  void clearOrder() {
    state = CurrentOrderState();
  }
}
