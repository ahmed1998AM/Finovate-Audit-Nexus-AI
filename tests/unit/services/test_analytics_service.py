"""
اختبارات وحدة خدمة التحليلات المالية
"""

import pytest
from datetime import datetime

from backend.services.analytics_service import AnalyticsService


@pytest.fixture
def service():
    return AnalyticsService()


class TestCalculateFinancialRatios:
    @pytest.fixture
    def full_financial_data(self):
        return {
            'current_assets': 200000,
            'current_liabilities': 100000,
            'inventory': 50000,
            'net_income': 30000,
            'revenue': 500000,
            'cogs': 300000,
            'equity': 150000,
            'total_debt': 100000,
            'total_assets': 500000,
            'accounts_receivable': 40000,
        }

    def test_all_ratios_computed_from_valid_data(self, service, full_financial_data):
        result = service.calculate_financial_ratios(full_financial_data)
        assert result['liquidity_ratios']['current_ratio'] == 2.0
        assert result['liquidity_ratios']['quick_ratio'] == 1.5
        assert result['profitability_ratios']['gross_profit_margin'] == 40.0
        assert result['profitability_ratios']['net_profit_margin'] == 6.0
        assert result['profitability_ratios']['roe'] == 20.0
        assert result['leverage_ratios']['debt_to_assets'] == 0.2
        assert result['leverage_ratios']['debt_to_equity'] == 0.67
        assert result['efficiency_ratios']['receivables_turnover'] == 12.5
        assert 'calculated_at' in result

    def test_zero_current_liabilities_returns_zero_ratios(self, service):
        data = {
            'current_assets': 100000,
            'current_liabilities': 0,
            'inventory': 20000,
            'net_income': 5000,
            'revenue': 100000,
        }
        result = service.calculate_financial_ratios(data)
        assert result['liquidity_ratios']['current_ratio'] == 0
        assert result['liquidity_ratios']['quick_ratio'] == 0

    def test_zero_revenue_returns_zero_profitability_ratios(self, service):
        data = {
            'net_income': 0,
            'revenue': 0,
            'cogs': 0,
            'current_assets': 50000,
            'current_liabilities': 25000,
        }
        result = service.calculate_financial_ratios(data)
        assert result['profitability_ratios']['gross_profit_margin'] == 0
        assert result['profitability_ratios']['net_profit_margin'] == 0

    def test_missing_keys_omits_ratio_categories(self, service):
        data = {'current_assets': 100000, 'current_liabilities': 50000}
        result = service.calculate_financial_ratios(data)
        assert 'current_ratio' in result['liquidity_ratios']
        assert result['liquidity_ratios']['current_ratio'] == 2.0
        assert result['profitability_ratios'] == {}
        assert result['leverage_ratios'] == {}
        assert result['efficiency_ratios'] == {}

    def test_empty_dict_returns_all_empty_categories(self, service):
        result = service.calculate_financial_ratios({})
        assert result['liquidity_ratios'] == {}
        assert result['profitability_ratios'] == {}
        assert result['leverage_ratios'] == {}
        assert result['efficiency_ratios'] == {}
        assert 'calculated_at' in result


class TestAnalyzeTrends:
    @pytest.fixture
    def upward_data(self):
        return [
            {'date': '2024-Q1', 'revenue': 100},
            {'date': '2024-Q2', 'revenue': 120},
            {'date': '2024-Q3', 'revenue': 150},
        ]

    @pytest.fixture
    def flat_data(self):
        return [
            {'date': '2024-Q1', 'revenue': 100},
            {'date': '2024-Q2', 'revenue': 98},
            {'date': '2024-Q3', 'revenue': 97},
        ]

    @pytest.fixture
    def downward_data(self):
        return [
            {'date': '2024-Q1', 'revenue': 200},
            {'date': '2024-Q2', 'revenue': 180},
            {'date': '2024-Q3', 'revenue': 150},
        ]

    def test_strong_upward_trend_when_growth_exceeds_5_percent(self, service, upward_data):
        result = service.analyze_trends(upward_data, 'revenue')
        assert result['trend'] == 'strong_upward'
        assert result['average_growth_rate'] > 5
        assert result['min_value'] == 100
        assert result['max_value'] == 150
        assert result['latest_value'] == 150
        assert result['data_points'] == 3

    def test_upward_trend_when_growth_positive_and_below_5(self, service):
        data = [
            {'date': '2024-Q1', 'val': 100},
            {'date': '2024-Q2', 'val': 103},
            {'date': '2024-Q3', 'val': 105},
        ]
        result = service.analyze_trends(data, 'val')
        assert result['trend'] == 'upward'

    def test_stable_trend_when_growth_slightly_negative(self, service, flat_data):
        result = service.analyze_trends(flat_data, 'revenue')
        assert result['trend'] == 'stable'

    def test_downward_trend_when_decline_between_5_and_10_percent(self, service):
        data = [
            {'date': '2024-Q1', 'val': 200},
            {'date': '2024-Q2', 'val': 185},
            {'date': '2024-Q3', 'val': 172},
        ]
        result = service.analyze_trends(data, 'val')
        assert result['trend'] == 'downward'

    def test_strong_downward_trend_when_decline_exceeds_10_percent(self, service, downward_data):
        result = service.analyze_trends(downward_data, 'revenue')
        assert result['trend'] == 'strong_downward'

    def test_insufficient_data_with_single_point_returns_error(self, service):
        data = [{'date': '2024-Q1', 'revenue': 100}]
        result = service.analyze_trends(data, 'revenue')
        assert 'error' in result
        assert result['error'] == 'Insufficient data'

    def test_empty_list_returns_error(self, service):
        result = service.analyze_trends([], 'revenue')
        assert 'error' in result

    def test_missing_metric_defaults_to_zero(self, service):
        data = [
            {'date': '2024-Q1', 'revenue': 100},
            {'date': '2024-Q2', 'revenue': 200},
        ]
        result = service.analyze_trends(data, 'nonexistent')
        assert result['min_value'] == 0
        assert result['max_value'] == 0


class TestDetectAnomalies:
    def test_no_anomalies_detected_when_all_within_threshold(self, service):
        data = [{'value': 10}, {'value': 12}, {'value': 11}, {'value': 9}, {'value': 10}]
        result = service.detect_anomalies(data)
        assert result == []

    def test_anomalies_detected_when_value_exceeds_threshold(self, service):
        data = [
            {'value': 1}, {'value': 1}, {'value': 1}, {'value': 1},
            {'value': 1}, {'value': 1}, {'value': 1}, {'value': 1},
            {'value': 3}, {'value': 4},
        ]
        result = service.detect_anomalies(data)
        assert len(result) == 1
        assert result[0]['value'] == 4

    def test_high_severity_for_z_score_above_3(self, service):
        data = [{'x': 5}] * 19 + [{'x': 100}]
        result = service.detect_anomalies(data)
        assert len(result) == 1
        assert result[0]['severity'] == 'high'

    def test_medium_severity_for_z_score_between_2_and_3(self, service):
        data = [{'v': 10}] * 9 + [{'v': 15}]
        result = service.detect_anomalies(data)
        assert len(result) == 1
        assert result[0]['severity'] == 'medium'

    def test_empty_list_returns_empty_anomalies(self, service):
        result = service.detect_anomalies([])
        assert result == []

    def test_single_item_returns_no_anomalies(self, service):
        result = service.detect_anomalies([{'value': 42}])
        assert result == []

    def test_only_non_numeric_values_returns_empty(self, service):
        data = [{'name': 'foo'}, {'name': 'bar'}]
        result = service.detect_anomalies(data)
        assert result == []

    def test_custom_threshold_detects_anomalies(self, service):
        data = [{'value': 10}, {'value': 12}, {'value': 11}, {'value': 9}, {'value': 10}]
        result = service.detect_anomalies(data, threshold=0.5)
        assert len(result) > 0

    def test_all_identical_values_return_no_anomalies(self, service):
        data = [{'v': 5}, {'v': 5}, {'v': 5}]
        result = service.detect_anomalies(data)
        assert result == []


class TestCalculateRiskScore:
    def test_low_risk_when_score_25_or_below(self, service):
        factors = {
            'financial_risk': 10,
            'compliance_risk': 10,
            'fraud_risk': 10,
            'operational_risk': 10,
        }
        result = service.calculate_risk_score(factors)
        assert result['overall_score'] == 10.0
        assert result['risk_level'] == 'low'

    def test_medium_risk_when_score_between_26_and_50(self, service):
        factors = {
            'financial_risk': 50,
            'compliance_risk': 30,
            'fraud_risk': 40,
            'operational_risk': 20,
        }
        result = service.calculate_risk_score(factors)
        assert 25 < result['overall_score'] <= 50
        assert result['risk_level'] == 'medium'

    def test_high_risk_when_score_between_51_and_75(self, service):
        factors = {
            'financial_risk': 80,
            'compliance_risk': 70,
            'fraud_risk': 60,
            'operational_risk': 50,
        }
        result = service.calculate_risk_score(factors)
        assert 50 < result['overall_score'] <= 75
        assert result['risk_level'] == 'high'

    def test_critical_risk_when_score_exceeds_75(self, service):
        factors = {
            'financial_risk': 100,
            'compliance_risk': 100,
            'fraud_risk': 100,
            'operational_risk': 100,
        }
        result = service.calculate_risk_score(factors)
        assert result['overall_score'] == 100.0
        assert result['risk_level'] == 'critical'

    def test_missing_factors_default_to_zero(self, service):
        factors = {'financial_risk': 200}
        result = service.calculate_risk_score(factors)
        assert result['overall_score'] == 50.0
        assert result['risk_level'] == 'medium'

    def test_empty_dict_returns_zero_score_and_low_risk(self, service):
        result = service.calculate_risk_score({})
        assert result['overall_score'] == 0.0
        assert result['risk_level'] == 'low'

    def test_factor_scores_and_weights_in_result(self, service):
        factors = {'fraud_risk': 80}
        result = service.calculate_risk_score(factors)
        assert 'factor_scores' in result
        assert 'weights' in result
        assert result['factor_scores']['fraud_risk'] == 80
        assert result['weights']['fraud_risk'] == 0.30


class TestGenerateInsights:
    def test_low_liquidity_warning_when_current_ratio_below_one(self, service):
        results = {
            'ratios': {
                'liquidity_ratios': {'current_ratio': 0.5},
                'profitability_ratios': {'net_profit_margin': 15},
            }
        }
        insights = service.generate_insights(results)
        assert len(insights) == 1
        assert insights[0]['type'] == 'warning'
        assert insights[0]['category'] == 'liquidity'

    def test_low_profit_margin_warning_when_net_below_5_percent(self, service):
        results = {
            'ratios': {
                'liquidity_ratios': {'current_ratio': 2.0},
                'profitability_ratios': {'net_profit_margin': 3},
            }
        }
        insights = service.generate_insights(results)
        assert len(insights) == 1
        assert insights[0]['type'] == 'warning'
        assert insights[0]['category'] == 'profitability'

    def test_strong_downward_trend_triggers_alert(self, service):
        results = {
            'trends': {
                'revenue': {
                    'trend': 'strong_downward',
                    'average_growth_rate': -15.5,
                }
            }
        }
        insights = service.generate_insights(results)
        assert len(insights) == 1
        assert insights[0]['type'] == 'alert'
        assert insights[0]['category'] == 'trend'

    def test_high_severity_anomaly_triggers_critical_insight(self, service):
        results = {
            'anomalies': [
                {'severity': 'high', 'field': 'amount', 'value': 999},
            ]
        }
        insights = service.generate_insights(results)
        assert len(insights) == 1
        assert insights[0]['type'] == 'critical'
        assert insights[0]['category'] == 'anomaly'

    def test_no_insights_when_everything_normal(self, service):
        results = {
            'ratios': {
                'liquidity_ratios': {'current_ratio': 2.0},
                'profitability_ratios': {'net_profit_margin': 15},
            }
        }
        insights = service.generate_insights(results)
        assert insights == []

    def test_empty_dict_returns_no_insights(self, service):
        insights = service.generate_insights({})
        assert insights == []

    def test_multiple_insights_combined(self, service):
        results = {
            'ratios': {
                'liquidity_ratios': {'current_ratio': 0.8},
                'profitability_ratios': {'net_profit_margin': 2.5},
            },
            'trends': {
                'profit': {
                    'trend': 'strong_downward',
                    'average_growth_rate': -20.0,
                }
            },
            'anomalies': [
                {'severity': 'high', 'field': 'amount', 'value': 999},
            ]
        }
        insights = service.generate_insights(results)
        assert len(insights) >= 4

    def test_medium_severity_anomalies_dont_trigger_critical(self, service):
        results = {
            'anomalies': [
                {'severity': 'medium', 'field': 'amount', 'value': 50},
            ]
        }
        insights = service.generate_insights(results)
        assert insights == []


class TestGetDashboardMetrics:
    def test_returns_expected_structure_with_company_id(self, service):
        result = service.get_dashboard_metrics(company_id=42)
        assert result['company_id'] == 42
        assert isinstance(result['financial_health_score'], int)
        assert isinstance(result['risk_score'], int)
        assert isinstance(result['compliance_score'], int)
        assert isinstance(result['active_audits'], int)
        assert isinstance(result['pending_findings'], int)
        assert isinstance(result['critical_alerts'], int)
        assert 'last_sync' in result
        assert 'kpi_summary' in result
        assert 'revenue_growth' in result['kpi_summary']
        assert 'profit_margin' in result['kpi_summary']
        assert 'current_ratio' in result['kpi_summary']
        assert 'debt_to_equity' in result['kpi_summary']
