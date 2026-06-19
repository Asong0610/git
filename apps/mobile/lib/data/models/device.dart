class Device {
  final String id;
  final String deviceCode;
  final String name;
  final String? category;
  final String? location;
  final String hourlyRate;
  final String status;
  
  Device({
    required this.id,
    required this.deviceCode,
    required this.name,
    this.category,
    this.location,
    required this.hourlyRate,
    required this.status,
  });
  
  factory Device.fromJson(Map<String, dynamic> json) {
    return Device(
      id: json['id'] as String,
      deviceCode: json['device_code'] as String,
      name: json['name'] as String,
      category: json['category'] as String?,
      location: json['location'] as String?,
      hourlyRate: json['hourly_rate'] as String,
      status: json['status'] as String,
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'device_code': deviceCode,
      'name': name,
      'category': category,
      'location': location,
      'hourly_rate': hourlyRate,
      'status': status,
    };
  }
  
  bool get isAvailable => status == 'available';
}
