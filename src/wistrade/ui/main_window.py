"""
Main application window for WisTrade

PyQt6-based desktop interface with modern dark theme.
"""

import sys
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QStatusBar,
    QMessageBox,
    QFrame,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

from wistrade.ui.styles import COLORS, MAIN_WINDOW, format_currency
from wistrade.ui.pages.dashboard import DashboardPage

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    Main application window with modern dark theme
    
    Features:
    - Dark theme UI
    - Tabbed navigation
    - Real-time data updates
    - Service status monitoring
    """
    
    def __init__(self, app_manager=None):
        super().__init__()
        
        self.app_manager = app_manager
        
        # Window settings
        self.setWindowTitle("WisTrade - AI智能交易平台 v0.1.0")
        self.setGeometry(100, 100, 1600, 900)
        self.setMinimumSize(1280, 720)
        
        # Apply dark theme
        self.setStyleSheet(MAIN_WINDOW)
        
        # Initialize components
        self._init_ui()
        self._init_status_bar()
        self._init_timers()
        
        logger.info("Main window initialized")
    
    def _init_ui(self):
        """Initialize user interface"""
        # Central widget
        central_widget = QWidget()
        central_widget.setStyleSheet(f"background-color: {COLORS['bg_primary']};")
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Top bar
        top_bar = self._create_top_bar()
        main_layout.addWidget(top_bar)
        
        # Content area with tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background-color: {COLORS['bg_primary']};
            }}
            QTabBar::tab {{
                background-color: {COLORS['bg_secondary']};
                color: {COLORS['text_secondary']};
                border: none;
                padding: 12px 24px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }}
            QTabBar::tab:hover {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_primary']};
            }}
            QTabBar::tab:selected {{
                background-color: {COLORS['bg_primary']};
                color: {COLORS['text_primary']};
                border-bottom: 2px solid {COLORS['accent_blue']};
            }}
        """)
        
        # Add tabs
        self.dashboard_page = DashboardPage()
        self.tabs.addTab(self.dashboard_page, " 仪表盘 ")
        
        # Placeholder pages
        trading_page = self._create_placeholder_page("交易", "交易功能页面 - 开发中")
        analytics_page = self._create_placeholder_page("分析", "分析功能页面 - 开发中")
        ai_page = self._create_placeholder_page("AI助手", "AI助手功能页面 - 开发中")
        settings_page = self._create_placeholder_page("设置", "设置功能页面 - 开发中")
        
        self.tabs.addTab(trading_page, " 交易 ")
        self.tabs.addTab(analytics_page, " 分析 ")
        self.tabs.addTab(ai_page, " AI助手 ")
        self.tabs.addTab(settings_page, " 设置 ")
        
        main_layout.addWidget(self.tabs)
    
    def _create_top_bar(self) -> QFrame:
        """Create top status bar"""
        top_bar = QFrame()
        top_bar.setFixedHeight(60)
        top_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-bottom: 1px solid {COLORS['border_primary']};
            }}
        """)
        
        layout = QHBoxLayout(top_bar)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # Logo and title
        title_layout = QHBoxLayout()
        logo_label = QLabel("🚀")
        logo_label.setFont(QFont("Arial", 24))
        title_layout.addWidget(logo_label)
        
        title_label = QLabel("WisTrade 智策AI交易")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {COLORS['text_primary']};")
        title_layout.addWidget(title_label)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        
        # Account info
        self.account_label = QLabel("账户: 演示账户")
        self.account_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        layout.addWidget(self.account_label)
        
        # Connection status
        self.status_indicator = QLabel("● 已连接")
        self.status_indicator.setStyleSheet(f"color: {COLORS['accent_green']}; font-weight: 500;")
        layout.addWidget(self.status_indicator)
        
        # Current time
        self.time_label = QLabel(datetime.now().strftime("%H:%M:%S"))
        self.time_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        layout.addWidget(self.time_label)
        
        return top_bar
    
    def _create_placeholder_page(self, title: str, message: str) -> QWidget:
        """Create a placeholder page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {COLORS['text_primary']};")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        msg_label = QLabel(message)
        msg_label.setFont(QFont("Arial", 14))
        msg_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(msg_label)
        
        layout.addStretch()
        return page
    
    def closeEvent(self, event):
        # Settings tab
        settings_widget = self._create_settings_tab()
        self.tabs.addTab(settings_widget, "设置")
    
    def _create_dashboard_tab(self) -> QWidget:
        """Create dashboard tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Account overview
        overview_label = QLabel("账户概览")
        overview_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(overview_label)
        
        # Portfolio info (placeholder)
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setPlainText(
            "总资产: ¥0.00\n"
            "可用资金: ¥0.00\n"
            "持仓市值: ¥0.00\n"
            "今日盈亏: ¥0.00 (0.00%)\n\n"
            "持仓数量: 0\n"
            "活跃策略: 0"
        )
        layout.addWidget(info_text)
        
        # Refresh button
        refresh_btn = QPushButton("刷新数据")
        refresh_btn.clicked.connect(self._refresh_dashboard)
        layout.addWidget(refresh_btn)
        
        layout.addStretch()
        return widget
    
    def _create_trading_tab(self) -> QWidget:
        """Create trading tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Trading controls
        controls_label = QLabel("交易控制")
        controls_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(controls_label)
        
        # Strategy status
        strategy_text = QTextEdit()
        strategy_text.setReadOnly(True)
        strategy_text.setPlainText(
            "策略状态: 未启动\n\n"
            "AI选股: 等待中\n"
            "风险评估: 未完成\n"
            "自动交易: 停止"
        )
        layout.addWidget(strategy_text)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        
        start_ai_btn = QPushButton("启动AI选股")
        start_ai_btn.clicked.connect(self._start_ai_selection)
        btn_layout.addWidget(start_ai_btn)
        
        start_trading_btn = QPushButton("启动自动交易")
        start_trading_btn.clicked.connect(self._start_auto_trading)
        btn_layout.addWidget(start_trading_btn)
        
        stop_trading_btn = QPushButton("停止交易")
        stop_trading_btn.clicked.connect(self._stop_trading)
        btn_layout.addWidget(stop_trading_btn)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        return widget
    
    def _create_analytics_tab(self) -> QWidget:
        """Create analytics tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Performance metrics
        metrics_label = QLabel("绩效分析")
        metrics_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(metrics_label)
        
        # Metrics display (placeholder)
        metrics_text = QTextEdit()
        metrics_text.setReadOnly(True)
        metrics_text.setPlainText(
            "总收益率: 0.00%\n"
            "夏普比率: N/A\n"
            "最大回撤: 0.00%\n"
            "胜率: N/A\n\n"
            "总交易次数: 0\n"
            "盈利交易: 0\n"
            "亏损交易: 0"
        )
        layout.addWidget(metrics_text)
        
        # Export button
        export_btn = QPushButton("导出报告")
        export_btn.clicked.connect(self._export_report)
        layout.addWidget(export_btn)
        
        layout.addStretch()
        return widget
    
    def _create_ai_tab(self) -> QWidget:
        """Create AI assistant tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # AI assistant
        ai_label = QLabel("AI投资助手")
        ai_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(ai_label)
        
        # AI output
        self.ai_output = QTextEdit()
        self.ai_output.setReadOnly(True)
        self.ai_output.setPlaceholderText(
            "AI分析结果将显示在这里...\n\n"
            "您可以:\n"
            "1. 点击'市场分析'获取AI市场观点\n"
            "2. 点击'选股推荐'获取AI推荐股票\n"
            "3. 点击'策略生成'让AI生成交易策略"
        )
        layout.addWidget(self.ai_output)
        
        # AI action buttons
        btn_layout = QHBoxLayout()
        
        analyze_btn = QPushButton("市场分析")
        analyze_btn.clicked.connect(self._ai_analyze_market)
        btn_layout.addWidget(analyze_btn)
        
        select_btn = QPushButton("选股推荐")
        select_btn.clicked.connect(self._ai_select_stocks)
        btn_layout.addWidget(select_btn)
        
        strategy_btn = QPushButton("策略生成")
        strategy_btn.clicked.connect(self._ai_generate_strategy)
        btn_layout.addWidget(strategy_btn)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        return widget
    
    def _create_settings_tab(self) -> QWidget:
        """Create settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Settings info
        settings_label = QLabel("应用设置")
        settings_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(settings_label)
        
        # Settings display
        settings_text = QTextEdit()
        settings_text.setReadOnly(True)
        settings_text.setPlainText(
            "配置文件: config/settings.yaml\n\n"
            "AI模型: GLM-4-Plus\n"
            "数据源: AkShare (免费)\n"
            "券商: QMT\n"
            "日志级别: INFO\n\n"
            "风险限制:\n"
            "  最大仓位: 20%\n"
            "  日损失限额: 5%\n"
            "  订单频率: 10/分钟"
        )
        layout.addWidget(settings_text)
        
        # Config buttons
        btn_layout = QHBoxLayout()
        
        open_config_btn = QPushButton("打开配置文件")
        open_config_btn.clicked.connect(self._open_config)
        btn_layout.addWidget(open_config_btn)
        
        check_update_btn = QPushButton("检查更新")
        check_update_btn.clicked.connect(self._check_updates)
        btn_layout.addWidget(check_update_btn)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        return widget
    
    def _init_status_bar(self):
        """Initialize status bar"""
        status_bar = QStatusBar()
        status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {COLORS['bg_secondary']};
                color: {COLORS['text_secondary']};
                border-top: 1px solid {COLORS['border_primary']};
                padding: 4px 8px;
            }}
        """)
        status_bar.showMessage("就绪 | WisTrade v0.1.0 | 2024")
        self.setStatusBar(status_bar)
    
    def _init_timers(self):
        """Initialize update timers"""
        # Time update timer
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self._update_time)
        self.time_timer.start(1000)
    
    def _update_time(self):
        """Update current time display"""
        self.time_label.setText(datetime.now().strftime("%H:%M:%S"))
    
    def _refresh_dashboard(self):
        """Refresh dashboard data"""
        self.statusBar().showMessage("刷新数据...")
        logger.info("Dashboard refresh requested")
        QMessageBox.information(self, "提示", "数据刷新功能需要连接券商API")
    
    def _start_ai_selection(self):
        """Start AI stock selection"""
        self.statusBar().showMessage("启动AI选股...")
        logger.info("AI stock selection requested")
        QMessageBox.information(self, "提示", "AI选股功能需要配置GLM-4.7 API密钥")
    
    def _start_auto_trading(self):
        """Start automated trading"""
        self.statusBar().showMessage("启动自动交易...")
        logger.info("Auto trading start requested")
        QMessageBox.warning(self, "警告", "自动交易功能需要完整的策略配置和风险评估")
    
    def _stop_trading(self):
        """Stop trading"""
        self.statusBar().showMessage("停止交易")
        logger.info("Trading stop requested")
    
    def _export_report(self):
        """Export analytics report"""
        self.statusBar().showMessage("导出报告...")
        logger.info("Report export requested")
        QMessageBox.information(self, "提示", "报告导出功能需要先执行交易")
    
    def _ai_analyze_market(self):
        """AI market analysis"""
        self.ai_output.setPlainText("正在分析市场...\n\n请稍候，AI正在处理市场数据...")
        logger.info("AI market analysis requested")
    
    def _ai_select_stocks(self):
        """AI stock selection"""
        self.ai_output.setPlainText("正在进行AI选股...\n\n请稍候, AI正在筛选优质股票...")
        logger.info("AI stock selection requested")
    
    def _ai_generate_strategy(self):
        """AI strategy generation"""
        self.ai_output.setPlainText("正在生成交易策略...\n\n请稍候, AI正在制定最优策略...")
        logger.info("AI strategy generation requested")
    
    def _open_config(self):
        """Open configuration file"""
        self.statusBar().showMessage("打开配置文件...")
        logger.info("Open config requested")
        QMessageBox.information(self, "提示", "配置文件位于: config/settings.yaml")
    
    def _check_updates(self):
        """Check for updates"""
        self.statusBar().showMessage("检查更新...")
        logger.info("Update check requested")
        QMessageBox.information(self, "提示", "当前版本: 0.1.0\n最新版本: 0.1.0\n您已使用最新版本")
    
    def _auto_refresh(self):
        """Auto refresh timer callback"""
        pass
    
    def closeEvent(self, event):
        """Handle window close event"""
        reply = QMessageBox.question(
            self,
            "确认退出",
            "确定要退出WisTrade吗?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            logger.info("Application closed by user")
            event.accept()
        else:
            event.ignore()
