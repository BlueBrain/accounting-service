from unittest.mock import patch

from app.tasks.job_charger import storage as test_module


@patch(f"{test_module.__name__}.charge_storage_jobs")
async def test_periodic_storage_charger_run_forever(mock_charge_storage_jobs):
    task = test_module.PeriodicStorageCharger(name="test-storage-charger")
    await task.run_forever(limit=1)
    assert mock_charge_storage_jobs.call_count == 1
    assert task.get_stats() == {
        "counter": 1,
        "success": 1,
        "failure": 0,
    }

    mock_charge_storage_jobs.reset_mock()
    mock_charge_storage_jobs.side_effect = Exception("Test error")
    task.reset_stats()
    await task.run_forever(limit=1)
    assert mock_charge_storage_jobs.call_count == 1
    assert task.get_stats() == {
        "counter": 1,
        "success": 0,
        "failure": 1,
    }
