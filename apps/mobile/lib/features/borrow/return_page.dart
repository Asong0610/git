import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../providers/borrow_provider.dart';

class ReturnPage extends ConsumerStatefulWidget {
  final String orderId;
  
  const ReturnPage({super.key, required this.orderId});

  @override
  ConsumerState<ReturnPage> createState() => _ReturnPageState();
}

class _ReturnPageState extends ConsumerState<ReturnPage> {
  bool _isReturning = false;

  Future<void> _returnDevice() async {
    setState(() => _isReturning = true);
    
    final result = await ref.read(currentOrderProvider.notifier).returnDevice(widget.orderId);

    if (result != null && mounted) {
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (context) => AlertDialog(
          title: const Row(
            children: [
              Icon(Icons.check_circle, color: Colors.green, size: 28),
              SizedBox(width: 8),
              Text('归还成功'),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildResultRow('实际使用', '${result['actual_hours']} 小时'),
              _buildResultRow('逾期费', '¥${result['overdue_fee']}'),
              _buildResultRow('总费用', '¥${result['total_fee']}'),
              _buildResultRow('退还押金', '¥${result['deposit_refund']}'),
            ],
          ),
          actions: [
            ElevatedButton(
              onPressed: () {
                Navigator.pop(context);
                context.go('/');
              },
              child: const Text('返回首页'),
            ),
          ],
        ),
      );
    } else if (mounted) {
      final error = ref.read(currentOrderProvider).error;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(error ?? '归还失败')),
      );
      setState(() => _isReturning = false);
    }
  }

  Widget _buildResultRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(color: Colors.grey.shade600)),
          Text(value, style: const TextStyle(fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('归还设备')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.assignment_return, size: 80, color: Colors.orange),
            const SizedBox(height: 24),
            const Text('确认归还设备？', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            const Text('系统将自动计算费用并退还押金', style: TextStyle(color: Colors.grey)),
            const SizedBox(height: 48),
            SizedBox(
              width: double.infinity,
              height: 48,
              child: ElevatedButton(
                onPressed: _isReturning ? null : _returnDevice,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.orange,
                  foregroundColor: Colors.white,
                ),
                child: _isReturning
                    ? const SizedBox(width: 24, height: 24, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                    : const Text('确认归还', style: TextStyle(fontSize: 16)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
