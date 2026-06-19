import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../data/models/device.dart';
import '../../providers/device_provider.dart';
import '../../providers/borrow_provider.dart';

class HomePage extends ConsumerStatefulWidget {
  const HomePage({super.key});

  @override
  ConsumerState<HomePage> createState() => _HomePageState();
}

class _HomePageState extends ConsumerState<HomePage> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      ref.read(deviceListProvider.notifier).loadDevices();
      ref.read(currentOrderProvider.notifier).loadCurrentOrder();
    });
  }

  @override
  Widget build(BuildContext context) {
    final deviceState = ref.watch(deviceListProvider);
    final orderState = ref.watch(currentOrderProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('校园共享设备'),
        actions: [
          IconButton(
            icon: const Icon(Icons.person),
            onPressed: () => context.push('/profile'),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () => ref.read(deviceListProvider.notifier).loadDevices(),
        child: Column(
          children: [
            // 当前订单卡片
            if (orderState.order != null)
              _buildCurrentOrderCard(orderState.order!),
            
            // 设备列表
            Expanded(
              child: deviceState.isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : deviceState.error != null
                      ? Center(child: Text('加载失败: ${deviceState.error}'))
                      : deviceState.devices.isEmpty
                          ? const Center(child: Text('暂无设备'))
                          : ListView.builder(
                              padding: const EdgeInsets.all(16),
                              itemCount: deviceState.devices.length,
                              itemBuilder: (context, index) {
                                return _buildDeviceCard(deviceState.devices[index]);
                              },
                            ),
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => context.push('/scan'),
        icon: const Icon(Icons.qr_code_scanner),
        label: const Text('扫码'),
      ),
    );
  }

  Widget _buildCurrentOrderCard(order) {
    return Card(
      margin: const EdgeInsets.all(16),
      color: Colors.orange.shade50,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.warning_amber, color: Colors.orange),
                const SizedBox(width: 8),
                const Text('当前借用中', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                const Spacer(),
                if (order.isOverdue)
                  const Chip(label: Text('已逾期'), backgroundColor: Colors.red, labelStyle: TextStyle(color: Colors.white)),
              ],
            ),
            const SizedBox(height: 8),
            Text('设备: ${order.deviceName}'),
            Text('应还时间: ${order.dueAt.toLocal().toString().substring(0, 16)}'),
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () => context.push('/borrow/return/${order.id}'),
                style: ElevatedButton.styleFrom(backgroundColor: Colors.orange),
                child: const Text('归还设备', style: TextStyle(color: Colors.white)),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDeviceCard(Device device) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: device.isAvailable ? Colors.green : Colors.grey,
          child: Icon(
            device.category == '充电宝' ? Icons.battery_charging_full :
            device.category == '相机' ? Icons.camera_alt :
            device.category == '平板' ? Icons.tablet :
            Icons.devices,
            color: Colors.white,
          ),
        ),
        title: Text(device.name),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('位置: ${device.location ?? '未知'}'),
            Text('费率: ¥${device.hourlyRate}/小时'),
          ],
        ),
        trailing: Chip(
          label: Text(device.isAvailable ? '可借' : '已借出'),
          backgroundColor: device.isAvailable ? Colors.green.shade100 : Colors.grey.shade300,
        ),
        onTap: device.isAvailable
            ? () => context.push('/borrow/${device.deviceCode}')
            : null,
      ),
    );
  }
}
