"""
AI-powered stock selection system
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from wistrade.ai.llm_client import AIClient
from wistrade.data.market_data import AkShareProvider, TushareProvider

logger = logging.getLogger(__name__)


@dataclass
class StockCandidate:
    """Stock candidate for selection"""
    symbol: str
    name: str
    score: float
    reasons: List[str]
    technical_score: float
    fundamental_score: float
    sentiment_score: float
    risk_level: str
    current_price: float
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None


class StockSelector:
    """
    AI-powered stock selection system
    
    Analyzes stocks using:
    - Technical indicators (RSI, MACD, moving averages)
    - Fundamental data (PE, PB, ROE, growth)
    - Market sentiment (news, trends)
    - Risk assessment (volatility, liquidity)
    """
    
    def __init__(
        self,
        llm_client: AIClient,
        data_provider: Optional[Any] = None,
    ):
        """
        Initialize stock selector
        
        Args:
            llm_client: LLM client for analysis
            data_provider: Market data provider (AkShare/Tushare)
        """
        self.llm = llm_client
        self.data_provider = data_provider or AkShareProvider()
    
    async def select_stocks(
        self,
        account_id: str,
        available_capital: float,
        max_positions: int = 5,
        risk_preference: str = "moderate",
        sector_preference: Optional[List[str]] = None,
        exclude_symbols: Optional[List[str]] = None,
    ) -> List[StockCandidate]:
        """
        Select stocks for trading
        
        Args:
            account_id: Trading account ID
            available_capital: Available capital for investment
            max_positions: Maximum number of positions
            risk_preference: Risk preference (conservative/moderate/aggressive)
            sector_preference: Preferred sectors (optional)
            exclude_symbols: Symbols to exclude (already held)
        
        Returns:
            List of stock candidates sorted by score
        """
        logger.info(
            f"Starting stock selection: capital={available_capital}, "
            f"max_positions={max_positions}, risk={risk_preference}"
        )
        
        # Step 1: Get market data
        all_stocks = await self.data_provider.get_stock_list()
        logger.info(f"Total stocks in market: {len(all_stocks)}")
        
        # Step 2: Initial filtering (remove ST, delisted, etc.)
        filtered_stocks = self._initial_filter(all_stocks, exclude_symbols)
        logger.info(f"After initial filter: {len(filtered_stocks)} stocks")
        
        # Step 3: Technical screening
        technical_candidates = await self._technical_screening(filtered_stocks)
        logger.info(f"Technical candidates: {len(technical_candidates)}")
        
        # Step 4: Fundamental analysis
        fundamental_candidates = await self._fundamental_analysis(technical_candidates)
        logger.info(f"Fundamental candidates: {len(fundamental_candidates)}")
        
        # Step 5: AI scoring and ranking
        scored_candidates = await self._ai_scoring(
            fundamental_candidates,
            available_capital,
            max_positions,
            risk_preference,
            sector_preference,
        )
        
        logger.info(f"Final candidates: {len(scored_candidates)}")
        
        return scored_candidates[:max_positions]
    
    def _initial_filter(
        self,
        stocks: List[Dict],
        exclude_symbols: Optional[List[str]] = None,
    ) -> List[Dict]:
        """Initial filtering to remove unsuitable stocks"""
        filtered = []
        exclude_set = set(exclude_symbols or [])
        
        for stock in stocks:
            symbol = stock.get('symbol', '')
            name = stock.get('name', '')
            
            # Skip excluded symbols
            if symbol in exclude_set:
                continue
            
            # Skip ST stocks
            if 'ST' in name or 'st' in name:
                continue
            
            # Skip delisted stocks (marked with 退)
            if '退' in name:
                continue
            
            # Skip very low priced stocks (< 2 yuan)
            price = stock.get('price', 0)
            if price < 2.0:
                continue
            
            # Skip very high volatility (if available)
            # TODO: Add volatility filter
            
            filtered.append(stock)
        
        return filtered
    
    async def _technical_screening(self, stocks: List[Dict]) -> List[Dict]:
        """Technical indicator screening"""
        candidates = []
        
        for stock in stocks[:500]:  # Limit for performance
            try:
                symbol = stock['symbol']
                
                # Get technical data
                # TODO: Implement actual technical analysis
                # For now, use simple heuristics
                
                # Skip if no volume
                volume = stock.get('volume', 0)
                if volume < 1000000:  # Less than 1M shares
                    continue
                
                # Add to candidates
                candidates.append(stock)
                
            except Exception as e:
                logger.debug(f"Technical screening failed for {stock.get('symbol')}: {e}")
        
        return candidates
    
    async def _fundamental_analysis(self, stocks: List[Dict]) -> List[Dict]:
        """Fundamental data analysis"""
        candidates = []
        
        for stock in stocks[:200]:  # Limit for performance
            try:
                symbol = stock['symbol']
                
                # Get fundamental data
                fundamentals = await self.data_provider.get_financial_indicator(symbol)
                
                if not fundamentals:
                    continue
                
                # Basic fundamental filters
                pe_ratio = fundamentals.get('pe_ratio', 0)
                pb_ratio = fundamentals.get('pb_ratio', 0)
                roe = fundamentals.get('roe', 0)
                
                # Filter by valuation
                if pe_ratio <= 0 or pe_ratio > 100:  # Unreasonable PE
                    continue
                
                if pb_ratio <= 0 or pb_ratio > 10:  # Overvalued
                    continue
                
                if roe < 5:  # Poor profitability
                    continue
                
                # Add fundamentals to stock data
                stock['fundamentals'] = fundamentals
                candidates.append(stock)
                
            except Exception as e:
                logger.debug(f"Fundamental analysis failed for {stock.get('symbol')}: {e}")
        
        return candidates
    
    async def _ai_scoring(
        self,
        stocks: List[Dict],
        available_capital: float,
        max_positions: int,
        risk_preference: str,
        sector_preference: Optional[List[str]],
    ) -> List[StockCandidate]:
        """Use AI to score and rank candidates"""
        
        # Prepare stock data for AI analysis
        stock_data = []
        for stock in stocks[:50]:  # Limit to top 50 for AI analysis
            stock_data.append({
                'symbol': stock['symbol'],
                'name': stock['name'],
                'price': stock.get('price', 0),
                'volume': stock.get('volume', 0),
                'turnover': stock.get('turnover', 0),
                'change_pct': stock.get('change_pct', 0),
                'fundamentals': stock.get('fundamentals', {}),
            })
        
        # Generate AI analysis
        prompt = f"""
你是一位专业的股票分析师。请从以下股票中选出最值得投资的 {max_positions} 只股票。

可用资金: {available_capital} 元
风险偏好: {risk_preference}
行业偏好: {sector_preference or '无特定偏好'}

候选股票:
{self._format_stocks_for_ai(stock_data)}

请为每只股票打分（0-100分），并给出选择理由。

输出格式（JSON）:
{{
  "recommendations": [
    {{
      "symbol": "股票代码",
      "name": "股票名称",
      "score": 85,
      "reasons": ["理由1", "理由2"],
      "technical_score": 80,
      "fundamental_score": 90,
      "sentiment_score": 85,
      "risk_level": "moderate",
      "target_price": 12.50,
      "stop_loss": 10.00
    }}
  ]
}}

请给出JSON格式的分析结果。
"""
        
        messages = [
            {"role": "system", "content": "你是一位资深的量化分析师，擅长综合分析并给出客观评分。"},
            {"role": "user", "content": prompt},
        ]
        
        response = self.llm.chat_completion(messages, temperature=0.7)
        
        # Parse AI response
        candidates = self._parse_ai_response(response.content, stock_data)
        
        # Sort by score
        candidates.sort(key=lambda x: x.score, reverse=True)
        
        return candidates
    
    def _format_stocks_for_ai(self, stocks: List[Dict]) -> str:
        """Format stock data for AI prompt"""
        lines = []
        for i, stock in enumerate(stocks, 1):
            fund = stock.get('fundamentals', {})
            lines.append(
                f"{i}. {stock['symbol']} {stock['name']}\n"
                f"   价格: {stock['price']:.2f} | 成交量: {stock['volume']:,} | 涨跌幅: {stock['change_pct']:.2f}%\n"
                f"   PE: {fund.get('pe_ratio', 0):.2f} | PB: {fund.get('pb_ratio', 0):.2f} | ROE: {fund.get('roe', 0):.2f}%"
            )
        return "\n\n".join(lines)
    
    def _parse_ai_response(self, content: str, stock_data: List[Dict]) -> List[StockCandidate]:
        """Parse AI response into StockCandidate objects"""
        import json
        import re
        
        candidates = []
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                data = json.loads(json_match.group(0))
                
                for rec in data.get('recommendations', []):
                    # Find stock data
                    stock_info = next(
                        (s for s in stock_data if s['symbol'] == rec['symbol']),
                        {}
                    )
                    
                    candidate = StockCandidate(
                        symbol=rec['symbol'],
                        name=rec.get('name', stock_info.get('name', '')),
                        score=rec.get('score', 0),
                        reasons=rec.get('reasons', []),
                        technical_score=rec.get('technical_score', 0),
                        fundamental_score=rec.get('fundamental_score', 0),
                        sentiment_score=rec.get('sentiment_score', 0),
                        risk_level=rec.get('risk_level', 'moderate'),
                        current_price=stock_info.get('price', 0),
                        target_price=rec.get('target_price'),
                        stop_loss=rec.get('stop_loss'),
                    )
                    
                    candidates.append(candidate)
                    
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
        
        return candidates
