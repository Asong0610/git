import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/models/user.dart';
import '../data/repositories/auth_repository.dart';

// Auth Repository Provider
final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepository();
});

// 当前用户状态
final authStateProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(ref.watch(authRepositoryProvider));
});

class AuthState {
  final bool isLoading;
  final bool isLoggedIn;
  final User? user;
  final String? error;
  
  AuthState({
    this.isLoading = false,
    this.isLoggedIn = false,
    this.user,
    this.error,
  });
  
  AuthState copyWith({
    bool? isLoading,
    bool? isLoggedIn,
    User? user,
    String? error,
  }) {
    return AuthState(
      isLoading: isLoading ?? this.isLoading,
      isLoggedIn: isLoggedIn ?? this.isLoggedIn,
      user: user ?? this.user,
      error: error,
    );
  }
}

class AuthNotifier extends StateNotifier<AuthState> {
  final AuthRepository _authRepository;
  
  AuthNotifier(this._authRepository) : super(AuthState());
  
  Future<void> checkAuthStatus() async {
    final isLoggedIn = await _authRepository.isLoggedIn();
    if (isLoggedIn) {
      state = state.copyWith(isLoggedIn: true, isLoading: true);
      try {
        final user = await _authRepository.getProfile();
        state = state.copyWith(isLoggedIn: true, isLoading: false, user: user);
      } catch (e) {
        state = state.copyWith(isLoggedIn: false, isLoading: false);
      }
    } else {
      state = state.copyWith(isLoggedIn: false, isLoading: false);
    }
  }
  
  Future<String?> sendSmsCode(String phone) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final debugCode = await _authRepository.sendSmsCode(phone);
      state = state.copyWith(isLoading: false);
      return debugCode;
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
      return null;
    }
  }
  
  Future<bool> login(String phone, String smsCode) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final user = await _authRepository.login(phone, smsCode);
      state = state.copyWith(isLoggedIn: true, isLoading: false, user: user);
      return true;
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
      return false;
    }
  }
  
  Future<void> logout() async {
    await _authRepository.logout();
    state = AuthState();
  }
  
  Future<bool> updateNickname(String nickname) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final user = await _authRepository.updateNickname(nickname);
      state = state.copyWith(isLoading: false, user: user);
      return true;
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
      return false;
    }
  }
  
  Future<bool> topUpDeposit(String amount) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final user = await _authRepository.topUpDeposit(amount);
      state = state.copyWith(isLoading: false, user: user);
      return true;
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
      return false;
    }
  }
}
