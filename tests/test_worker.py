import os
import pytest
import importlib
from unittest.mock import patch
from app import worker
from app.worker import celery_app

@pytest.fixture(scope='session')
def celery_config():
    return {
        'broker_url': 'memory://',
        'result_backend': 'cache+memory://',
        'task_always_eager': True,
        'task_eager_propagates': True,
    }

def test_tasks_registration():
    registered_tasks = celery_app.tasks.keys()
    assert "master_fetch_task" in registered_tasks
    assert "save_chunk_to_csv" in registered_tasks

def test_celery_config_init():
    assert celery_app.main == "worker"
    assert celery_app.conf.broker_url is not None


def test_celery_broker_url_from_env():
    expected_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
    assert celery_app.conf.broker_url.rstrip('/') == expected_url.rstrip('/')


def test_celery_broker_url_configured():
    assert "redis://" in celery_app.conf.broker_url


def test_celery_broker_invalid_protocol():
    invalid_url = "not_redis://localhost:6379/0"

    with patch.dict(os.environ, {"CELERY_BROKER_URL": invalid_url}):
        importlib.reload(worker)

        assert worker.celery_app.conf.broker_url == invalid_url


def test_celery_default_values_when_env_missing():
    with patch.dict(os.environ, {}, clear=True):
        importlib.reload(worker)
        assert "localhost" in worker.celery_app.conf.broker_url
        assert "localhost" in worker.celery_app.conf.result_backend


def test_autodiscover_failure_handling():
    from celery import Celery
    test_app = Celery("test_worker_isolated")

    try:
        test_app.autodiscover_tasks(['non_existent_folder'])
    except Exception as e:
        pytest.fail(f"autodiscover_tasks raised an exception: {e}")


@patch("celery.app.base.Celery.autodiscover_tasks")
def test_autodiscover_called_correctly(mock_autodiscover):
    from app import worker
    import importlib
    importlib.reload(worker)
    mock_autodiscover.assert_called()
    args, _ = mock_autodiscover.call_args
    assert 'app' in args[0]