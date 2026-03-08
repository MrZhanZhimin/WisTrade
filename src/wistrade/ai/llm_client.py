"""
LLM client for GLM-4.7 integration
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from openai import OpenAI
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class LLMResponse(BaseModel):
    """LLM response structure"""
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str


class AIClient(ABC):
    """Abstract base class for AI clients"""
    
    @abstractmethod
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs,
    ) -> LLMResponse:
        """Generate chat completion"""
        pass
    
    @abstractmethod
    def stream_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs,
    ):
        """Stream chat completion"""
        pass


class GLMClient(AIClient):
    """
    GLM-4.7 client using Zhipu AI API
    
    Provides OpenAI-compatible interface to GLM models.
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "glm-4-plus",
        base_url: str = "https://open.bigmodel.cn/api/paas/v4",
        timeout: int = 60,
    ):
        """
        Initialize GLM client
        
        Args:
            api_key: Zhipu AI API key
            model: Model name (glm-4-plus, glm-4, etc.)
            base_url: API base URL
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        
        # Initialize OpenAI client with GLM endpoint
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
        )
        
        logger.info(f"GLM client initialized: model={model}")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs,
    ) -> LLMResponse:
        """
        Generate chat completion using GLM-4.7
        
        Args:
            messages: Chat messages (role, content)
            model: Override default model
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
            **kwargs: Additional parameters
        
        Returns:
            LLM response
        
        Raises:
            RuntimeError: If API call fails
        """
        try:
            response = self.client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
            
            # Extract response
            choice = response.choices[0]
            
            return LLMResponse(
                content=choice.message.content,
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                finish_reason=choice.finish_reason,
            )
            
        except Exception as e:
            logger.error(f"GLM API call failed: {e}")
            raise RuntimeError(f"GLM API error: {e}")
    
    def stream_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs,
    ):
        """
        Stream chat completion
        
        Args:
            messages: Chat messages
            model: Override default model
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            **kwargs: Additional parameters
        
        Yields:
            Chunks of response content
        """
        try:
            stream = self.client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs,
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"GLM streaming failed: {e}")
            raise RuntimeError(f"GLM streaming error: {e}")
    
    def analyze_market(
        self,
        symbol: str,
        market_data: Dict[str, Any],
        fundamentals: Dict[str, Any],
        sentiment: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Analyze stock using GLM
        
        Args:
            symbol: Stock symbol
            market_data: Market data (OHLCV, indicators)
            fundamentals: Fundamental data (PE, PB, ROE, etc.)
            sentiment: Sentiment data (news, social)
        
        Returns:
            Analysis result
        """
        # Build analysis prompt
        prompt = f"""
你是一位专业的股票分析师。请分析以下股票的投资价值：

股票代码: {symbol}

技术指标:
- 当前价格: {market_data.get('current_price')}
- 52周最高: {market_data.get('high_52w')}
- 52周最低: {market_data.get('low_52w')}
- 成交量: {market_data.get('volume')}
- 换手率: {market_data.get('turnover_rate')}

基本面数据:
- 市盈率(PE): {fundamentals.get('pe_ratio')}
- 市净率(PB): {fundamentals.get('pb_ratio')}
- 净资产收益率(ROE): {fundamentals.get('roe')}
- 营收增长率: {fundamentals.get('revenue_growth')}
- 净利润增长率: {fundamentals.get('profit_growth')}

请从以下几个方面分析：
1. 技术面分析（趋势、支撑位、阻力位）
2. 基本面分析（估值、成长性、财务健康）
3. 风险提示
4. 投资建议（买入/持有/卖出）

请给出详细的分析报告。
"""
        
        messages = [
            {"role": "system", "content": "你是一位资深的股票分析师，具有丰富的A股投资经验。"},
            {"role": "user", "content": prompt},
        ]
        
        response = self.chat_completion(messages, temperature=0.7)
        return response.content
    
    def generate_strategy(
        self,
        account_info: Dict[str, Any],
        risk_preference: str = "moderate",
        market_view: str = "neutral",
    ) -> str:
        """
        Generate trading strategy using GLM
        
        Args:
            account_info: Account information (capital, positions, etc.)
            risk_preference: Risk preference (conservative/moderate/aggressive)
            market_view: Market view (bullish/neutral/bearish)
        
        Returns:
            Strategy description
        """
        prompt = f"""
你是一位量化交易策略专家。请为以下账户生成适合的交易策略：

账户信息:
- 可用资金: {account_info.get('available_cash')} 元
- 持仓市值: {account_info.get('market_value')} 元
- 总资产: {account_info.get('total_assets')} 元
- 当前持仓: {account_info.get('positions')}

风险偏好: {risk_preference}
市场观点: {market_view}

请生成：
1. 策略名称和类型
2. 选股标准（技术指标+基本面）
3. 仓位管理规则
4. 止损止盈设置
5. 风险控制措施

请给出详细的策略描述。
"""
        
        messages = [
            {"role": "system", "content": "你是一位专业的量化交易策略师，擅长设计适合散户的自动化交易策略。"},
            {"role": "user", "content": prompt},
        ]
        
        response = self.chat_completion(messages, temperature=0.8)
        return response.content
