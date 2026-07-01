"""
اختبارات وحدة خدمة تنسيق وإدارة الوكلاء الذكية
"""

import pytest

from backend.services.ai_orchestration_service import AIOrchestrationService


@pytest.fixture
def service():
    return AIOrchestrationService()


class TestRegisterAgent:
    def test_register_agent_returns_true(self, service):
        result = service.register_agent('agent-1', 'audit', ['analysis', 'reporting'])
        assert result is True
        assert 'agent-1' in service.agent_registry

    def test_registered_agent_has_correct_defaults(self, service):
        service.register_agent('agent-2', 'fraud', ['detection'])
        agent = service.agent_registry['agent-2']
        assert agent['agent_type'] == 'fraud'
        assert agent['status'] == 'available'
        assert agent['current_task'] is None
        assert agent['tasks_completed'] == 0
        assert 'registered_at' in agent

    def test_register_multiple_agents(self, service):
        service.register_agent('a1', 'audit', ['x'])
        service.register_agent('a2', 'fraud', ['y'])
        service.register_agent('a3', 'compliance', ['z'])
        assert len(service.agent_registry) == 3

    def test_re_registration_overwrites_existing_agent(self, service):
        service.register_agent('agent-1', 'audit', ['old'])
        service.register_agent('agent-1', 'fraud', ['new'])
        agent = service.agent_registry['agent-1']
        assert agent['agent_type'] == 'fraud'
        assert agent['capabilities'] == ['new']
        assert agent['tasks_completed'] == 0


class TestAssignTask:
    def test_assign_task_returns_task_dict(self, service):
        service.register_agent('agent-1', 'audit', ['analysis'])
        task = service.assign_task('task-1', 'agent-1', 'analysis', {'query': 'test'})
        assert task['task_id'] == 'task-1'
        assert task['agent_id'] == 'agent-1'
        assert task['status'] == 'pending'
        assert task['result'] is None
        assert 'created_at' in task
        assert task['started_at'] is None
        assert task['completed_at'] is None

    def test_assign_task_sets_agent_busy(self, service):
        service.register_agent('agent-1', 'audit', ['analysis'])
        service.assign_task('task-1', 'agent-1', 'analysis', {})
        agent = service.agent_registry['agent-1']
        assert agent['status'] == 'busy'
        assert agent['current_task'] == 'task-1'

    def test_assign_task_with_priority(self, service):
        service.register_agent('agent-1', 'audit', [])
        task = service.assign_task('t1', 'agent-1', 'audit', {}, priority=1)
        assert task['priority'] == 1
        task2 = service.assign_task('t2', 'agent-1', 'audit', {}, priority=10)
        assert task2['priority'] == 10

    def test_assign_to_unregistered_agent_returns_error(self, service):
        result = service.assign_task('task-1', 'ghost-agent', 'audit', {})
        assert result['success'] is False
        assert 'error' in result

    def test_assign_task_appends_to_queue(self, service):
        service.register_agent('agent-1', 'audit', [])
        service.assign_task('t1', 'agent-1', 'audit', {})
        service.assign_task('t2', 'agent-1', 'audit', {})
        assert len(service.task_queue) == 2


class TestStartTask:
    def test_start_task_returns_true_and_updates_status(self, service):
        service.register_agent('agent-1', 'audit', [])
        service.assign_task('task-1', 'agent-1', 'audit', {})
        result = service.start_task('task-1')
        assert result is True
        task = next(t for t in service.task_queue if t['task_id'] == 'task-1')
        assert task['status'] == 'running'
        assert task['started_at'] is not None

    def test_start_non_existent_task_returns_false(self, service):
        result = service.start_task('nonexistent')
        assert result is False


class TestCompleteTask:
    def test_complete_task_returns_true_and_stores_result(self, service):
        service.register_agent('agent-1', 'audit', [])
        service.assign_task('task-1', 'agent-1', 'audit', {})
        service.start_task('task-1')
        result = service.complete_task('task-1', {'status': 'ok'})
        assert result is True
        task = next(t for t in service.task_queue if t['task_id'] == 'task-1')
        assert task['status'] == 'completed'
        assert task['result'] == {'status': 'ok'}
        assert task['completed_at'] is not None

    def test_complete_task_returns_agent_to_available(self, service):
        service.register_agent('agent-1', 'audit', [])
        service.assign_task('task-1', 'agent-1', 'audit', {})
        service.start_task('task-1')
        service.complete_task('task-1', {})
        agent = service.agent_registry['agent-1']
        assert agent['status'] == 'available'
        assert agent['current_task'] is None
        assert agent['tasks_completed'] == 1

    def test_complete_task_adds_to_completed_dict(self, service):
        service.register_agent('agent-1', 'audit', [])
        service.assign_task('task-1', 'agent-1', 'audit', {})
        service.complete_task('task-1', {'done': True})
        assert 'task-1' in service.completed_tasks
        assert service.completed_tasks['task-1']['result'] == {'done': True}

    def test_complete_non_existent_task_returns_false(self, service):
        result = service.complete_task('nonexistent', {})
        assert result is False

    def test_complete_task_without_start_is_allowed(self, service):
        service.register_agent('agent-1', 'audit', [])
        service.assign_task('task-1', 'agent-1', 'audit', {})
        result = service.complete_task('task-1', {'skipped': True})
        assert result is True
        task = next(t for t in service.task_queue if t['task_id'] == 'task-1')
        assert task['status'] == 'completed'


class TestGetTaskStatus:
    def test_get_task_status_for_pending_task(self, service):
        service.register_agent('agent-1', 'audit', [])
        service.assign_task('task-1', 'agent-1', 'audit', {'x': 1})
        status = service.get_task_status('task-1')
        assert status['exists'] is True
        assert status['status'] == 'pending'
        assert status['task_type'] == 'audit'
        assert status['result'] is None

    def test_get_task_status_for_running_task(self, service):
        service.register_agent('agent-1', 'audit', [])
        service.assign_task('task-1', 'agent-1', 'audit', {})
        service.start_task('task-1')
        status = service.get_task_status('task-1')
        assert status['status'] == 'running'

    def test_get_task_status_for_completed_task(self, service):
        service.register_agent('agent-1', 'audit', [])
        service.assign_task('task-1', 'agent-1', 'audit', {})
        service.complete_task('task-1', {'done': True})
        status = service.get_task_status('task-1')
        assert status['status'] == 'completed'
        assert status['result'] == {'done': True}

    def test_get_task_status_for_nonexistent_task(self, service):
        status = service.get_task_status('nobody')
        assert status['exists'] is False


class TestGetAgentStatus:
    def test_get_agent_status_for_available_agent(self, service):
        service.register_agent('agent-1', 'audit', ['a', 'b'])
        status = service.get_agent_status('agent-1')
        assert status['exists'] is True
        assert status['status'] == 'available'
        assert status['current_task'] is None
        assert status['capabilities'] == ['a', 'b']

    def test_get_agent_status_for_busy_agent(self, service):
        service.register_agent('agent-1', 'audit', [])
        service.assign_task('task-1', 'agent-1', 'audit', {})
        status = service.get_agent_status('agent-1')
        assert status['status'] == 'busy'
        assert status['current_task'] == 'task-1'

    def test_get_agent_status_for_nonexistent_agent(self, service):
        status = service.get_agent_status('ghost')
        assert status['exists'] is False


class TestListAgents:
    def test_list_all_agents(self, service):
        service.register_agent('a1', 'audit', [])
        service.register_agent('a2', 'fraud', [])
        agents = service.list_agents()
        assert len(agents) == 2

    def test_list_agents_filtered_by_status(self, service):
        service.register_agent('a1', 'audit', [])
        service.register_agent('a2', 'fraud', [])
        service.register_agent('a3', 'compliance', [])
        service.assign_task('t1', 'a1', 'audit', {})
        available = service.list_agents(status='available')
        busy = service.list_agents(status='busy')
        assert len(available) == 2
        assert len(busy) == 1

    def test_list_agents_with_unmatched_status_returns_empty(self, service):
        service.register_agent('a1', 'audit', [])
        result = service.list_agents(status='nonexistent')
        assert result == []

    def test_list_agents_when_no_agents_registered(self, service):
        assert service.list_agents() == []


class TestGetPendingTasks:
    def test_get_pending_tasks_returns_pending_only(self, service):
        service.register_agent('a1', 'audit', [])
        service.assign_task('t1', 'a1', 'audit', {})
        service.assign_task('t2', 'a1', 'audit', {})
        service.start_task('t1')
        pending = service.get_pending_tasks()
        assert len(pending) == 1
        assert pending[0]['task_id'] == 't2'

    def test_get_pending_tasks_empty_when_none_pending(self, service):
        assert service.get_pending_tasks() == []


class TestGetRunningTasks:
    def test_get_running_tasks_returns_running_only(self, service):
        service.register_agent('a1', 'audit', [])
        service.assign_task('t1', 'a1', 'audit', {})
        service.assign_task('t2', 'a1', 'audit', {})
        service.start_task('t1')
        running = service.get_running_tasks()
        assert len(running) == 1
        assert running[0]['task_id'] == 't1'

    def test_get_running_tasks_empty_when_none_running(self, service):
        assert service.get_running_tasks() == []


class TestCancelTask:
    def test_cancel_pending_task_returns_true(self, service):
        service.register_agent('agent-1', 'audit', [])
        service.assign_task('task-1', 'agent-1', 'audit', {})
        result = service.cancel_task('task-1')
        assert result is True
        task = next(t for t in service.task_queue if t['task_id'] == 'task-1')
        assert task['status'] == 'cancelled'

    def test_cancel_task_frees_the_agent(self, service):
        service.register_agent('agent-1', 'audit', [])
        service.assign_task('task-1', 'agent-1', 'audit', {})
        service.cancel_task('task-1')
        agent = service.agent_registry['agent-1']
        assert agent['status'] == 'available'
        assert agent['current_task'] is None

    def test_cancel_non_existent_task_returns_false(self, service):
        result = service.cancel_task('nonexistent')
        assert result is False

    def test_cancel_already_completed_task_returns_true(self, service):
        service.register_agent('agent-1', 'audit', [])
        service.assign_task('task-1', 'agent-1', 'audit', {})
        service.complete_task('task-1', {})
        result = service.cancel_task('task-1')
        assert result is True
        task = next(t for t in service.task_queue if t['task_id'] == 'task-1')
        assert task['status'] == 'cancelled'


class TestOrchestrateMultiAgentWorkflow:
    def test_single_step_workflow(self, service):
        service.register_agent('agent-1', 'audit', ['analysis'])
        steps = [
            {'step_id': 's1', 'agent_id': 'agent-1', 'type': 'analysis', 'task_data': {'q': 'test'}},
        ]
        result = service.orchestrate_multi_agent_workflow('wf-1', steps)
        assert result['workflow_id'] == 'wf-1'
        assert result['status'] == 'completed'
        assert len(result['steps']) == 1
        assert result['final_result']['total_steps'] == 1
        assert result['final_result']['successful_steps'] == 1

    def test_multi_step_workflow_with_multiple_agents(self, service):
        service.register_agent('agent-a', 'audit', [])
        service.register_agent('agent-b', 'fraud', [])
        steps = [
            {'step_id': 's1', 'agent_id': 'agent-a', 'type': 'analysis', 'task_data': {}},
            {'step_id': 's2', 'agent_id': 'agent-b', 'type': 'detection', 'task_data': {}},
        ]
        result = service.orchestrate_multi_agent_workflow('wf-2', steps)
        assert result['status'] == 'completed'
        assert len(result['steps']) == 2
        assert result['final_result']['total_steps'] == 2
        assert result['final_result']['successful_steps'] == 2

    def test_empty_steps_returns_zero_total(self, service):
        result = service.orchestrate_multi_agent_workflow('wf-empty', [])
        assert result['status'] == 'completed'
        assert result['final_result']['total_steps'] == 0
        assert result['final_result']['successful_steps'] == 0
