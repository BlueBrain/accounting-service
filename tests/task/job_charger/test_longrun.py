from unittest.mock import patch

from app.task.job_charger import longrun as test_module


@patch(f"{test_module.__name__}.charge_longrun")
async def test_periodic_longrun_charger_run_forever(mock_charge_longrun):
    task = test_module.PeriodicLongrunCharger(name="test-longrun-charger")
    await task.run_forever(limit=1)
    assert mock_charge_longrun.call_count == 1
    assert task.get_stats() == {
        "counter": 1,
        "success": 1,
        "failure": 0,
    }

    mock_charge_longrun.reset_mock()
    mock_charge_longrun.side_effect = Exception("Test error")
    task.reset_stats()
    await task.run_forever(limit=1)
    assert mock_charge_longrun.call_count == 1
    assert task.get_stats() == {
        "counter": 1,
        "success": 0,
        "failure": 1,
    }
