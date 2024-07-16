from unittest.mock import patch

from app.tasks.job_charger import short_jobs as test_module


@patch(f"{test_module.__name__}.charge_short_jobs")
async def test_periodic_short_jobs_charger_run_forever(mock_charge_short_jobs):
    task = test_module.PeriodicShortJobsCharger(name="test-short-jobs-charger")
    await task.run_forever(limit=1)
    assert mock_charge_short_jobs.call_count == 1
    assert task.get_stats() == {
        "counter": 1,
        "success": 1,
        "failure": 0,
    }

    mock_charge_short_jobs.reset_mock()
    mock_charge_short_jobs.side_effect = Exception("Test error")
    task.reset_stats()
    await task.run_forever(limit=1)
    assert mock_charge_short_jobs.call_count == 1
    assert task.get_stats() == {
        "counter": 1,
        "success": 0,
        "failure": 1,
    }
