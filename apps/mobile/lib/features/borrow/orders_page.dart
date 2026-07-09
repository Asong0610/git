import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../data/api/api_client.dart';
import 'package:uuid/uuid.dart';

class OrdersPage extends ConsumerStatefulWidget {
  const OrdersPage({super.key});

  @override
  ConsumerState<OrdersPage> createState() => _OrdersPageState();
}

class _OrdersPageState extends ConsumerState<OrdersPage> {
  final _api = ApiClient();
  List<OrderItem> _orders = [];
  bool _loading = true;
  String? _error;
  int _total = 0;
  final int _page = 1;
  final Map<String, bool> _returningOrders = {};
  final _uuid = const Uuid();

  @override
  void initState() {
    super.initState();
    _loadOrders();
  }

  Future<void> _loadOrders() async {
    setState(() { _loading = true; _error = null; });
    try {
      final resp = await _api.get('/borrows', queryParameters: {'page': _page, 'page_size': 20});
      final items = resp.data['items'] as List;
      setState(() {
        _orders = items.map((e) => OrderItem.fromJson(e)).toList();
        _total = resp.data['total'] as int;
        _loading = false;
      });
    } catch (e) {
      setState(() { _error = e.toString(); _loading = false; });
    }
  }


  Future<void> _reportFault(OrderItem order) async {
    final controller = TextEditingController();
    bool submitting = false;

    await showDialog(
      context: context,
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setDialogState) {
            return AlertDialog(
              title: const Row(
                children: [
                  Icon(Icons.report_problem, color: Colors.orange, size: 28),
                  SizedBox(width: 8),
                  Text('故障报修'),
                ],
              ),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _infoRow('设备', order.deviceName),
                  const SizedBox(height: 12),
                  TextField(
                    controller: controller,
                    maxLines: 4,
                    maxLength: 500,
                    decoration: const InputDecoration(
                      hintText: '请描述设备故障情况（1~500字）',
                      border: OutlineInputBorder(),
                    ),
                  ),
                ],
              ),
              actions: [
                TextButton(
                  onPressed: submitting ? null : () => Navigator.pop(context),
                  child: const Text('取消'),
                ),
                ElevatedButton(
                  onPressed: submitting
                      ? null
                      : () async {
                          final description = controller.text.trim();
                          if (description.isEmpty) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(content: Text('请填写故障描述')),
                            );
                            return;
                          }
                          if (description.length > 500) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(content: Text('故障描述不能超过500字')),
                            );
                            return;
                          }
                          setDialogState(() => submitting = true);
                          try {
                            await _api.post('/faults', data: {
                              'device_id': order.deviceId,
                              'description': description,
                            });
                            if (!mounted) return;
                            Navigator.pop(context);
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(content: Text('工单已提交，管理员将尽快处理')),
                            );
                          } catch (e) {
                            setDialogState(() => submitting = false);
                            if (!mounted) return;
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(content: Text('提交失败：${e.toString()}')),
                            );
                          }
                        },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.orange,
                    foregroundColor: Colors.white,
                  ),
                  child: submitting
                      ? const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                        )
                      : const Text('提交工单'),
                ),
              ],
            );
          },
        );
      },
    );

    controller.dispose();
  }

  Future<void> _returnOrder(OrderItem order) async {
    final confirmed = await showDialog<bool>(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.warning_amber, color: Colors.orange, size: 28),
            SizedBox(width: 8),
            Text('确认归还'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('设备：${order.deviceName}', style: const TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            const Text('归还后将自动计算费用并退还押金。'),
            const SizedBox(height: 12),
            const Text('确定继续？', style: TextStyle(color: Colors.grey)),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('取消'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.orange,
              foregroundColor: Colors.white,
            ),
            child: const Text('确认归还'),
          ),
        ],
      ),
    );

    if (confirmed != true || !mounted) return;

    setState(() { _returningOrders[order.id] = true; });

    try {
      final response = await _api.post('/borrows/${order.id}/return', data: {
        'idempotency_key': _uuid.v4(),
      });

      if (response.statusCode == 200 && mounted) {
        final result = response.data;
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
                _buildResultRow('使用费', '¥${result['usage_fee']}'),
                _buildResultRow('总费用', '¥${result['total_fee']}'),
                _buildResultRow('退还押金', '¥${result['deposit_refund']}'),
              ],
            ),
            actions: [
              ElevatedButton(
                onPressed: () {
                  Navigator.pop(context);
                  _loadOrders();
                },
                child: const Text('确定'),
              ),
            ],
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('归还失败：${e.toString()}')),
        );
      }
    } finally {
      if (mounted) {
        setState(() { _returningOrders.remove(order.id); });
      }
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
      appBar: AppBar(title: const Text('我的订单')),
      body: RefreshIndicator(
        onRefresh: _loadOrders,
        child: _loading
            ? const Center(child: CircularProgressIndicator())
            : _error != null
                ? Center(child: Column(mainAxisSize: MainAxisSize.min, children: [
                    Text('加载失败: $_error'),
                    const SizedBox(height: 16),
                    ElevatedButton(onPressed: _loadOrders, child: const Text('重试')),
                  ]))
                : _orders.isEmpty
                    ? ListView(children: const [SizedBox(height: 200), Center(child: Text('暂无订单', style: TextStyle(fontSize: 16, color: Colors.grey)))])
                    : ListView.builder(
                        itemCount: _orders.length + 1,
                        itemBuilder: (ctx, i) {
                          if (i == _orders.length) {
                            return Padding(padding: const EdgeInsets.all(16), child: Center(child: Text('共 $_total 条记录', style: TextStyle(color: Colors.grey.shade500))));
                          }
                          return _buildOrderCard(_orders[i]);
                        },
                      ),
      ),
    );
  }

  Widget _buildOrderCard(OrderItem order) {
    final dateFormat = DateFormat('MM-dd HH:mm');
    final statusColor = switch (order.status) {
      'active' => Colors.blue,
      'returned' => Colors.green,
      'cancelled' => Colors.grey,
      _ => Colors.grey,
    };
    final statusLabel = switch (order.status) {
      'active' => '借用中',
      'returned' => '已归还',
      'cancelled' => '已取消',
      _ => order.status,
    };

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.devices, color: statusColor, size: 20),
                const SizedBox(width: 8),
                Expanded(child: Text(order.deviceName, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16))),
                Chip(
                  label: Text(statusLabel, style: TextStyle(color: statusColor, fontSize: 12)),
                  backgroundColor: statusColor.withOpacity(0.1),
                  padding: EdgeInsets.zero,
                ),
              ],
            ),
            const SizedBox(height: 12),
            _infoRow('设备码', order.deviceCode),
            _infoRow('借出时间', dateFormat.format(order.borrowedAt)),
            _infoRow('免费截止', dateFormat.format(order.dueAt)),
            if (order.returnedAt != null)
              _infoRow('归还时间', dateFormat.format(order.returnedAt!)),
            if (order.usageFee != '0.00' && order.usageFee != '0')
              Padding(
                padding: const EdgeInsets.only(top: 4),
                child: _infoRow('使用费', '¥${order.usageFee}', valueColor: Colors.red),
              ),

            if (order.status == 'active') ...[
              const SizedBox(height: 12),
              const Divider(height: 1),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: SizedBox(
                      height: 40,
                      child: OutlinedButton.icon(
                        onPressed: () => _reportFault(order),
                        style: OutlinedButton.styleFrom(
                          foregroundColor: Colors.orange,
                          side: const BorderSide(color: Colors.orange),
                        ),
                        icon: const Icon(Icons.report_problem, size: 18),
                        label: const Text('故障报修'),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: SizedBox(
                      height: 40,
                      child: ElevatedButton.icon(
                        onPressed: _returningOrders[order.id] == true ? null : () => _returnOrder(order),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.orange,
                          foregroundColor: Colors.white,
                        ),
                        icon: _returningOrders[order.id] == true
                            ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                            : const Icon(Icons.assignment_return, size: 18),
                        label: Text(_returningOrders[order.id] == true ? '归还中...' : '确认归还'),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _infoRow(String label, String value, {Color? valueColor}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(color: Colors.grey.shade600, fontSize: 13)),
          Text(value, style: TextStyle(fontWeight: FontWeight.w500, color: valueColor, fontSize: 13)),
        ],
      ),
    );
  }
}

class OrderItem {
  final String id;
  final String deviceId;
  final String deviceCode;
  final String deviceName;
  final String status;
  final DateTime borrowedAt;
  final DateTime dueAt;
  final DateTime? returnedAt;
  final String usageFee;

  OrderItem({
    required this.id,
    required this.deviceId,
    required this.deviceCode,
    required this.deviceName,
    required this.status,
    required this.borrowedAt,
    required this.dueAt,
    this.returnedAt,
    required this.usageFee,
  });

  factory OrderItem.fromJson(Map<String, dynamic> json) {
    return OrderItem(
      id: json['id'] as String,
      deviceId: json['device_id'] as String,
      deviceCode: json['device_code'] as String,
      deviceName: json['device_name'] as String,
      status: json['status'] as String,
      borrowedAt: DateTime.parse(json['borrowed_at'] as String),
      dueAt: DateTime.parse(json['due_at'] as String),
      returnedAt: json['returned_at'] != null ? DateTime.parse(json['returned_at'] as String) : null,
      usageFee: json['usage_fee'] as String,
    );
  }
}
