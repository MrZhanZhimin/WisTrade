"""
AI-powered trading strategy generator
"""

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from wistrade.ai.llm_client import AIClient
from wistrade.ai.stock_selector import StockCandidate

logger = logging.getLogger(__name__)


@dataclass
class TradingStrategy:
    """Generated trading strategy"""
    strategy_id: str
    name: str
    description: str
    strategy_type: str
    
    # Target stocks
    symbols: List[str]
    stock_selection_reasons: Dict[str, List[str]]
    
    # Position management
    position_sizing: str  # equal_weight, risk_parity, kelly
    max_position_pct: float
    min_position_pct: float
    
    # Entry rules
    entry_conditions: List[str]
    entry_timing: str  # immediate, on_pullback, on_breakout
    
    # Exit rules
    exit_conditions: List[str]
    stop_loss_pct: Optional[float]
    take_profit_pct: Optional[float]
    trailing_stop_pct: Optional[float]
    
    # Risk management
    max_drawdown_pct: float
    max_daily_loss_pct: float
    correlation_limit: float
    
    # Execution parameters
    order_type: str  # market, limit, vwap
    time_in_force: str  # day, gtc, ioc
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    confidence_score: float = 0.0
    risk_level: str = "moderate"
    expected_return: Optional[float] = None
    expected_volatility: Optional[float] = None


class StrategyGenerator:
    """
    AI-powered trading strategy generator
    
    Generates complete trading strategies with:
    - Stock selection
    - Entry/exit rules
    - Position sizing
    - Risk management
    """
    
    def __init__(self, llm_client: AIClient):
        """
        Initialize strategy generator
        
        Args:
            llm_client: LLM client for generation
        """
        self.llm = llm_client
    
    async def generate_strategy(
        self,
        account_id: str,
        selected_stocks: List[StockCandidate],
        available_capital: float,
        risk_preference: str = "moderate",
        investment_horizon: str = "medium_term",  # short_term, medium_term, long_term
        market_view: str = "neutral",  # bullish, neutral, bearish
        custom_constraints: Optional[Dict[str, Any]] = None,
    ) -> TradingStrategy:
        """
        Generate trading strategy based on selected stocks
        
        Args:
            account_id: Trading account ID
            selected_stocks: Selected stock candidates
            available_capital: Available capital
            risk_preference: Risk preference
            investment_horizon: Investment time horizon
            market_view: Market outlook
            custom_constraints: Additional constraints
        
        Returns:
            Generated trading strategy
        """
        logger.info(
            f"Generating strategy: {len(selected_stocks)} stocks, "
            f"capital={available_capital}, risk={risk_preference}"
        )
        
        # Generate strategy using LLM
        prompt = self._build_strategy_prompt(
            selected_stocks,
            available_capital,
            risk_preference,
            investment_horizon,
            market_view,
            custom_constraints,
        )
        
        messages = [
            {"role": "system", "content": "你是一位专业的量化策略师，擅长设计风险可控的交易策略。"},
            {"role": "user", "content": prompt},
        ]
        
        response = self.llm.chat_completion(messages, temperature=0.8)
        
        # Parse strategy from response
        strategy = self._parse_strategy(response.content, selected_stocks)
        
        # Validate strategy
        self._validate_strategy(strategy, available_capital)
        
        logger.info(f"Strategy generated: {strategy.name}")
        
        return strategy
    
    def _build_strategy_prompt(
        self,
        stocks: List[StockCandidate],
        capital: float,
        risk_pref: str,
        horizon: str,
        view: str,
        constraints: Optional[Dict],
    ) -> str:
        """Build strategy generation prompt"""
        
        stocks_info = "\n".join([
            f"- {s.symbol} {s.name}: 评分 {s.score}, "
            f"当前价 {s.current_price:.2f}, "
            f"目标价 {s.target_price or 'N/A'}, "
            f"止损价 {s.stop_loss or 'N/A'}"
            for s in stocks
        ])
        
        return f"""
请为以下投资组合生成详细的交易策略：

## 账户信息
- 可用资金: {capital} 元
- 风险偏好: {risk_pref}
- 投资期限: {horizon}
- 市场观点: {view}
- 自定义约束: {constraints or '无'}

## 已选股票
{stocks_info}

## 策略要求
1. **仓位管理**: 合理分配资金到各只股票
2. **入场规则**: 明确的买入条件和时机
3. **出场规则**: 止盈止损策略
4. **风险控制**: 最大回撤、日损失限制
5. **执行方式**: 订单类型、有效期

请生成JSON格式的策略：

```json
{{
  "name": "策略名称",
  "description": "策略描述",
  "strategy_type": "类型(趋势跟踪/均值回归/多因子)",
  "position_sizing": "仓位分配方法",
  "max_position_pct": 20.0,
  "min_position_pct": 5.0,
  "entry_conditions": ["条件1", "条件2"],
  "entry_timing": "入场时机",
  "exit_conditions": ["条件1", "条件2"],
  "stop_loss_pct": 8.0,
  "take_profit_pct": 15.0,
  "trailing_stop_pct": 5.0,
  "max_drawdown_pct": 15.0,
  "max_daily_loss_pct": 5.0,
  "correlation_limit": 0.7,
  "order_type": "limit",
  "time_in_force": "day",
  "confidence_score": 75.0,
  "risk_level": "moderate",
  "expected_return": 12.0,
  "expected_volatility": 20.0
}}
```

请确保策略风险可控且符合用户的风险偏好。
"""
    
    def _parse_strategy(self, content: str, stocks: List[StockCandidate]) -> TradingStrategy:
        """Parse strategy from LLM response"""
        
        # Extract JSON
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', content)
        if not json_match:
            json_match = re.search(r'\{[\s\S]*\}', content)
        
        if not json_match:
            raise ValueError("No strategy JSON found in response")
        
        data = json.loads(json_match.group(1) if '```' in content else json_match.group(0))
        
        # Build strategy object
        strategy = TradingStrategy(
            strategy_id=f"strategy_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            name=data.get('name', 'AI Generated Strategy'),
            description=data.get('description', ''),
            strategy_type=data.get('strategy_type', 'ai_generated'),
            symbols=[s.symbol for s in stocks],
            stock_selection_reasons={s.symbol: s.reasons for s in stocks},
            position_sizing=data.get('position_sizing', 'equal_weight'),
            max_position_pct=data.get('max_position_pct', 20.0),
            min_position_pct=data.get('min_position_pct', 5.0),
            entry_conditions=data.get('entry_conditions', []),
            entry_timing=data.get('entry_timing', 'immediate'),
            exit_conditions=data.get('exit_conditions', []),
            stop_loss_pct=data.get('stop_loss_pct'),
            take_profit_pct=data.get('take_profit_pct'),
            trailing_stop_pct=data.get('trailing_stop_pct'),
            max_drawdown_pct=data.get('max_drawdown_pct', 15.0),
            max_daily_loss_pct=data.get('max_daily_loss_pct', 5.0),
            correlation_limit=data.get('correlation_limit', 0.7),
            order_type=data.get('order_type', 'limit'),
            time_in_force=data.get('time_in_force', 'day'),
            confidence_score=data.get('confidence_score', 0.0),
            risk_level=data.get('risk_level', 'moderate'),
            expected_return=data.get('expected_return'),
            expected_volatility=data.get('expected_volatility'),
        )
        
        return strategy
    
    def _validate_strategy(self, strategy: TradingStrategy, capital: float) -> None:
        """Validate strategy parameters"""
        
        # Check position limits
        if strategy.max_position_pct > 40:
            logger.warning("Max position > 40%, adjusting to 40%")
            strategy.max_position_pct = 40.0
        
        # Check risk limits
        if strategy.max_daily_loss_pct > 10:
            logger.warning("Max daily loss > 10%, adjusting to 10%")
            strategy.max_daily_loss_pct = 10.0
        
        if strategy.stop_loss_pct and strategy.stop_loss_pct > 20:
            logger.warning("Stop loss > 20%, adjusting to 20%")
            strategy.stop_loss_pct = 20.0
        
        # Ensure we have stocks
        if not strategy.symbols:
            raise ValueError("Strategy must have at least one stock")
        
        logger.info("Strategy validated successfully")
    
    async def optimize_strategy(
        self,
        strategy: TradingStrategy,
        performance_metrics: Dict[str, Any],
    ) -> TradingStrategy:
        """
        Optimize strategy based on performance feedback
        
        Args:
            strategy: Current strategy
            performance_metrics: Performance data
        
        Returns:
            Optimized strategy
        """
        prompt = f"""
当前策略表现：

策略名称: {strategy.name}
持仓股票: {strategy.symbols}

绩效指标:
- 总收益率: {performance_metrics.get('total_return', 0)}%
- 夏普比率: {performance_metrics.get('sharpe_ratio', 0)}
- 最大回撤: {performance_metrics.get('max_drawdown', 0)}%
- 胜率: {performance_metrics.get('win_rate', 0)}%

请分析当前策略的问题并提出优化建议：
1. 仓位管理是否需要调整
2. 止损止盈设置是否合理
3. 选股标准是否需要优化
4. 风险控制是否到位

请给出具体的优化方案（JSON格式）。
"""
        
        messages = [
            {"role": "system", "content": "你是一位策略优化专家，擅长根据历史表现改进交易策略。"},
            {"role": "user", "content": prompt},
        ]
        
        response = self.llm.chat_completion(messages, temperature=0.7)
        
        # TODO: Parse optimization suggestions and update strategy
        
        logger.info("Strategy optimization analysis complete")
        
        return strategy
