import pytest
from unittest.mock import AsyncMock
from src.adapters.resilience.circuit_breaker import CircuitBreaker, CircuitBreakerOpenException, CircuitState

@pytest.mark.asyncio
async def test_circuit_breaker_closed_success():
    cb = CircuitBreaker()
    func = AsyncMock(return_value="success")
    
    res = await cb.call(func)
    assert res == "success"
    assert cb.state == CircuitState.CLOSED
    assert cb.failures == 0

@pytest.mark.asyncio
async def test_circuit_breaker_opens_on_failures():
    cb = CircuitBreaker(failure_threshold=2)
    func = AsyncMock(side_effect=ValueError("fail"))
    
    # 1st failure
    with pytest.raises(ValueError):
        await cb.call(func)
    assert cb.state == CircuitState.CLOSED
    
    # 2nd failure -> Open
    with pytest.raises(ValueError):
        await cb.call(func)
    assert cb.state == CircuitState.OPEN

    # 3rd call -> Fast fail
    with pytest.raises(CircuitBreakerOpenException):
        await cb.call(func)

@pytest.mark.asyncio
async def test_circuit_breaker_recovery():
    cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.1)
    func = AsyncMock(side_effect=ValueError("fail"))
    
    # Fail to Open
    with pytest.raises(ValueError):
        await cb.call(func)
    assert cb.state == CircuitState.OPEN
    
    import time
    time.sleep(0.2)
    
    # Next call -> Half Open -> Success -> Closed
    func.side_effect = None
    func.return_value = "recovered"
    
    res = await cb.call(func)
    assert res == "recovered"
    assert cb.state == CircuitState.CLOSED
    assert cb.failures == 0
