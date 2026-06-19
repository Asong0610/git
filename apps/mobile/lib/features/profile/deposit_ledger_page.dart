import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../data/api/api_client.dart';

class DepositLedgerPage extends ConsumerStatefulWidget {
  const DepositLedgerPage({super.key});

  @override
  ConsumerState<DepositLedgerPage> createState() => _DepositLedgerPageState();
}

class _DepositLedgerPageState extends ConsumerState<DepositLedgerPage> {
  final _api = ApiClient();
  List<LedgerEntry> _entries = [];
  bool _loading = true;
  String? _error;
  int _total = 0;

  @override
  void initState() {
    super.initState();
    _loadLedger();
  }

  Future<void> _loadLedger() async {
    setState(() { _loading = true; _error = null; });
    try {
      final resp = await _api.get('/users/me/deposit/ledger', queryParameters: {'page': 1, 'page_size': 50});
      final items = resp.data['items'] as List;
      setState(() {
        _entries = items.map((e) => LedgerEntry.fromJson(e)).toList();
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
      appBar: AppBar(title: const Text('押金流水')),
      body: RefreshIndicator(
        onRefresh: _loadLedger,
        child: _loading
            ? const Center(child: CircularProgressIndicator())
            : _error != null
                ? Center(child: Column(mainAxisSize: MainAxisSize.min, children: [
                    Text('加载失败: $_error'),
                    const SizedBox(height: 16),
                    ElevatedButton(onPressed: _loadLedger, child: const Text('重试')),
                  ]))
                : _entries.isEmpty
                    ? ListView(children: const [SizedBox(height: 200), Center(child: Text('暂无流水记录', style: TextStyle(fontSize: 16, color: Colors.grey)))])
                    : ListView.builder(
                        itemCount: _entries.length + 1,
                        itemBuilder: (ctx, i) {
                          if (i == _entries.length) {
                            return Padding(padding: const EdgeInsets.all(16), child: Center(child: Text('共 $_total 条记录', style: TextStyle(color: Colors.grey.shade500))));
                          }
                          return _buildLedgerCard(_entries[i]);
                        },
                      ),
      ),
    );
  }

  Widget _buildLedgerCard(LedgerEntry entry) {
    final dateFormat = DateFormat('yyyy-MM-dd HH:mm');
    final isPositive = !entry.amount.startsWith('-');
    final icon = switch (entry.entryType) {
      'topup' => Icons.arrow_downward,
      'freeze' => Icons.lock,
      'refund' => Icons.arrow_upward,
      'adjust' => Icons.tune,
      _ => Icons.swap_horiz,
    };
    final label = switch (entry.entryType) {
      'topup' => '押金充值',
      'freeze' => '借出冻结',
      'refund' => '归还退还',
      'adjust' => '管理员调账',
      _ => entry.entryType,
    };
    final iconColor = switch (entry.entryType) {
      'topup' => Colors.green,
      'freeze' => Colors.orange,
      'refund' => Colors.blue,
      'adjust' => Colors.purple,
      _ => Colors.grey,
    };

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: iconColor.withOpacity(0.1),
          child: Icon(icon, color: iconColor, size: 20),
        ),
        title: Text(label, style: const TextStyle(fontWeight: FontWeight.w500)),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(dateFormat.format(entry.createdAt), style: TextStyle(color: Colors.grey.shade500, fontSize: 12)),
            if (entry.remark != null && entry.remark!.isNotEmpty)
              Text(entry.remark!, style: TextStyle(color: Colors.grey.shade500, fontSize: 12)),
          ],
        ),
        trailing: Column(
          crossAxisAlignment: CrossAxisAlignment.end,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              '${isPositive ? "+" : ""}¥${entry.amount}',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 15,
                color: isPositive ? Colors.green : Colors.red,
              ),
            ),
            Text('余额: ¥${entry.balanceAfter}', style: TextStyle(color: Colors.grey.shade500, fontSize: 12)),
          ],
        ),
      ),
    );
  }
}

class LedgerEntry {
  final String id;
  final String entryType;
  final String amount;
  final String balanceAfter;
  final String? remark;
  final DateTime createdAt;

  LedgerEntry({
    required this.id,
    required this.entryType,
    required this.amount,
    required this.balanceAfter,
    this.remark,
    required this.createdAt,
  });

  factory LedgerEntry.fromJson(Map<String, dynamic> json) {
    return LedgerEntry(
      id: json['id'] as String,
      entryType: json['entry_type'] as String,
      amount: json['amount'] as String,
      balanceAfter: json['balance_after'] as String,
      remark: json['remark'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }
}
