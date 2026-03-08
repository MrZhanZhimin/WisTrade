#!/usr/bin/env python3
"""
WisTrade Web界面 - 基于Flask的Web版本

运行方式：
    python web_app.py
    
然后访问：http://localhost:5000
"""

from flask import Flask, render_template_string, jsonify, request
from datetime import datetime
import json

app = Flask(__name__)

# 模拟数据
MOCK_DATA = {
    'account': {
        'total_assets': 1234567.89,
        'available_cash': 456789.12,
        'market_value': 777778.77,
        'today_pnl': 23456.78,
        'today_pnl_pct': 1.92
    },
    'positions': [
        {
            'code': '000001',
            'name': '平安银行',
            'quantity': 1000,
            'cost_price': 12.50,
            'current_price': 13.20,
            'pnl': 700.00,
            'pnl_pct': 5.60
        },
        {
            'code': '600000',
            'name': '浦发银行',
            'quantity': 2000,
            'cost_price': 8.80,
            'current_price': 9.15,
            'pnl': 700.00,
            'pnl_pct': 3.98
        },
        {
            'code': '000002',
            'name': '万科A',
            'quantity': 500,
            'cost_price': 15.30,
            'current_price': 14.80,
            'pnl': -250.00,
            'pnl_pct': -3.27
        }
    ],
    'quotes': [
        {'code': '600519', 'name': '贵州茅台', 'price': 1688.00, 'change_pct': 2.15},
        {'code': '000858', 'name': '五粮液', 'price': 158.50, 'change_pct': 1.82},
        {'code': '601318', 'name': '中国平安', 'price': 45.60, 'change_pct': -0.65},
        {'code': '600036', 'name': '招商银行', 'price': 32.45, 'change_pct': 0.95},
        {'code': '000333', 'name': '美的集团', 'price': 58.90, 'change_pct': 1.45}
    ]
}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WisTrade - AI智能交易平台</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #0D1117;
            color: #E6EDF3;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        /* 顶部栏 */
        .header {
            background: #161B22;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1px solid #30363D;
        }
        
        .logo {
            font-size: 24px;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .status {
            display: flex;
            gap: 20px;
            font-size: 14px;
            color: #8B949E;
        }
        
        .status-item {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .online {
            color: #3FB950;
            font-weight: 500;
        }
        
        /* 导航标签 */
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .tab {
            background: #161B22;
            border: 1px solid #30363D;
            color: #8B949E;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .tab:hover {
            background: #21262D;
            color: #E6EDF3;
        }
        
        .tab.active {
            background: #0D1117;
            color: #E6EDF3;
            border-bottom: 2px solid #58A6FF;
        }
        
        /* 统计卡片 */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: #161B22;
            border: 1px solid #30363D;
            border-radius: 12px;
            padding: 20px;
            transition: all 0.3s;
        }
        
        .stat-card:hover {
            border-color: #58A6FF;
        }
        
        .stat-label {
            color: #8B949E;
            font-size: 14px;
            margin-bottom: 8px;
        }
        
        .stat-value {
            font-size: 28px;
            font-weight: 600;
            color: #E6EDF3;
        }
        
        .stat-change {
            font-size: 14px;
            margin-top: 8px;
            font-weight: 500;
        }
        
        .positive { color: #3FB950; }
        .negative { color: #F85149; }
        
        /* 持仓表格 */
        .positions-section {
            background: #161B22;
            border: 1px solid #30363D;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .section-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 15px;
        }
        
        .positions-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .positions-table th {
            text-align: left;
            padding: 12px;
            color: #8B949E;
            font-weight: 500;
            border-bottom: 1px solid #30363D;
        }
        
        .positions-table td {
            padding: 12px;
            border-bottom: 1px solid #21262D;
        }
        
        .positions-table tr:hover {
            background: #21262D;
        }
        
        .btn-sell {
            background: #F85149;
            color: white;
            border: none;
            padding: 6px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
        }
        
        .btn-sell:hover {
            background: #DA3633;
        }
        
        /* 实时行情 */
        .quotes-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
        }
        
        .quote-card {
            background: #0D1117;
            border: 1px solid #30363D;
            border-radius: 8px;
            padding: 15px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .quote-card:hover {
            border-color: #58A6FF;
            transform: translateY(-2px);
        }
        
        .quote-name {
            font-weight: 500;
            margin-bottom: 5px;
        }
        
        .quote-code {
            color: #8B949E;
            font-size: 12px;
            margin-bottom: 8px;
        }
        
        .quote-price {
            font-size: 20px;
            font-weight: 600;
        }
        
        .quote-change {
            font-size: 14px;
            font-weight: 500;
        }
        
        /* AI助手 */
        .ai-section {
            display: none;
            background: #161B22;
            border: 1px solid #30363D;
            border-radius: 12px;
            padding: 20px;
            min-height: 500px;
        }
        
        .ai-section.active {
            display: block;
        }
        
        .ai-buttons {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .ai-btn {
            background: #21262D;
            border: 1px solid #30363D;
            color: #E6EDF3;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .ai-btn:hover {
            background: #30363D;
            border-color: #58A6FF;
        }
        
        .chat-container {
            background: #0D1117;
            border-radius: 8px;
            padding: 20px;
            height: 400px;
            overflow-y: auto;
        }
        
        .chat-message {
            margin-bottom: 15px;
            padding: 12px;
            border-radius: 8px;
        }
        
        .chat-message.user {
            background: #1F6FEB;
            margin-left: 20%;
        }
        
        .chat-message.ai {
            background: #21262D;
            margin-right: 20%;
        }
        
        .chat-input-container {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        
        .chat-input {
            flex: 1;
            background: #0D1117;
            border: 1px solid #30363D;
            color: #E6EDF3;
            padding: 12px;
            border-radius: 8px;
            font-size: 14px;
        }
        
        .chat-input:focus {
            outline: none;
            border-color: #58A6FF;
        }
        
        .send-btn {
            background: #238636;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
        }
        
        .send-btn:hover {
            background: #2EA043;
        }
        
        /* 通知 */
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            background: #161B22;
            border: 1px solid #30363D;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.5);
            display: none;
            z-index: 1000;
        }
        
        .notification.show {
            display: block;
            animation: slideIn 0.3s ease;
        }
        
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        /* 时间显示 */
        #current-time {
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- 顶部栏 -->
        <div class="header">
            <div class="logo">
                <span>🚀</span>
                <span>WisTrade 智策AI交易</span>
            </div>
            <div class="status">
                <div class="status-item">
                    <span>账户: 演示账户</span>
                </div>
                <div class="status-item">
                    <span class="online">● 已连接</span>
                </div>
                <div class="status-item">
                    <span id="current-time"></span>
                </div>
            </div>
        </div>
        
        <!-- 导航标签 -->
        <div class="tabs">
            <div class="tab active" onclick="switchTab('dashboard')">📊 仪表盘</div>
            <div class="tab" onclick="switchTab('trading')">💼 交易</div>
            <div class="tab" onclick="switchTab('analytics')">📈 分析</div>
            <div class="tab" onclick="switchTab('ai')">🤖 AI助手</div>
            <div class="tab" onclick="switchTab('settings')">⚙️ 设置</div>
        </div>
        
        <!-- 仪表盘内容 -->
        <div id="dashboard-content">
            <!-- 统计卡片 -->
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">总资产</div>
                    <div class="stat-value" id="total-assets">¥1,234,567.89</div>
                    <div class="stat-change positive">+2.34% 较昨日</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">今日盈亏</div>
                    <div class="stat-value positive" id="today-pnl">+¥23,456.78</div>
                    <div class="stat-change positive">+1.92%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">持仓市值</div>
                    <div class="stat-value" id="market-value">¥777,888.99</div>
                    <div class="stat-change">占比 62.99%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">可用资金</div>
                    <div class="stat-value" id="available-cash">¥456,678.90</div>
                    <div class="stat-change">占比 37.01%</div>
                </div>
            </div>
            
            <!-- 持仓列表 -->
            <div class="positions-section">
                <div class="section-title">持仓列表</div>
                <table class="positions-table">
                    <thead>
                        <tr>
                            <th>股票代码</th>
                            <th>股票名称</th>
                            <th>持仓数量</th>
                            <th>成本价</th>
                            <th>现价</th>
                            <th>盈亏</th>
                            <th>盈亏%</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody id="positions-body">
                    </tbody>
                </table>
            </div>
            
            <!-- 实时行情 -->
            <div class="positions-section">
                <div class="section-title">实时行情</div>
                <div class="quotes-grid" id="quotes-grid">
                </div>
            </div>
        </div>
        
        <!-- AI助手内容 -->
        <div id="ai-content" class="ai-section">
            <div class="section-title">AI投资助手</div>
            <div class="ai-buttons">
                <button class="ai-btn" onclick="aiAction('market')">📊 市场分析</button>
                <button class="ai-btn" onclick="aiAction('stock')">🎯 选股推荐</button>
                <button class="ai-btn" onclick="aiAction('strategy')">📋 策略生成</button>
                <button class="ai-btn" onclick="aiAction('risk')">⚠️ 风险预警</button>
            </div>
            <div class="chat-container" id="chat-container">
                <div class="chat-message ai">
                    👋 您好！我是WisTrade AI助手。我可以帮您分析市场、推荐股票、生成交易策略和检查风险。请问有什么可以帮您的？
                </div>
            </div>
            <div class="chat-input-container">
                <input type="text" class="chat-input" id="chat-input" placeholder="输入您的问题..." onkeypress="handleKeyPress(event)">
                <button class="send-btn" onclick="sendMessage()">发送</button>
            </div>
        </div>
    </div>
    
    <!-- 通知 -->
    <div class="notification" id="notification"></div>
    
    <script>
        // 更新时间
        function updateTime() {
            const now = new Date();
            const timeStr = now.toLocaleTimeString('zh-CN', { hour12: false });
            document.getElementById('current-time').textContent = timeStr;
        }
        setInterval(updateTime, 1000);
        updateTime();
        
        // 加载数据
        function loadData() {
            fetch('/api/data')
                .then(response => response.json())
                .then(data => {
                    updateUI(data);
                });
        }
        
        // 更新UI
        function updateUI(data) {
            // 更新账户信息
            document.getElementById('total-assets').textContent = 
                '¥' + data.account.total_assets.toLocaleString('zh-CN', {minimumFractionDigits: 2});
            
            const pnlElement = document.getElementById('today-pnl');
            pnlElement.textContent = (data.account.today_pnl >= 0 ? '+' : '') + 
                '¥' + data.account.today_pnl.toLocaleString('zh-CN', {minimumFractionDigits: 2});
            pnlElement.className = 'stat-value ' + (data.account.today_pnl >= 0 ? 'positive' : 'negative');
            
            // 更新持仓列表
            const tbody = document.getElementById('positions-body');
            tbody.innerHTML = data.positions.map(pos => `
                <tr>
                    <td>${pos.code}</td>
                    <td>${pos.name}</td>
                    <td>${pos.quantity}</td>
                    <td>¥${pos.cost_price.toFixed(2)}</td>
                    <td>¥${pos.current_price.toFixed(2)}</td>
                    <td class="${pos.pnl >= 0 ? 'positive' : 'negative'}">
                        ${pos.pnl >= 0 ? '+' : ''}¥${pos.pnl.toFixed(2)}
                    </td>
                    <td class="${pos.pnl_pct >= 0 ? 'positive' : 'negative'}">
                        ${pos.pnl_pct >= 0 ? '+' : ''}${pos.pnl_pct.toFixed(2)}%
                    </td>
                    <td><button class="btn-sell" onclick="sellStock('${pos.code}')">卖出</button></td>
                </tr>
            `).join('');
            
            // 更新行情
            const quotesGrid = document.getElementById('quotes-grid');
            quotesGrid.innerHTML = data.quotes.map(quote => `
                <div class="quote-card">
                    <div class="quote-name">${quote.name}</div>
                    <div class="quote-code">${quote.code}</div>
                    <div class="quote-price">¥${quote.price.toFixed(2)}</div>
                    <div class="quote-change ${quote.change_pct >= 0 ? 'positive' : 'negative'}">
                        ${quote.change_pct >= 0 ? '+' : ''}${quote.change_pct.toFixed(2)}%
                    </div>
                </div>
            `).join('');
        }
        
        // 切换标签
        function switchTab(tabName) {
            // 更新标签样式
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            event.target.classList.add('active');
            
            // 显示内容
            document.getElementById('dashboard-content').style.display = tabName === 'dashboard' ? 'block' : 'none';
            document.getElementById('ai-content').classList.toggle('active', tabName === 'ai');
        }
        
        // AI操作
        function aiAction(action) {
            const actions = {
                'market': '正在分析当前市场趋势...',
                'stock': '正在为您筛选优质股票...',
                'strategy': '正在生成交易策略...',
                'risk': '正在检查持仓风险...'
            };
            
            addMessage('user', actions[action]);
            
            setTimeout(() => {
                const responses = {
                    'market': '📊 市场分析：\n\n当前A股市场整体呈现震荡上行态势。沪深300指数近期表现稳健，建议关注大消费、新能源等板块。注意控制仓位，防范短期回调风险。',
                    'stock': '🎯 推荐股票：\n\n1. 贵州茅台(600519) - 消费龙头，业绩稳定\n2. 宁德时代(300750) - 新能源领军，成长性好\n3. 招商银行(600036) - 银行优质标的，估值合理\n\n建议分散投资，控制单股仓位。',
                    'strategy': '📋 交易策略：\n\n【稳健增长策略】\n- 选股标准：ROE>15%，PE<30，连续3年盈利\n- 仓位管理：单股不超过20%，总仓位60-80%\n- 止损止盈：止损-7%，止盈+15%\n- 操作频率：中长线持有，月度调仓',
                    'risk': '⚠️ 风险提示：\n\n当前持仓风险等级：中等\n\n建议：\n1. 持仓集中度适中，但万科A占比较高\n2. 银行板块敞口较大，注意行业风险\n3. 建议增加科技或消费板块配置\n4. 设置好止损位，防范系统性风险'
                };
                addMessage('ai', responses[action]);
            }, 1000);
        }
        
        // 添加消息
        function addMessage(type, content) {
            const container = document.getElementById('chat-container');
            const messageDiv = document.createElement('div');
            messageDiv.className = `chat-message ${type}`;
            messageDiv.textContent = content;
            container.appendChild(messageDiv);
            container.scrollTop = container.scrollHeight;
        }
        
        // 发送消息
        function sendMessage() {
            const input = document.getElementById('chat-input');
            const message = input.value.trim();
            if (!message) return;
            
            addMessage('user', message);
            input.value = '';
            
            setTimeout(() => {
                const response = generateAIResponse(message);
                addMessage('ai', response);
            }, 1000);
        }
        
        // 生成AI回复
        function generateAIResponse(message) {
            if (message.includes('茅台') || message.includes('600519')) {
                return '贵州茅台(600519)：\n\n当前价格：¥1688.00\nPE估值：合理\n技术面：震荡上行\n投资建议：可逢低配置，建议仓位5-10%';
            } else if (message.includes('平安') || message.includes('000001')) {
                return '平安银行(000001)：\n\n您当前持有1000股，成本价¥12.50，现价¥13.20\n盈亏：+¥700.00 (+5.60%)\n\n技术面：短期上涨趋势\n建议：可继续持有，止盈位¥14.00';
            } else if (message.includes('分析') || message.includes('市场')) {
                return '📊 市场整体评估：\n\n当前处于震荡市，结构性机会为主。\n\n看多板块：\n- 大消费（白酒、家电）\n- 新能源（光伏、锂电）\n- 科技（半导体、AI）\n\n风险提示：注意控制仓位，设置止损。';
            } else {
                return '感谢您的提问！我是WisTrade AI助手。\n\n我可以帮您：\n1. 分析市场和个股\n2. 推荐投资标的\n3. 生成交易策略\n4. 检查持仓风险\n\n请随时提问！';
            }
        }
        
        // 键盘事件
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }
        
        // 卖出股票
        function sellStock(code) {
            showNotification(`已提交卖出委托：${code}`, 'success');
        }
        
        // 显示通知
        function showNotification(message, type = 'info') {
            const notification = document.getElementById('notification');
            notification.textContent = message;
            notification.className = 'notification show';
            
            setTimeout(() => {
                notification.classList.remove('show');
            }, 3000);
        }
        
        // 初始化
        loadData();
        setInterval(loadData, 5000); // 5秒刷新一次
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/data')
def get_data():
    return jsonify(MOCK_DATA)

if __name__ == '__main__':
    print("=" * 60)
    print("WisTrade Web界面启动中...")
    print("=" * 60)
    print()
    print("🌐 访问地址: http://localhost:5000")
    print("📱 本地访问: http://127.0.0.1:5000")
    print()
    print("按 Ctrl+C 停止服务")
    print("=" * 60)
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=False)
