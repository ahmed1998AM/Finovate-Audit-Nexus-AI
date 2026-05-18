"""
Finovate Audit Nexus AI - Financial Graph Intelligence Agent
وكيل تحليل العلاقات المالية والشبكات

المهام:
- رسم العلاقات المالية
- تحليل الشبكات
- كشف العلاقات المخفية
- كشف الاحتيال المنظم
- تحليل شبكات الموردين والعملاء
- تتبع التدفقات المالية المعقدة

Developed By: Ahmed Mostafa Ibrahim
© 2025 Finovate – AHMED EG - All Rights Reserved
"""

from typing import Dict, List, Any, Set, Tuple
from datetime import datetime
from collections import defaultdict


class FinancialGraphIntelligenceAgent:
    """وكيل تحليل العلاقات المالية والشبكات"""
    
    def __init__(self):
        self.agent_name = "Financial Graph Intelligence Agent"
        self.agent_type = "graph_analysis"
        self.created_at = datetime.now()
        self.nodes = {}
        self.edges = []
        
    def build_financial_graph(self, transactions: List[Dict]) -> Dict:
        """بناء الرسم البياني المالي من المعاملات"""
        
        graph = {
            'nodes': [],
            'edges': [],
            'node_count': 0,
            'edge_count': 0,
            'connected_components': 0,
            'suspicious_patterns': []
        }
        
        # بناء العقد (الكيانات)
        entities = set()
        for txn in transactions:
            if 'from_entity' in txn:
                entities.add(txn['from_entity'])
            if 'to_entity' in txn:
                entities.add(txn['to_entity'])
        
        # إضافة العقد
        for entity in entities:
            node = {
                'id': entity,
                'type': self._infer_entity_type(entity),
                'transaction_count': 0,
                'total_inflow': 0,
                'total_outflow': 0,
                'connections': set()
            }
            graph['nodes'].append(node)
            self.nodes[entity] = node
        
        # بناء الحواف (المعاملات)
        for txn in transactions:
            from_entity = txn.get('from_entity')
            to_entity = txn.get('to_entity')
            amount = txn.get('amount', 0)
            
            if from_entity and to_entity:
                edge = {
                    'from': from_entity,
                    'to': to_entity,
                    'amount': amount,
                    'date': txn.get('date', ''),
                    'type': txn.get('type', 'transfer')
                }
                graph['edges'].append(edge)
                self.edges.append(edge)
                
                # تحديث إحصائيات العقد
                if from_entity in self.nodes:
                    self.nodes[from_entity]['transaction_count'] += 1
                    self.nodes[from_entity]['total_outflow'] += amount
                    self.nodes[from_entity]['connections'].add(to_entity)
                
                if to_entity in self.nodes:
                    self.nodes[to_entity]['transaction_count'] += 1
                    self.nodes[to_entity]['total_inflow'] += amount
                    self.nodes[to_entity]['connections'].add(from_entity)
        
        graph['node_count'] = len(graph['nodes'])
        graph['edge_count'] = len(graph['edges'])
        
        # تحويل المجموعات إلى قوائم للتسلسل
        for node in graph['nodes']:
            node['connections'] = list(node['connections'])
        
        # كشف الأنماط المشبوهة
        graph['suspicious_patterns'] = self._detect_suspicious_patterns(graph)
        
        return graph
    
    def _infer_entity_type(self, entity_id: str) -> str:
        """استنتاج نوع الكيان من المعرف"""
        
        entity_id_lower = entity_id.lower()
        
        if 'bank' in entity_id_lower:
            return 'BANK'
        elif 'customer' in entity_id_lower or 'client' in entity_id_lower:
            return 'CUSTOMER'
        elif 'vendor' in entity_id_lower or 'supplier' in entity_id_lower:
            return 'VENDOR'
        elif 'employee' in entity_id_lower:
            return 'EMPLOYEE'
        elif 'company' in entity_id_lower or 'corp' in entity_id_lower:
            return 'COMPANY'
        else:
            return 'UNKNOWN'
    
    def _detect_suspicious_patterns(self, graph: Dict) -> List[Dict]:
        """كشف الأنماط المشبوهة في الشبكة"""
        
        patterns = []
        
        # نمط 1: دائرة مغلقة (Circular Transactions)
        circular = self._detect_circular_transactions(graph)
        if circular:
            patterns.append({
                'type': 'CIRCULAR_TRANSACTIONS',
                'severity': 'HIGH',
                'description': 'تم كشف معاملات دائرية مغلقة',
                'entities': circular,
                'risk': 'غسيل أموال محتمل أو تضخيم إيرادات'
            })
        
        # نمط 2: تركيز عالي (High Concentration)
        concentration = self._detect_high_concentration(graph)
        if concentration:
            patterns.append({
                'type': 'HIGH_CONCENTRATION',
                'severity': 'MEDIUM',
                'description': 'تركيز معاملات عالي في كيان واحد',
                'entities': concentration,
                'risk': 'اعتماد مفرط أو علاقات مشبوهة'
            })
        
        # نمط 3: هيكل نجمي (Star Pattern)
        star = self._detect_star_pattern(graph)
        if star:
            patterns.append({
                'type': 'STAR_PATTERN',
                'severity': 'HIGH',
                'description': 'نمط نجمي - كيان مركزي يتصل بعدة كيانات',
                'entities': star,
                'risk': 'شركة وهمية مركزية محتملة'
            })
        
        # نمط 4: معاملات متكررة بنفس القيمة
        repeated = self._detect_repeated_amounts(graph)
        if repeated:
            patterns.append({
                'type': 'REPEATED_AMOUNTS',
                'severity': 'MEDIUM',
                'description': 'معاملات متكررة بنفس القيمة بدقة',
                'count': len(repeated),
                'risk': 'أتمتة مشبوهة أو تقسيم معاملات'
            })
        
        return patterns
    
    def _detect_circular_transactions(self, graph: Dict) -> List[str]:
        """كشف المعاملات الدائرية A→B→C→A"""
        
        adjacency = defaultdict(set)
        for edge in graph['edges']:
            adjacency[edge['from']].add(edge['to'])
        
        cycles = []
        nodes_list = list(adjacency.keys())  # إنشاء نسخة ثابتة
        
        def find_cycle(start, current, path, visited_edges):
            for neighbor in adjacency[current]:
                edge_key = (current, neighbor)
                if edge_key in visited_edges:
                    continue
                
                if neighbor == start and len(path) >= 3:
                    return path + [neighbor]
                
                if neighbor not in path:
                    new_visited = visited_edges | {edge_key}
                    result = find_cycle(start, neighbor, path + [current], new_visited)
                    if result:
                        return result
            
            return None
        
        for node in nodes_list:
            cycle = find_cycle(node, node, [], set())
            if cycle:
                cycles.append(cycle)
                break
        
        return cycles[0] if cycles else []
    
    def _detect_high_concentration(self, graph: Dict) -> Dict:
        """كشف التركيز العالي للمعاملات"""
        
        if not graph['nodes']:
            return {}
        
        # إيجاد الكيان بأعلى نسبة تدفق
        max_concentration = 0
        concentrated_entity = None
        
        for node in graph['nodes']:
            total = node['total_inflow'] + node['total_outflow']
            if total > 0:
                connections = len(node['connections'])
                if connections > 0:
                    avg_per_connection = total / connections
                    max_txn = max(node['total_inflow'], node['total_outflow'])
                    concentration_ratio = max_txn / total if total > 0 else 0
                    
                    if concentration_ratio > max_concentration and concentration_ratio > 0.7:
                        max_concentration = concentration_ratio
                        concentrated_entity = {
                            'entity': node['id'],
                            'concentration_ratio': round(concentration_ratio * 100, 2),
                            'total_volume': total
                        }
        
        return concentrated_entity
    
    def _detect_star_pattern(self, graph: Dict) -> Dict:
        """كشف النمط النجمي"""
        
        if not graph['nodes']:
            return {}
        
        # إيجاد الكيان بأكبر عدد اتصالات
        max_connections = 0
        center_entity = None
        
        for node in graph['nodes']:
            connections = len(node['connections'])
            if connections > max_connections and connections >= 5:
                max_connections = connections
                center_entity = {
                    'center': node['id'],
                    'connections_count': connections,
                    'connected_to': node['connections'][:10]
                }
        
        return center_entity
    
    def _detect_repeated_amounts(self, graph: Dict) -> List[float]:
        """كشف المعاملات المتكررة بنفس القيمة"""
        
        amount_counts = defaultdict(int)
        
        for edge in graph['edges']:
            amount = edge['amount']
            if amount > 0:
                rounded_amount = round(amount, 2)
                amount_counts[rounded_amount] += 1
        
        repeated = [amount for amount, count in amount_counts.items() if count >= 5]
        
        return repeated
    
    def analyze_network_centrality(self, graph: Dict) -> Dict:
        """تحليل مركزية الشبكة"""
        
        centrality = {
            'most_connected': None,
            'highest_flow': None,
            'potential_bottlenecks': [],
            'isolated_nodes': []
        }
        
        if not graph['nodes']:
            return centrality
        
        max_connections = 0
        for node in graph['nodes']:
            connections = len(node['connections'])
            if connections > max_connections:
                max_connections = connections
                centrality['most_connected'] = {
                    'entity': node['id'],
                    'connections': connections
                }
        
        max_flow = 0
        for node in graph['nodes']:
            total_flow = node['total_inflow'] + node['total_outflow']
            if total_flow > max_flow:
                max_flow = total_flow
                centrality['highest_flow'] = {
                    'entity': node['id'],
                    'total_flow': total_flow
                }
        
        for node in graph['nodes']:
            if len(node['connections']) == 0:
                centrality['isolated_nodes'].append(node['id'])
        
        return centrality
    
    def generate_fraud_risk_report(self, graph: Dict) -> Dict:
        """إنشاء تقرير مخاطر الاحتيال بناءً على تحليل الشبكة"""
        
        report = {
            'agent': self.agent_name,
            'report_type': 'Financial Graph Fraud Risk Analysis',
            'timestamp': datetime.now().isoformat(),
            'network_stats': {
                'total_entities': graph['node_count'],
                'total_transactions': graph['edge_count'],
                'suspicious_patterns_found': len(graph['suspicious_patterns'])
            },
            'risk_level': 'LOW',
            'risk_score': 0,
            'findings': [],
            'recommendations': []
        }
        
        risk_score = 0
        
        for pattern in graph['suspicious_patterns']:
            if pattern['severity'] == 'HIGH':
                risk_score += 30
                report['findings'].append({
                    'severity': 'HIGH',
                    'finding': pattern['description'],
                    'risk': pattern['risk'],
                    'entities_involved': pattern.get('entities', [])
                })
            elif pattern['severity'] == 'MEDIUM':
                risk_score += 15
                report['findings'].append({
                    'severity': 'MEDIUM',
                    'finding': pattern['description'],
                    'risk': pattern['risk']
                })
        
        if risk_score >= 60:
            report['risk_level'] = 'CRITICAL'
        elif risk_score >= 30:
            report['risk_level'] = 'HIGH'
        elif risk_score >= 15:
            report['risk_level'] = 'MEDIUM'
        else:
            report['risk_level'] = 'LOW'
        
        report['risk_score'] = min(risk_score, 100)
        
        if report['risk_level'] in ['CRITICAL', 'HIGH']:
            report['recommendations'].append({
                'priority': 'URGENT',
                'action': 'إجراء تحقيق فوري في المعاملات المشبوهة',
                'details': 'مراجعة جميع الكيانات المدرجة في النتائج'
            })
        
        if any(p['type'] == 'CIRCULAR_TRANSACTIONS' for p in graph['suspicious_patterns']):
            report['recommendations'].append({
                'priority': 'HIGH',
                'action': 'التحقق من طبيعة المعاملات الدائرية',
                'details': 'قد تشير إلى غسيل أموال أو تضخيم إيرادات'
            })
        
        return report


# === مثال على الاستخدام ===
if __name__ == "__main__":
    print("=" * 70)
    print("Finovate Audit Nexus AI - Financial Graph Intelligence Agent")
    print("=" * 70)
    
    agent = FinancialGraphIntelligenceAgent()
    
    sample_transactions = [
        {'from_entity': 'Company_A', 'to_entity': 'Vendor_X', 'amount': 50000, 'date': '2025-01-01', 'type': 'payment'},
        {'from_entity': 'Vendor_X', 'to_entity': 'Company_B', 'amount': 48000, 'date': '2025-01-02', 'type': 'transfer'},
        {'from_entity': 'Company_B', 'to_entity': 'Company_A', 'amount': 45000, 'date': '2025-01-03', 'type': 'transfer'},
        {'from_entity': 'Company_A', 'to_entity': 'Customer_1', 'amount': 100000, 'date': '2025-01-04', 'type': 'sale'},
        {'from_entity': 'Company_A', 'to_entity': 'Customer_2', 'amount': 75000, 'date': '2025-01-05', 'type': 'sale'},
        {'from_entity': 'Company_A', 'to_entity': 'Customer_3', 'amount': 60000, 'date': '2025-01-06', 'type': 'sale'},
        {'from_entity': 'Company_A', 'to_entity': 'Customer_4', 'amount': 80000, 'date': '2025-01-07', 'type': 'sale'},
        {'from_entity': 'Company_A', 'to_entity': 'Customer_5', 'amount': 90000, 'date': '2025-01-08', 'type': 'sale'},
        {'from_entity': 'Company_A', 'to_entity': 'Customer_6', 'amount': 55000, 'date': '2025-01-09', 'type': 'sale'},
        {'from_entity': 'Bank_Main', 'to_entity': 'Company_A', 'amount': 200000, 'date': '2025-01-10', 'type': 'loan'},
        {'from_entity': 'Company_A', 'to_entity': 'Bank_Main', 'amount': 25000, 'date': '2025-01-15', 'type': 'repayment'},
        {'from_entity': 'Company_A', 'to_entity': 'Bank_Main', 'amount': 25000, 'date': '2025-02-15', 'type': 'repayment'},
        {'from_entity': 'Company_A', 'to_entity': 'Bank_Main', 'amount': 25000, 'date': '2025-03-15', 'type': 'repayment'},
        {'from_entity': 'Company_A', 'to_entity': 'Bank_Main', 'amount': 25000, 'date': '2025-04-15', 'type': 'repayment'},
        {'from_entity': 'Company_A', 'to_entity': 'Bank_Main', 'amount': 25000, 'date': '2025-05-15', 'type': 'repayment'},
    ]
    
    print("\n🕸️ جاري بناء الرسم البياني المالي...")
    graph = agent.build_financial_graph(sample_transactions)
    
    print(f"\n{'='*70}")
    print("إحصائيات الشبكة المالية")
    print(f"{'='*70}")
    print(f"\nعدد الكيانات: {graph['node_count']}")
    print(f"عدد المعاملات: {graph['edge_count']}")
    
    print(f"\n📊 الكيانات:")
    for node in graph['nodes']:
        print(f"\n  • {node['id']} ({node['type']})")
        print(f"    اتصالات: {len(node['connections'])}")
        print(f"    تدفق وارد: {node['total_inflow']:,.0f}")
        print(f"    تدفق صادر: {node['total_outflow']:,.0f}")
    
    print(f"\n⚠️ الأنماط المشبوهة المكتشفة: {len(graph['suspicious_patterns'])}")
    for pattern in graph['suspicious_patterns']:
        print(f"\n  [{pattern['severity']}] {pattern['type']}")
        print(f"  → {pattern['description']}")
        print(f"  الخطر: {pattern['risk']}")
    
    print(f"\n{'='*70}")
    print("تحليل مركزية الشبكة")
    print(f"{'='*70}")
    
    centrality = agent.analyze_network_centrality(graph)
    
    if centrality['most_connected']:
        print(f"\n🔗 الأكثر اتصالاً:")
        print(f"  {centrality['most_connected']['entity']} ({centrality['most_connected']['connections']} اتصال)")
    
    if centrality['highest_flow']:
        print(f"\n💰 أعلى تدفق:")
        print(f"  {centrality['highest_flow']['entity']} ({centrality['highest_flow']['total_flow']:,.0f})")
    
    print(f"\n{'='*70}")
    print("تقرير مخاطر الاحتيال")
    print(f"{'='*70}")
    
    fraud_report = agent.generate_fraud_risk_report(graph)
    
    print(f"\n🎯 مستوى المخاطرة: {fraud_report['risk_level']}")
    print(f"📊 درجة المخاطرة: {fraud_report['risk_score']}/100")
    
    if fraud_report['findings']:
        print(f"\n🔍 النتائج:")
        for finding in fraud_report['findings']:
            print(f"\n  [{finding['severity']}] {finding['finding']}")
            print(f"  الخطر: {finding['risk']}")
    
    if fraud_report['recommendations']:
        print(f"\n💡 التوصيات:")
        for rec in fraud_report['recommendations']:
            print(f"\n  [{rec['priority']}] {rec['action']}")
            if 'details' in rec:
                print(f"  تفاصيل: {rec['details']}")
    
    print(f"\n{'='*70}")
    print("✅ اكتمل تحليل الشبكة المالية بنجاح!")
    print(f"{'='*70}\n")
