class BorrowOrder {
  final String id;
  final String deviceCode;
  final String deviceName;
  final DateTime borrowedAt;
  final DateTime dueAt;
  final String depositFrozen;
  
  BorrowOrder({
    required this.id,
    required this.deviceCode,
    required this.deviceName,
    required this.borrowedAt,
    required this.dueAt,
    required this.depositFrozen,
  });
  
  factory BorrowOrder.fromJson(Map<String, dynamic> json) {
    return BorrowOrder(
      id: json['id'] as String,
      deviceCode: json['device_code'] as String,
      deviceName: json['device_name'] as String,
      borrowedAt: DateTime.parse(json['borrowed_at'] as String),
      dueAt: DateTime.parse(json['due_at'] as String),
      depositFrozen: json['deposit_frozen'] as String,
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'device_code': deviceCode,
      'device_name': deviceName,
      'borrowed_at': borrowedAt.toIso8601String(),
      'due_at': dueAt.toIso8601String(),
      'deposit_frozen': depositFrozen,
    };
  }
  
  bool get isOverdue => DateTime.now().isAfter(dueAt);
  
  Duration get remainingTime => dueAt.difference(DateTime.now());
}
