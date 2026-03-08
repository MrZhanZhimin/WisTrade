"""
仪表盘页面 - 简化版
显示账户概览和持仓信息
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QGridLayout, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from wistrade.ui.styles import COLORS, format_currency, get_profit_color

class DashboardPage(QWidget):
    """仪表盘页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 标题
        title = QLabel("仪表盘")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        layout.addWidget(title)
        
        # 账户概览卡片
        overview_layout = QHBoxLayout()
        overview_layout.setSpacing(15)
        
        # 创建4个统计卡片
        cards_data = [
            ("总资产", "¥1,234,567.89", "+2.34%", True),
            ("今日盈亏", "¥23,456.78", "+1.92%", True),
            ("持仓市值", "¥777,888.99", "62.99%", None),
            ("可用资金", "¥456,678.90", "37.01%", None),
        ]
        
        for label, value, change, is_profit in cards_data:
            card = self.create_stat_card(label, value, change, is_profit)
            overview_layout.addWidget(card)
        
        layout.addLayout(overview_layout)
        
        # 持仓列表
        positions_group = QGroupBox("持仓列表")
        positions_group.setStyleSheet(f"""
            QGroupBox {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border_primary']};
                border-radius: 12px;
                margin-top: 16px;
                padding-top: 16px;
                color: {COLORS['text_primary']};
                font-weight: 500;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                color: {COLORS['text_secondary']};
            }}
        """)
        
        positions_layout = QVBoxLayout(positions_group)
        
        # 示例持仓数据
        positions_data = [
            ("000001", "平安银行", "1000", "12.50", "13.20", "+5.60%"),
            ("600000", "浦发银行", "2000", "8.80", "9.15", "+3.98%"),
            ("000002", "万科A", "500", "15.30", "14.80", "-3.27%"),
        ]
        
        for code, name, qty, cost, price, pnl in positions_data:
            pos_widget = self.create_position_row(code, name, qty, cost, price, pnl)
            positions_layout.addWidget(pos_widget)
        
        positions_layout.addStretch()
        layout.addWidget(positions_group)
        
        layout.addStretch()
    
    def create_stat_card(self, label: str, value: str, change: str, is_profit) -> QWidget:
        """创建统计卡片"""
        card = QFrame()
        card.setObjectName("statCard")
        card.setStyleSheet(f"""
            QFrame#statCard {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border_primary']};
                border-radius: 12px;
                padding: 20px;
            }}
        """)
        card.setFixedHeight(120)
        
        layout = QVBoxLayout(card)
        
        # 标签
        label_widget = QLabel(label)
        label_widget.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 14px;")
        layout.addWidget(label_widget)
        
        # 数值
        value_widget = QLabel(value)
        value_widget.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 24px; font-weight: 600;")
        layout.addWidget(value_widget)
        
        # 变化
        if is_profit is not None:
            color = get_profit_color(1 if is_profit else -1)
            change_widget = QLabel(change)
            change_widget.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: 500;")
            layout.addWidget(change_widget)
        
        layout.addStretch()
        
        return card
    
    def create_position_row(self, code, name, qty, cost, price, pnl) -> QWidget:
        """创建持仓行"""
        row = QFrame()
        row.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_primary']};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        
        layout = QHBoxLayout(row)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 股票信息
        info_layout = QVBoxLayout()
        code_label = QLabel(f"{code} {name}")
        code_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: 500;")
        info_layout.addWidget(code_label)
        
        qty_label = QLabel(f"持仓: {qty}股")
        qty_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        info_layout.addWidget(qty_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # 价格信息
        price_layout = QVBoxLayout()
        cost_label = QLabel(f"成本: ¥{cost}")
        cost_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        price_layout.addWidget(cost_label)
        
        price_label = QLabel(f"现价: ¥{price}")
        price_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: 500;")
        price_layout.addWidget(price_label)
        
        layout.addLayout(price_layout)
        
        # 盈亏
        is_profit = pnl.startswith('+')
        color = get_profit_color(1 if is_profit else -1)
        pnl_label = QLabel(pnl)
        pnl_label.setStyleSheet(f"color: {color}; font-size: 16px; font-weight: 600;")
        pnl_label.setFixedWidth(80)
        layout.addWidget(pnl_label)
        
        # 卖出按钮
        sell_btn = QPushButton("卖出")
        sell_btn.setFixedSize(60, 30)
        sell_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent_red']};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: #DA3633;
            }}
        """)
        layout.addWidget(sell_btn)
        
        return row
