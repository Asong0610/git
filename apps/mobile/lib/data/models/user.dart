class User {
  final String id;
  final String phone;
  final String? nickname;
  final String depositBalance;
  final String role;
  final String status;
  
  User({
    required this.id,
    required this.phone,
    this.nickname,
    required this.depositBalance,
    required this.role,
    required this.status,
  });
  
  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as String,
      phone: json['phone'] as String,
      nickname: json['nickname'] as String?,
      depositBalance: json['deposit_balance'] as String,
      role: json['role'] as String,
      status: json['status'] as String,
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'phone': phone,
      'nickname': nickname,
      'deposit_balance': depositBalance,
      'role': role,
      'status': status,
    };
  }
}
