import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../features/auth/login_page.dart';
import '../features/home/home_page.dart';
import '../features/scan/scan_page.dart';
import '../features/borrow/borrow_page.dart';
import '../features/profile/profile_page.dart';
import '../features/borrow/orders_page.dart';
import '../features/service/faq_page.dart';
import '../providers/auth_provider.dart';

final routerProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/',
    redirect: (context, state) {
      final authState = ref.read(authStateProvider);
      final isLoggedIn = authState.isLoggedIn;
      final isLoginRoute = state.matchedLocation == '/login';
      
      if (!isLoggedIn && !isLoginRoute) {
        return '/login';
      }
      if (isLoggedIn && isLoginRoute) {
        return '/';
      }
      return null;
    },
    routes: [
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginPage(),
      ),
      GoRoute(
        path: '/',
        builder: (context, state) => const HomePage(),
      ),
      GoRoute(
        path: '/scan',
        builder: (context, state) => const ScanPage(),
      ),
      GoRoute(
        path: '/borrow/:deviceCode',
        builder: (context, state) => BorrowPage(
          deviceCode: state.pathParameters['deviceCode']!,
        ),
      ),
      GoRoute(
        path: '/profile',
        builder: (context, state) => const ProfilePage(),
      ),
      GoRoute(
        path: '/orders',
        builder: (context, state) => const OrdersPage(),
      ),
      GoRoute(
        path: '/faq',
        builder: (context, state) => const FaqPage(),
      ),
    ],
  );
});
