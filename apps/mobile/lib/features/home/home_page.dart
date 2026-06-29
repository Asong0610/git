import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../data/models/device.dart';
import '../../providers/device_provider.dart';

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
    });
  }

  @override
  Widget build(BuildContext context) {
    final deviceState = ref.watch(deviceListProvider);

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
