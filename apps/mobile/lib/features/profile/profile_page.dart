import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../providers/auth_provider.dart';

class ProfilePage extends ConsumerStatefulWidget {
  const ProfilePage({super.key});

  @override
  ConsumerState<ProfilePage> createState() => _ProfilePageState();
}

class _ProfilePageState extends ConsumerState<ProfilePage> {
  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authStateProvider);
    final user = authState.user;

    return Scaffold(
      appBar: AppBar(title: const Text('个人中心')),
      body: user == null
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                // 用户信息卡片
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      children: [
                        CircleAvatar(
                          radius: 40,
                          backgroundColor: Colors.blue.shade100,
                          child: Text(
                            (user.nickname ?? user.phone).substring(0, 1),
                            style: TextStyle(fontSize: 32, color: Colors.blue.shade700),
                          ),
                        ),
                        const SizedBox(height: 12),
                        Text(user.nickname ?? '未设置昵称', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                        const SizedBox(height: 4),
                        Text(user.phone, style: TextStyle(color: Colors.grey.shade600)),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                
                // 押金信息
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('押金余额', style: TextStyle(fontSize: 14, color: Colors.grey)),
                        const SizedBox(height: 8),
                        Row(
                          children: [
                            Text('¥${user.depositBalance}', style: const TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: Colors.green)),
                            const Spacer(),
                            ElevatedButton.icon(
                              onPressed: () => _showTopUpDialog(),
                              icon: const Icon(Icons.add),
                              label: const Text('充值'),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                
                // 功能列表
                Card(
                  child: Column(
                    children: [
                      ListTile(
                        leading: const Icon(Icons.edit),
                        title: const Text('修改昵称'),
                        trailing: const Icon(Icons.chevron_right),
                        onTap: () => _showEditNicknameDialog(),
                      ),
                      const Divider(height: 1),
                      ListTile(
                        leading: const Icon(Icons.receipt_long),
                        title: const Text('我的订单'),
                        trailing: const Icon(Icons.chevron_right),
                        onTap: () {
                          // TODO: 跳转到订单列表
                        },
                      ),
                      const Divider(height: 1),
                      ListTile(
                        leading: const Icon(Icons.account_balance_wallet),
                        title: const Text('押金流水'),
                        trailing: const Icon(Icons.chevron_right),
                        onTap: () {
                          // TODO: 跳转到押金流水
                        },
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
                
                // 退出登录
                SizedBox(
                  width: double.infinity,
                  child: OutlinedButton.icon(
                    onPressed: () async {
                      final confirm = await showDialog<bool>(
                        context: context,
                        builder: (context) => AlertDialog(
                          title: const Text('退出登录'),
                          content: const Text('确定要退出登录吗？'),
                          actions: [
                            TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('取消')),
                            TextButton(onPressed: () => Navigator.pop(context, true), child: const Text('确定')),
                          ],
                        ),
                      );
                      if (confirm == true) {
                        await ref.read(authStateProvider.notifier).logout();
                        if (mounted) context.go('/login');
                      }
                    },
                    icon: const Icon(Icons.logout, color: Colors.red),
                    label: const Text('退出登录', style: TextStyle(color: Colors.red)),
                  ),
                ),
              ],
            ),
    );
  }

  void _showTopUpDialog() {
    final amounts = ['100', '200', '500', '1000'];
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('押金充值'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: amounts.map((amount) {
            return ListTile(
              title: Text('¥$amount'),
              trailing: const Icon(Icons.arrow_forward),
              onTap: () async {
                Navigator.pop(context);
                final success = await ref.read(authStateProvider.notifier).topUpDeposit(amount);
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text(success ? '充值成功' : '充值失败')),
                  );
                }
              },
            );
          }).toList(),
        ),
      ),
    );
  }

  void _showEditNicknameDialog() {
    final controller = TextEditingController(text: ref.read(authStateProvider).user?.nickname ?? '');
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('修改昵称'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(labelText: '昵称'),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('取消')),
          TextButton(
            onPressed: () async {
              Navigator.pop(context);
              final nickname = controller.text.trim();
              if (nickname.isNotEmpty) {
                final success = await ref.read(authStateProvider.notifier).updateNickname(nickname);
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text(success ? '修改成功' : '修改失败')),
                  );
                }
              }
            },
            child: const Text('确定'),
          ),
        ],
      ),
    );
  }
}
