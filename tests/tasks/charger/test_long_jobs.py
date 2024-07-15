from unittest.mock import patch

from app.tasks.charger import long_jobs as test_module


@patch(f"{test_module.__name__}.charge_long_jobs")
async def test_periodic_long_jobs_charger_run_forever(mock_charge_long_jobs):
    task = test_module.PeriodicLongJobsCharger(name="test-long-jobs-charger")
    await task.run_forever(limit=1)
    assert mock_charge_long_jobs.call_count == 1
    assert task.get_stats() == {
        "counter": 1,
        "success": 1,
        "failure": 0,
    }

    mock_charge_long_jobs.reset_mock()
    mock_charge_long_jobs.side_effect = Exception("Test error")
    task.reset_stats()
    await task.run_forever(limit=1)
    assert mock_charge_long_jobs.call_count == 1
    assert task.get_stats() == {
        "counter": 1,
        "success": 0,
        "failure": 1,
    }
