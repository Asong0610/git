import 'package:flutter/material.dart';

class FaqPage extends StatefulWidget {
  const FaqPage({super.key});

  @override
  State<FaqPage> createState() => _FaqPageState();
}

class _FaqPageState extends State<FaqPage> {
  int? _expandedIndex;

  final List<Map<String, String>> _faqs = [
    {"q": "如何借设备？", "a": "在首页找到可借用的设备，点击进入详情页，确认借出即可。或者使用底部扫码按钮，扫描设备上的二维码快速借出。"},
    {"q": "如何归还？", "a": "在首页顶部卡片中点击「归还设备」按钮，确认归还后系统会自动结算费用。"},
    {"q": "收费规则是什么？", "a": "每次借用前 5 分钟免费。超出后按整小时计费，不足 1 小时按 1 小时计算。具体费率见设备详情页。"},
    {"q": "押金怎么退？", "a": "归还设备时系统会自动结算费用。如果无使用费，押金全额退还；有使用费时从押金中扣除后退还。"},
    {"q": "押金不够怎么办？", "a": "在「个人中心」页面可以充值押金。押金根据设备类型固定收取，不同设备押金不同。"},
    {"q": "设备损坏怎么办？", "a": "请立即停止使用并联系管理员。故意损坏设备需要按价赔偿。建议借用前检查设备状态。"},
    {"q": "可以提前归还吗？", "a": "当然。你可以随时归还设备。5 分钟内归还不收费，超出按实际使用时长计费。"},
    {"q": "如何联系管理员？", "a": "电话: 138-0000-0000（工作日 9:00-18:00）。也可到图书馆一楼服务台咨询。"},
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('帮助与客服')),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _faqs.length,
              itemBuilder: (context, index) {
                final faq = _faqs[index];
                final isExpanded = _expandedIndex == index;
                return Card(
                  margin: const EdgeInsets.only(bottom: 8),
                  child: Column(
                    children: [
                      ListTile(
                        title: Text(faq['q']!, style: const TextStyle(fontWeight: FontWeight.w500)),
                        trailing: Icon(isExpanded ? Icons.expand_less : Icons.expand_more),
                        onTap: () => setState(() {
                          _expandedIndex = isExpanded ? null : index;
                        }),
                      ),
                      if (isExpanded)
                        Padding(
                          padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                          child: Text(faq['a']!, style: TextStyle(color: Colors.grey.shade600)),
                        ),
                    ],
                  ),
                );
              },
            ),
          ),
          // 底部联系区域
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.grey.shade50,
              border: Border(top: BorderSide(color: Colors.grey.shade200)),
            ),
            child: SafeArea(
              child: Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () {}, // 可替换为拨号
                      icon: const Icon(Icons.phone, color: Colors.white),
                      label: const Text('联系客服 138-0000-0000', style: TextStyle(color: Colors.white)),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.blue,
                        padding: const EdgeInsets.symmetric(vertical: 12),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
