"""
WisTrade Modern Dark Theme - 专业交易UI样式系统

设计理念:
- 深色主题，减少眼睛疲劳
- 参考 TradingView, Bloomberg Terminal 设计
- 清晰的视觉层次
- 专业的数据可视化

颜色系统基于 GitHub Dark 主题
"""

# ============================================
# 颜色常量
# ============================================

COLORS = {
    # 背景色
    'bg_primary': '#0D1117',      # 主背景 (深蓝黑)
    'bg_secondary': '#161B22',    # 次背景 (卡片)
    'bg_tertiary': '#21262D',     # 三级背景 (边框)
    'bg_overlay': '#30363D',      # 悬浮背景
    
    # 文字色
    'text_primary': '#E6EDF3',    # 主文字 (高亮)
    'text_secondary': '#8B949E',  # 次要文字 (灰色)
    'text_tertiary': '#6E7681',   # 三级文字 (更灰)
    'text_link': '#58A6FF',       # 链接文字 (蓝色)
    
    # 功能色
    'accent_green': '#3FB950',    # 买入/上涨
    'accent_red': '#F85149',      # 卖出/下跌
    'accent_blue': '#58A6FF',     # 信息/强调
    'accent_purple': '#A371F7',   # 高亮/特殊
    'accent_yellow': '#D29922',   # 警告
    'accent_orange': '#DB6D28',   # 注意
    
    # 边框
    'border_primary': '#30363D',  # 主边框
    'border_secondary': '#21262D', # 次边框
    'border_focus': '#58A6FF',    # 聚焦边框
    
    # 透明色
    'overlay_light': 'rgba(255, 255, 255, 0.05)',
    'overlay_medium': 'rgba(255, 255, 255, 0.08)',
    'overlay_dark': 'rgba(0, 0, 0, 0.5)',
}

# ============================================
# 样式表模板
# ============================================

# 主窗口样式
MAIN_WINDOW = f"""
QMainWindow {{
    background-color: {COLORS['bg_primary']};
    color: {COLORS['text_primary']};
}}

QStatusBar {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_secondary']};
    border-top: 1px solid {COLORS['border_primary']};
    padding: 4px 8px;
}}
"""

# 标签样式
LABEL = f"""
QLabel {{
    color: {COLORS['text_primary']};
    background-color: transparent;
}}
"""

# 按钮样式
BUTTON_PRIMARY = f"""
QPushButton {{
    background-color: {COLORS['accent_green']};
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
    min-width: 80px;
}}

QPushButton:hover {{
    background-color: #2EA043;
}}

QPushButton:pressed {{
    background-color: #238636;
}}

QPushButton:disabled {{
    background-color: {COLORS['bg_tertiary']};
    color: {COLORS['text_tertiary']};
}}
"""

BUTTON_DANGER = f"""
QPushButton {{
    background-color: {COLORS['accent_red']};
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
    min-width: 80px;
}}

QPushButton:hover {{
    background-color: #DA3633;
}}

QPushButton:pressed {{
    background-color: #B62324;
}}

QPushButton:disabled {{
    background-color: {COLORS['bg_tertiary']};
    color: {COLORS['text_tertiary']};
}}
"""

BUTTON_GHOST = f"""
QPushButton {{
    background-color: transparent;
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border_primary']};
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
    min-width: 80px;
}}

QPushButton:hover {{
    background-color: {COLORS['overlay_light']};
    border-color: {COLORS['border_focus']};
}}

QPushButton:pressed {{
    background-color: {COLORS['overlay_medium']};
}}

QPushButton:disabled {{
    color: {COLORS['text_tertiary']};
    border-color: {COLORS['border_secondary']};
}}
"""

# 输入框样式
INPUT = f"""
QLineEdit {{
    background-color: {COLORS['bg_primary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border_primary']};
    border-radius: 6px;
    padding: 8px 12px;
    selection-background-color: {COLORS['accent_blue']};
}}

QLineEdit:hover {{
    border-color: {COLORS['bg_overlay']};
}}

QLineEdit:focus {{
    border-color: {COLORS['border_focus']};
    background-color: {COLORS['bg_secondary']};
}}

QLineEdit:disabled {{
    background-color: {COLORS['bg_tertiary']};
    color: {COLORS['text_tertiary']};
}}
"""

# 下拉框样式
COMBOBOX = f"""
QComboBox {{
    background-color: {COLORS['bg_primary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border_primary']};
    border-radius: 6px;
    padding: 8px 12px;
    min-width: 100px;
}}

QComboBox:hover {{
    border-color: {COLORS['bg_overlay']};
}}

QComboBox:focus {{
    border-color: {COLORS['border_focus']};
}}

QComboBox::drop-down {{
    border: none;
    width: 30px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid {COLORS['text_secondary']};
    margin-right: 10px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border_primary']};
    selection-background-color: {COLORS['accent_blue']};
    selection-color: white;
    padding: 4px;
}}
"""

# 数字输入框
SPINBOX = f"""
QSpinBox, QDoubleSpinBox {{
    background-color: {COLORS['bg_primary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border_primary']};
    border-radius: 6px;
    padding: 8px 12px;
}}

QSpinBox:hover, QDoubleSpinBox:hover {{
    border-color: {COLORS['bg_overlay']};
}}

QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {COLORS['border_focus']};
}}

QSpinBox::up-button, QDoubleSpinBox::up-button {{
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 30px;
    border: none;
    background-color: transparent;
}}

QSpinBox::down-button, QDoubleSpinBox::down-button {{
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 30px;
    border: none;
    background-color: transparent;
}}

QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 4px solid {COLORS['text_secondary']};
}}

QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 4px solid {COLORS['text_secondary']};
}}
"""

# 表格样式
TABLE = f"""
QTableWidget {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    gridline-color: {COLORS['border_secondary']};
    border: 1px solid {COLORS['border_primary']};
    border-radius: 8px;
    selection-background-color: {COLORS['accent_blue']};
    selection-color: white;
}}

QTableWidget::item {{
    padding: 8px;
    border-bottom: 1px solid {COLORS['border_secondary']};
}}

QTableWidget::item:hover {{
    background-color: {COLORS['overlay_light']};
}}

QHeaderView::section {{
    background-color: {COLORS['bg_tertiary']};
    color: {COLORS['text_secondary']};
    padding: 10px;
    border: none;
    border-bottom: 1px solid {COLORS['border_primary']};
    font-weight: 500;
}}

QHeaderView::section:hover {{
    background-color: {COLORS['bg_overlay']};
}}
"""

# 标签页样式
TABWIDGET = f"""
QTabWidget::pane {{
    border: 1px solid {COLORS['border_primary']};
    border-radius: 8px;
    background-color: {COLORS['bg_secondary']};
    padding: 8px;
}}

QTabBar::tab {{
    background-color: transparent;
    color: {COLORS['text_secondary']};
    border: 1px solid transparent;
    border-bottom: none;
    padding: 10px 20px;
    margin-right: 4px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}}

QTabBar::tab:hover {{
    background-color: {COLORS['overlay_light']};
    color: {COLORS['text_primary']};
}}

QTabBar::tab:selected {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border-color: {COLORS['border_primary']};
}}

QTabBar::close-button {{
    image: none;
    subcontrol-position: right;
    margin-right: 8px;
}}
"""

# 滚动区域样式
SCROLLAREA = f"""
QScrollArea {{
    background-color: transparent;
    border: none;
}}

QScrollBar:vertical {{
    background-color: {COLORS['bg_primary']};
    width: 12px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS['bg_overlay']};
    border-radius: 6px;
    min-height: 30px;
    margin: 2px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS['border_focus']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}

QScrollBar:horizontal {{
    background-color: {COLORS['bg_primary']};
    height: 12px;
    margin: 0;
}}

QScrollBar::handle:horizontal {{
    background-color: {COLORS['bg_overlay']};
    border-radius: 6px;
    min-width: 30px;
    margin: 2px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {COLORS['border_focus']};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
    background: none;
}}
"""

# 列表样式
LISTWIDGET = f"""
QListWidget {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border_primary']};
    border-radius: 8px;
    padding: 4px;
}}

QListWidget::item {{
    background-color: transparent;
    padding: 10px;
    border-radius: 6px;
}}

QListWidget::item:hover {{
    background-color: {COLORS['overlay_light']};
}}

QListWidget::item:selected {{
    background-color: {COLORS['accent_blue']};
    color: white;
}}
"""

# 文本编辑器样式
TEXTEDIT = f"""
QTextEdit, QPlainTextEdit {{
    background-color: {COLORS['bg_primary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border_primary']};
    border-radius: 6px;
    padding: 8px;
    selection-background-color: {COLORS['accent_blue']};
    selection-color: white;
}}

QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {COLORS['border_focus']};
}}
"""

# 分组框样式
GROUPBOX = f"""
QGroupBox {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border_primary']};
    border-radius: 8px;
    margin-top: 16px;
    padding-top: 16px;
    font-weight: 500;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: {COLORS['text_secondary']};
    background-color: {COLORS['bg_secondary']};
}}
"""

# 复选框样式
CHECKBOX = f"""
QCheckBox {{
    color: {COLORS['text_primary']};
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {COLORS['border_primary']};
    border-radius: 4px;
    background-color: {COLORS['bg_primary']};
}}

QCheckBox::indicator:hover {{
    border-color: {COLORS['border_focus']};
}}

QCheckBox::indicator:checked {{
    background-color: {COLORS['accent_green']};
    border-color: {COLORS['accent_green']};
}}

QCheckBox::indicator:disabled {{
    background-color: {COLORS['bg_tertiary']};
    border-color: {COLORS['border_secondary']};
}}
"""

# 滑块样式
SLIDER = f"""
QSlider::groove:horizontal {{
    background: {COLORS['bg_tertiary']};
    height: 6px;
    border-radius: 3px;
}}

QSlider::handle:horizontal {{
    background: {COLORS['accent_blue']};
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}}

QSlider::handle:horizontal:hover {{
    background: {COLORS['border_focus']};
}}

QSlider::sub-page:horizontal {{
    background: {COLORS['accent_blue']};
    border-radius: 3px;
}}
"""

# 工具提示样式
TOOLTIP = f"""
QToolTip {{
    background-color: {COLORS['bg_tertiary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border_primary']};
    border-radius: 6px;
    padding: 6px 10px;
}}
"""

# ============================================
# 组合样式
# ============================================

# 完整应用样式
APP_STYLESHEET = (
    MAIN_WINDOW +
    LABEL +
    BUTTON_PRIMARY +
    BUTTON_DANGER +
    BUTTON_GHOST +
    INPUT +
    COMBOBOX +
    SPINBOX +
    TABLE +
    TABWIDGET +
    SCROLLAREA +
    LISTWIDGET +
    TEXTEDIT +
    GROUPBOX +
    CHECKBOX +
    SLIDER +
    TOOLTIP
)

# 卡片样式
CARD_STYLE = f"""
QWidget#card {{
    background-color: {COLORS['bg_secondary']};
    border: 1px solid {COLORS['border_primary']};
    border-radius: 12px;
    padding: 16px;
}}

QWidget#card:hover {{
    border-color: {COLORS['bg_overlay']};
}}
"""

# 统计卡片样式
STAT_CARD_STYLE = f"""
QWidget#statCard {{
    background-color: {COLORS['bg_secondary']};
    border: 1px solid {COLORS['border_primary']};
    border-radius: 12px;
    padding: 20px;
}}

QLabel#statValue {{
    font-size: 32px;
    font-weight: 600;
    color: {COLORS['text_primary']};
}}

QLabel#statLabel {{
    font-size: 14px;
    color: {COLORS['text_secondary']};
    margin-top: 4px;
}}

QLabel#statChange {{
    font-size: 14px;
    font-weight: 500;
}}
"""

# ============================================
# 辅助函数
# ============================================

def get_profit_color(profit_pct: float) -> str:
    """
    根据涨跌幅返回颜色
    
    Args:
        profit_pct: 盈亏百分比（正数盈利，负数亏损）
    
    Returns:
        颜色代码
    """
    if profit_pct > 0:
        return COLORS['accent_green']
    elif profit_pct < 0:
        return COLORS['accent_red']
    else:
        return COLORS['text_secondary']

def get_profit_style(profit_pct: float) -> str:
    """
    获取盈亏样式表
    
    Args:
        profit_pct: 盈亏百分比
    
    Returns:
        CSS样式
    """
    color = get_profit_color(profit_pct)
    return f"color: {color}; font-weight: 500;"

def format_currency(value: float) -> str:
    """
    格式化货币（添加中文单位）
    
    Args:
        value: 金额
    
    Returns:
        格式化字符串
    """
    if abs(value) >= 1e8:  # 1亿
        return f"¥{value/1e8:.2f}亿"
    elif abs(value) >= 1e4:  # 1万
        return f"¥{value/1e4:.2f}万"
    else:
        return f"¥{value:.2f}"

def format_percentage(value: float, show_sign: bool = True) -> str:
    """
    格式化百分比
    
    Args:
        value: 百分比值
        show_sign: 是否显示正负号
    
    Returns:
        格式化字符串
    """
    if show_sign and value > 0:
        return f"+{value:.2f}%"
    else:
        return f"{value:.2f}%"

def format_volume(volume: int) -> str:
    """
    格式化成交量
    
    Args:
        volume: 成交量（股）
    
    Returns:
        格式化字符串
    """
    if volume >= 1e8:  # 1亿股
        return f"{volume/1e8:.2f}亿"
    elif volume >= 1e4:  # 1万股
        return f"{volume/1e4:.2f}万"
    else:
        return str(volume)
