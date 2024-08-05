from unittest.mock import patch

from app.task.job_charger import oneshot as test_module


@patch(f"{test_module.__name__}.charge_oneshot")
async def test_periodic_oneshot_charger_run_forever(mock_charge_oneshot):
    task = test_module.PeriodicOneshotCharger(name="test-oneshot-charger")
    await task.run_forever(limit=1)
    assert mock_charge_oneshot.call_count == 1
    assert task.get_stats() == {
        "counter": 1,
        "success": 1,
        "failure": 0,
    }

    mock_charge_oneshot.reset_mock()
    mock_charge_oneshot.side_effect = Exception("Test error")
    task.reset_stats()
    await task.run_forever(limit=1)
    assert mock_charge_oneshot.call_count == 1
    assert task.get_stats() == {
        "counter": 1,
        "success": 0,
        "failure": 1,
    }
