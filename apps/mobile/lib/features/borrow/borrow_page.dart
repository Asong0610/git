import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../data/models/device.dart';
import '../../providers/device_provider.dart';
import '../../providers/borrow_provider.dart';

class BorrowPage extends ConsumerStatefulWidget {
  final String deviceCode;
  
  const BorrowPage({super.key, required this.deviceCode});

  @override
  ConsumerState<BorrowPage> createState() => _BorrowPageState();
}

class _BorrowPageState extends ConsumerState<BorrowPage> {
  int _durationHours = 2;

  Future<void> _borrowDevice() async {
    final success = await ref.read(currentOrderProvider.notifier).borrowDevice(
      widget.deviceCode,
      _durationHours,
    );

    if (success && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('借出成功')),
      );
      context.go('/');
    } else if (mounted) {
      final error = ref.read(currentOrderProvider).error;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(error ?? '借出失败')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final deviceAsync = ref.watch(deviceDetailProvider(widget.deviceCode));
    final borrowState = ref.watch(currentOrderProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('借出设备')),
      body: deviceAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('设备不存在或加载失败')),
        data: (device) => _buildContent(device, borrowState),
      ),
    );
  }

  Widget _buildContent(Device device, state) {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 设备信息卡片
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      CircleAvatar(
                        radius: 30,
                        backgroundColor: Colors.blue.shade100,
                        child: Icon(Icons.devices, size: 30, color: Colors.blue.shade700),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(device.name, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                            const SizedBox(height: 4),
                            Text('设备码: ${device.deviceCode}', style: TextStyle(color: Colors.grey.shade600)),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const Divider(height: 24),
                  _buildInfoRow('位置', device.location ?? '未知'),
                  _buildInfoRow('分类', device.category ?? '未分类'),
                  _buildInfoRow('费率', '¥${device.hourlyRate}/小时'),
                  _buildInfoRow('状态', device.isAvailable ? '可借' : '已借出'),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),
          
          // 借用时长选择
          const Text('选择借用时长', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          Row(
            children: [1, 2, 4, 8, 12, 24].map((hours) {
              final selected = _durationHours == hours;
              return Expanded(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 4),
                  child: ChoiceChip(
                    label: Text('${hours}h'),
                    selected: selected,
                    onSelected: (_) => setState(() => _durationHours = hours),
                    selectedColor: Colors.blue.shade100,
                  ),
                ),
              );
            }).toList(),
          ),
          const SizedBox(height: 16),
          
          // 费用预估
          Card(
            color: Colors.blue.shade50,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  _buildEstimateRow('预估费用', '¥${(double.parse(device.hourlyRate) * _durationHours).toStringAsFixed(2)}'),
                  _buildEstimateRow('需冻结押金', '¥${(double.parse(device.hourlyRate) * _durationHours * 2).toStringAsFixed(2)}'),
                  const SizedBox(height: 8),
                  const Text('按时长计费，逾期按整小时向上取整', style: TextStyle(fontSize: 12, color: Colors.grey)),
                ],
              ),
            ),
          ),
          const Spacer(),
          
          // 借出按钮
          SizedBox(
            width: double.infinity,
            height: 48,
            child: ElevatedButton(
              onPressed: device.isAvailable && !state.isLoading ? _borrowDevice : null,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue,
                foregroundColor: Colors.white,
              ),
              child: state.isLoading
                  ? const SizedBox(width: 24, height: 24, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                  : const Text('确认借出', style: TextStyle(fontSize: 16)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          SizedBox(width: 80, child: Text(label, style: TextStyle(color: Colors.grey.shade600))),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }

  Widget _buildEstimateRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(color: Colors.grey.shade700)),
          Text(value, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
        ],
      ),
    );
  }
}
