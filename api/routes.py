
# ===== STRATEGY API ENDPOINTS =====
from fastapi import HTTPException, Depends
from strategies.storage import save_strategy, list_strategies, get_strategy, delete_strategy, update_strategy
from strategies.dca import DCAStrategy
from api.dependencies import get_current_user

@router.post("/strategy/dca")
async def create_dca_strategy(
    symbol: str,
    amount: float,
    frequency: str = "daily",
    current_user: dict = Depends(get_current_user)
):
    """Create a new DCA strategy"""
    try:
        strategy = DCAStrategy(
            uid=current_user['user_id'],
            symbol=symbol,
            amount=amount,
            frequency=frequency
        )
        strategy_id = save_strategy(current_user['user_id'], strategy)
        return {
            "success": True,
            "strategy_id": strategy_id,
            "message": f"DCA strategy created for {symbol}"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/strategies")
async def get_user_strategies(current_user: dict = Depends(get_current_user)):
    """List all strategies for current user"""
    strategies = list_strategies(current_user['user_id'])
    return {"success": True, "strategies": strategies}

@router.delete("/strategy/{strategy_id}")
async def delete_user_strategy(
    strategy_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a strategy"""
    if delete_strategy(current_user['user_id'], strategy_id):
        return {"success": True, "message": "Strategy deleted"}
    raise HTTPException(status_code=404, detail="Strategy not found")
