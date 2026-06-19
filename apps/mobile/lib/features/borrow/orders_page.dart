import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../data/api/api_client.dart';

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
  final String deviceCode;
  final String deviceName;
  final String status;
  final DateTime borrowedAt;
  final DateTime dueAt;
  final DateTime? returnedAt;
  final String usageFee;

  OrderItem({
    required this.id,
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
