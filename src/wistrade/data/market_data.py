"""
Market data providers for Chinese stock market
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Optional

import akshare as ak
import pandas as pd

from wistrade.brokers.base import KLine, MarketData

logger = logging.getLogger(__name__)


class MarketDataProvider(ABC):
    """Abstract base class for market data providers"""
    
    @abstractmethod
    async def get_realtime_quote(self, symbol: str) -> MarketData:
        """Get real-time market quote"""
        pass
    
    @abstractmethod
    async def get_historical_klines(
        self,
        symbol: str,
        interval: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[KLine]:
        """Get historical K-line data"""
        pass
    
    @abstractmethod
    async def get_stock_list(self) -> List[dict]:
        """Get list of all stocks"""
        pass
    
    @abstractmethod
    async def search_stocks(self, keyword: str) -> List[dict]:
        """Search stocks by keyword"""
        pass


class AkShareProvider(MarketDataProvider):
    """
    Market data provider using AkShare
    
    AkShare is a free, open-source library for Chinese financial market data.
    No API key required.
    """
    
    def __init__(self):
        """Initialize AkShare provider"""
        self._stock_list_cache: Optional[List[dict]] = None
        self._cache_time: Optional[datetime] = None
    
    async def get_realtime_quote(self, symbol: str) -> MarketData:
        """
        Get real-time market quote from AkShare
        
        Args:
            symbol: Stock symbol (e.g., "000001" for 平安银行)
        
        Returns:
            Market data
        """
        try:
            # Remove exchange prefix if present
            symbol_code = symbol.split('.')[-1]
            
            # Get real-time data
            df = ak.stock_zh_a_spot_em()
            
            # Find the stock
            stock_data = df[df['代码'] == symbol_code]
            
            if stock_data.empty:
                raise ValueError(f"Stock not found: {symbol}")
            
            row = stock_data.iloc[0]
            
            return MarketData(
                symbol=symbol,
                name=row['名称'],
                current_price=float(row['最新价']),
                open_price=float(row['今开']),
                high_price=float(row['最高']),
                low_price=float(row['最低']),
                previous_close=float(row['昨收']),
                volume=int(row['成交量']),
                turnover=float(row['成交额']),
                timestamp=datetime.now(),
            )
            
        except Exception as e:
            logger.error(f"Failed to get real-time quote for {symbol}: {e}")
            raise
    
    async def get_historical_klines(
        self,
        symbol: str,
        interval: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[KLine]:
        """
        Get historical K-line data from AkShare
        
        Args:
            symbol: Stock symbol
            interval: Time interval (1d, 1w, 1M)
            start_date: Start date (optional)
            end_date: End date (optional)
            limit: Maximum number of candles
        
        Returns:
            List of K-line data
        """
        try:
            symbol_code = symbol.split('.')[-1]
            
            # Map interval to AkShare period
            period_map = {
                '1d': 'daily',
                '1w': 'weekly',
                '1M': 'monthly',
            }
            period = period_map.get(interval, 'daily')
            
            # Set default date range if not provided
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=limit * 2)
            
            # Get historical data
            df = ak.stock_zh_a_hist(
                symbol=symbol_code,
                period=period,
                start_date=start_date.strftime('%Y%m%d'),
                end_date=end_date.strftime('%Y%m%d'),
                adjust="qfq",  # 前复权
            )
            
            # Convert to KLine objects
            klines = []
            for idx, row in df.iterrows():
                klines.append(KLine(
                    symbol=symbol,
                    timestamp=pd.to_datetime(row['日期']),
                    open_price=float(row['开盘']),
                    high_price=float(row['最高']),
                    low_price=float(row['最低']),
                    close_price=float(row['收盘']),
                    volume=int(row['成交量']),
                    turnover=float(row['成交额']),
                    interval=interval,
                ))
            
            # Return last 'limit' items
            return klines[-limit:] if len(klines) > limit else klines
            
        except Exception as e:
            logger.error(f"Failed to get historical K-lines for {symbol}: {e}")
            raise
    
    async def get_stock_list(self) -> List[dict]:
        """
        Get list of all A-share stocks from AkShare
        
        Returns:
            List of stock dictionaries with symbol, name, etc.
        """
        try:
            # Check cache (refresh every 6 hours)
            if (self._stock_list_cache and self._cache_time and 
                (datetime.now() - self._cache_time) < timedelta(hours=6)):
                return self._stock_list_cache
            
            # Get all A-share stocks
            df = ak.stock_zh_a_spot_em()
            
            stocks = []
            for idx, row in df.iterrows():
                stocks.append({
                    'symbol': row['代码'],
                    'name': row['名称'],
                    'price': float(row['最新价']),
                    'change_pct': float(row['涨跌幅']),
                    'volume': int(row['成交量']),
                    'turnover': float(row['成交额']),
                    'market_cap': float(row.get('总市值', 0)),
                })
            
            # Update cache
            self._stock_list_cache = stocks
            self._cache_time = datetime.now()
            
            logger.info(f"Loaded {len(stocks)} stocks from AkShare")
            return stocks
            
        except Exception as e:
            logger.error(f"Failed to get stock list: {e}")
            raise
    
    async def search_stocks(self, keyword: str) -> List[dict]:
        """
        Search stocks by keyword (name or symbol)
        
        Args:
            keyword: Search keyword
        
        Returns:
            List of matching stocks
        """
        try:
            all_stocks = await self.get_stock_list()
            
            # Search by symbol or name
            keyword_lower = keyword.lower()
            matches = [
                stock for stock in all_stocks
                if keyword_lower in stock['symbol'].lower()
                or keyword_lower in stock['name'].lower()
            ]
            
            return matches[:20]  # Return top 20 matches
            
        except Exception as e:
            logger.error(f"Failed to search stocks: {e}")
            raise
    
    async def get_financial_indicator(self, symbol: str) -> dict:
        """
        Get financial indicators for fundamental analysis
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Dictionary of financial indicators
        """
        try:
            symbol_code = symbol.split('.')[-1]
            
            # Get financial indicators
            df = ak.stock_financial_analysis_indicator(symbol=symbol_code)
            
            if df.empty:
                return {}
            
            # Get latest data
            latest = df.iloc[0]
            
            return {
                'pe_ratio': float(latest.get('市盈率', 0)),
                'pb_ratio': float(latest.get('市净率', 0)),
                'roe': float(latest.get('净资产收益率', 0)),
                'revenue_growth': float(latest.get('营业收入增长率', 0)),
                'profit_growth': float(latest.get('净利润增长率', 0)),
                'gross_margin': float(latest.get('销售毛利率', 0)),
                'net_margin': float(latest.get('销售净利率', 0)),
                'debt_ratio': float(latest.get('资产负债率', 0)),
            }
            
        except Exception as e:
            logger.error(f"Failed to get financial indicators for {symbol}: {e}")
            return {}


class TushareProvider(MarketDataProvider):
    """
    Market data provider using Tushare Pro API
    
    Tushare requires an API token. Get one from: https://tushare.pro/
    """
    
    def __init__(self, token: str):
        """
        Initialize Tushare provider
        
        Args:
            token: Tushare API token
        """
        import tushare as ts
        ts.set_token(token)
        self._pro = ts.pro_api()
        self._stock_list_cache: Optional[List[dict]] = None
    
    async def get_realtime_quote(self, symbol: str) -> MarketData:
        """
        Get real-time market quote from Tushare
        
        Args:
            symbol: Stock symbol (e.g., "000001.SZ")
        
        Returns:
            Market data
        """
        try:
            # Get daily data (Tushare doesn't have real-time)
            df = self._pro.daily(ts_code=symbol, limit=1)
            
            if df.empty:
                raise ValueError(f"Stock not found: {symbol}")
            
            row = df.iloc[0]
            
            # Get previous day for comparison
            prev_df = self._pro.daily(ts_code=symbol, limit=2)
            prev_close = prev_df.iloc[1]['close'] if len(prev_df) > 1 else row['open']
            
            return MarketData(
                symbol=symbol,
                name="",  # Will fetch separately if needed
                current_price=float(row['close']),
                open_price=float(row['open']),
                high_price=float(row['high']),
                low_price=float(row['low']),
                previous_close=float(prev_close),
                volume=int(row['vol']),
                turnover=float(row['amount']),
                timestamp=datetime.now(),
            )
            
        except Exception as e:
            logger.error(f"Failed to get real-time quote for {symbol}: {e}")
            raise
    
    async def get_historical_klines(
        self,
        symbol: str,
        interval: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[KLine]:
        """
        Get historical K-line data from Tushare
        
        Args:
            symbol: Stock symbol
            interval: Time interval (1d, 1w, 1M)
            start_date: Start date (optional)
            end_date: End date (optional)
            limit: Maximum number of candles
        
        Returns:
            List of K-line data
        """
        try:
            # Set default date range
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=limit * 2)
            
            # Get data based on interval
            if interval == '1d':
                df = self._pro.daily(
                    ts_code=symbol,
                    start_date=start_date.strftime('%Y%m%d'),
                    end_date=end_date.strftime('%Y%m%d'),
                )
            elif interval == '1w':
                df = self._pro.weekly(
                    ts_code=symbol,
                    start_date=start_date.strftime('%Y%m%d'),
                    end_date=end_date.strftime('%Y%m%d'),
                )
            elif interval == '1M':
                df = self._pro.monthly(
                    ts_code=symbol,
                    start_date=start_date.strftime('%Y%m%d'),
                    end_date=end_date.strftime('%Y%m%d'),
                )
            else:
                raise ValueError(f"Unsupported interval: {interval}")
            
            # Convert to KLine objects
            klines = []
            for idx, row in df.iterrows():
                klines.append(KLine(
                    symbol=symbol,
                    timestamp=pd.to_datetime(row['trade_date']),
                    open_price=float(row['open']),
                    high_price=float(row['high']),
                    low_price=float(row['low']),
                    close_price=float(row['close']),
                    volume=int(row['vol']),
                    turnover=float(row['amount']),
                    interval=interval,
                ))
            
            # Sort by timestamp and return last 'limit' items
            klines.sort(key=lambda x: x.timestamp)
            return klines[-limit:] if len(klines) > limit else klines
            
        except Exception as e:
            logger.error(f"Failed to get historical K-lines for {symbol}: {e}")
            raise
    
    async def get_stock_list(self) -> List[dict]:
        """
        Get list of all stocks from Tushare
        
        Returns:
            List of stock dictionaries
        """
        try:
            if self._stock_list_cache:
                return self._stock_list_cache
            
            # Get stock basic info
            df = self._pro.stock_basic(exchange='', list_status='L')
            
            stocks = []
            for idx, row in df.iterrows():
                stocks.append({
                    'symbol': row['ts_code'],
                    'name': row['name'],
                    'exchange': row['exchange'],
                    'industry': row.get('industry', ''),
                    'market': row.get('market', ''),
                })
            
            self._stock_list_cache = stocks
            logger.info(f"Loaded {len(stocks)} stocks from Tushare")
            return stocks
            
        except Exception as e:
            logger.error(f"Failed to get stock list: {e}")
            raise
    
    async def search_stocks(self, keyword: str) -> List[dict]:
        """Search stocks by keyword"""
        try:
            all_stocks = await self.get_stock_list()
            
            keyword_lower = keyword.lower()
            matches = [
                stock for stock in all_stocks
                if keyword_lower in stock['symbol'].lower()
                or keyword_lower in stock['name'].lower()
            ]
            
            return matches[:20]
            
        except Exception as e:
            logger.error(f"Failed to search stocks: {e}")
            raise
    
    async def get_financial_indicator(self, symbol: str) -> dict:
        """
        Get financial indicators from Tushare
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Dictionary of financial indicators
        """
        try:
            df = self._pro.fina_indicator(ts_code=symbol)
            
            if df.empty:
                return {}
            
            latest = df.iloc[0]
            
            return {
                'pe_ratio': float(latest.get('pe', 0)),
                'pb_ratio': float(latest.get('pb', 0)),
                'roe': float(latest.get('roe', 0)),
                'revenue_growth': float(latest.get('or_yoy', 0)),
                'profit_growth': float(latest.get('profit_yoy', 0)),
                'gross_margin': float(latest.get('grossprofit_margin', 0)),
                'net_margin': float(latest.get('netprofit_margin', 0)),
                'debt_ratio': float(latest.get('debt_to_assets', 0)),
            }
            
        except Exception as e:
            logger.error(f"Failed to get financial indicators for {symbol}: {e}")
            return {}
