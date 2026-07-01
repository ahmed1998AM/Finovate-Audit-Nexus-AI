"""
اختبارات وحدة خدمة التحليل التنبؤي
"""

import pytest

from backend.services.predictive_service import PredictiveService


@pytest.fixture
def service():
    return PredictiveService()


class TestPredictRevenue:
    def test_upward_trend_returns_positive_predictions(self, service):
        data = [100, 110, 120, 130, 140]
        result = service.predict_revenue(data, periods=3)
        assert result['trend'] == 'صاعد'
        assert len(result['predictions']) == 3
        assert all(p > 0 for p in result['predictions'])
        assert result['growth_rate'] > 0

    def test_downward_trend_returns_decreasing_predictions(self, service):
        data = [200, 180, 160, 140, 120]
        result = service.predict_revenue(data, periods=4)
        assert result['trend'] == 'هابط'
        assert len(result['predictions']) == 4
        assert result['predictions'][0] > result['predictions'][-1]
        assert result['growth_rate'] < 0

    def test_flat_data_returns_constant_predictions(self, service):
        data = [50, 50, 50, 50, 50]
        result = service.predict_revenue(data, periods=3)
        assert result['growth_rate'] == 0.0
        assert all(p == 50 for p in result['predictions'])

    def test_insufficient_data_with_single_point_returns_error(self, service):
        result = service.predict_revenue([100], periods=3)
        assert 'error' in result

    def test_empty_list_returns_error(self, service):
        result = service.predict_revenue([], periods=3)
        assert 'error' in result

    def test_custom_periods_returns_correct_prediction_count(self, service):
        data = [10, 20, 30, 40, 50]
        result = service.predict_revenue(data, periods=5)
        assert len(result['predictions']) == 5

    def test_large_data_set_returns_valid_predictions(self, service):
        data = list(range(1, 101))
        result = service.predict_revenue(data, periods=12)
        assert len(result['predictions']) == 12
        assert result['trend'] == 'صاعد'

    def test_two_point_data_generates_linear_forecast(self, service):
        data = [100, 200]
        result = service.predict_revenue(data, periods=2)
        assert len(result['predictions']) == 2
        assert result['predictions'][0] == 300
        assert result['predictions'][1] == 400


class TestPredictFraudRisk:
    def test_high_risk_when_both_indicators_present(self, service):
        patterns = {
            'manual_adjustments_trend': 'increasing',
            'unusual_hours_activity': True,
        }
        result = service.predict_fraud_risk(patterns)
        assert result['predicted_risk_score'] == 50
        assert len(result['indicators']) == 2
        assert result['confidence'] == 0.85

    def test_low_risk_when_no_indicators_present(self, service):
        patterns = {}
        result = service.predict_fraud_risk(patterns)
        assert result['predicted_risk_score'] == 0
        assert result['indicators'] == []
        assert result['confidence'] == 0.85

    def test_risk_score_capped_at_100(self, service):
        patterns = {
            'manual_adjustments_trend': 'increasing',
            'unusual_hours_activity': True,
            'another_indicator': True,
        }
        result = service.predict_fraud_risk(patterns)
        assert result['predicted_risk_score'] <= 100

    def test_only_manual_adjustments_risk(self, service):
        patterns = {'manual_adjustments_trend': 'increasing'}
        result = service.predict_fraud_risk(patterns)
        assert result['predicted_risk_score'] == 30
        assert len(result['indicators']) == 1

    def test_only_unusual_hours_risk(self, service):
        patterns = {'unusual_hours_activity': True}
        result = service.predict_fraud_risk(patterns)
        assert result['predicted_risk_score'] == 20
        assert len(result['indicators']) == 1


class TestPredictCashFlowIssues:
    def test_returns_expected_structure(self, service):
        result = service.predict_cash_flow_issues([])
        assert 'liquidity_risk' in result
        assert 'projected_deficit_period' in result
        assert 'recommendations' in result
        assert result['liquidity_risk'] == 'Low'
        assert result['projected_deficit_period'] is None
        assert isinstance(result['recommendations'], list)

    def test_hardcoded_response_regardless_of_input(self, service):
        with_data = service.predict_cash_flow_issues([100, 90, 80, 70])
        empty = service.predict_cash_flow_issues([])
        assert with_data == empty
