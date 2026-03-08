"""
ReAct Agent implementation for AI trading

Implements Plan → Acquire → Reason → Act pattern.
"""

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from wistrade.ai.llm_client import AIClient

logger = logging.getLogger(__name__)


class AgentState(Enum):
    """Agent state in reasoning loop"""
    PLAN = "plan"
    ACQUIRE = "acquire"
    REASON = "reason"
    ACT = "act"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class Tool:
    """Tool that agent can use"""
    name: str
    description: str
    function: Callable
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    
@dataclass
class AgentContext:
    """Agent execution context"""
    query: str
    state: AgentState = AgentState.PLAN
    iteration: int = 0
    max_iterations: int = 10
    
    # Accumulated information
    plan: Optional[str] = None
    acquired_data: Dict[str, Any] = field(default_factory=dict)
    reasoning: Optional[str] = None
    action: Optional[str] = None
    result: Optional[Any] = None
    
    # History
    thought_history: List[str] = field(default_factory=list)
    action_history: List[str] = field(default_factory=list)
    
    # Metadata
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class ReActAgent:
    """
    ReAct-style reasoning agent
    
    Follows Plan → Acquire → Reason → Act loop:
    1. Plan: Formulate initial hypothesis
    2. Acquire: Gather information using tools
    3. Reason: Analyze information
    4. Act: Make decision or gather more info
    """
    
    def __init__(
        self,
        llm_client: AIClient,
        tools: Optional[List[Tool]] = None,
        max_iterations: int = 10,
    ):
        """
        Initialize ReAct agent
        
        Args:
            llm_client: LLM client for reasoning
            tools: Available tools for information gathering
            max_iterations: Maximum reasoning iterations
        """
        self.llm = llm_client
        self.tools = {tool.name: tool for tool in (tools or [])}
        self.max_iterations = max_iterations
        
        # Register default tools
        self._register_default_tools()
        
        logger.info(f"ReAct agent initialized with {len(self.tools)} tools")
    
    def _register_default_tools(self) -> None:
        """Register default trading tools"""
        # These will be implemented by TradingEngine in Phase 4
        pass
    
    def register_tool(self, tool: Tool) -> None:
        """
        Register a tool for agent to use
        
        Args:
            tool: Tool to register
        """
        self.tools[tool.name] = tool
        logger.info(f"Tool registered: {tool.name}")
    
    def execute(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentContext:
        """
        Execute ReAct reasoning loop
        
        Args:
            query: User query or task
            context: Additional context
        
        Returns:
            Agent execution context with results
        """
        # Initialize context
        agent_ctx = AgentContext(
            query=query,
            max_iterations=self.max_iterations,
        )
        
        if context:
            agent_ctx.acquired_data.update(context)
        
        logger.info(f"Starting ReAct agent: query={query}")
        
        try:
            # Main reasoning loop
            while agent_ctx.state != AgentState.COMPLETE and agent_ctx.iteration < agent_ctx.max_iterations:
                agent_ctx.iteration += 1
                
                logger.debug(f"Iteration {agent_ctx.iteration}: state={agent_ctx.state.value}")
                
                # Execute based on current state
                if agent_ctx.state == AgentState.PLAN:
                    self._plan(agent_ctx)
                elif agent_ctx.state == AgentState.ACQUIRE:
                    self._acquire(agent_ctx)
                elif agent_ctx.state == AgentState.REASON:
                    self._reason(agent_ctx)
                elif agent_ctx.state == AgentState.ACT:
                    self._act(agent_ctx)
            
            # Check if we completed successfully
            if agent_ctx.state != AgentState.COMPLETE:
                logger.warning(f"Agent reached max iterations without completion")
                agent_ctx.state = AgentState.ERROR
            
            agent_ctx.completed_at = datetime.now()
            
        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            agent_ctx.state = AgentState.ERROR
            agent_ctx.result = str(e)
        
        return agent_ctx
    
    def _plan(self, ctx: AgentContext) -> None:
        """
        Plan phase: Formulate initial hypothesis
        
        Args:
            ctx: Agent context
        """
        # Generate plan using LLM
        prompt = f"""
任务: {ctx.query}

请分析这个任务，并制定执行计划：

1. 明确任务目标
2. 识别需要收集的信息
3. 确定分析步骤
4. 预期输出结果

请给出详细的计划。
"""
        
        messages = [
            {"role": "system", "content": "你是一位专业的交易分析师，擅长制定分析和交易计划。"},
            {"role": "user", "content": prompt},
        ]
        
        response = self.llm.chat_completion(messages, temperature=0.7)
        ctx.plan = response.content
        ctx.thought_history.append(f"Plan: {ctx.plan[:200]}...")
        
        logger.info(f"Plan generated: {ctx.plan[:100]}...")
        
        # Transition to acquire phase
        ctx.state = AgentState.ACQUIRE
    
    def _acquire(self, ctx: AgentContext) -> None:
        """
        Acquire phase: Gather information using tools
        
        Args:
            ctx: Agent context
        """
        # Determine which tool to use
        tool_prompt = f"""
当前计划: {ctx.plan}

可用工具:
{self._format_tools()}

已收集信息: {json.dumps(ctx.acquired_data, ensure_ascii=False, default=str)}

请选择下一步需要使用的工具，并说明理由。
如果已有足够信息，请回复 "信息充足，进入分析阶段"。
"""
        
        messages = [
            {"role": "system", "content": "你是一位信息收集专家，知道如何高效获取所需数据。"},
            {"role": "user", "content": tool_prompt},
        ]
        
        response = self.llm.chat_completion(messages, temperature=0.7)
        decision = response.content
        
        # Check if we have enough information
        if "信息充足" in decision or "进入分析" in decision:
            logger.info("Sufficient information acquired, moving to reason phase")
            ctx.state = AgentState.REASON
            return
        
        # Extract tool to use (simple parsing)
        tool_name = self._extract_tool_name(decision)
        
        if tool_name and tool_name in self.tools:
            # Execute tool
            tool = self.tools[tool_name]
            try:
                result = tool.function(**tool.parameters)
                ctx.acquired_data[tool_name] = result
                ctx.action_history.append(f"Used tool: {tool_name}")
                logger.info(f"Tool executed: {tool_name}")
            except Exception as e:
                logger.error(f"Tool execution failed: {e}")
                ctx.thought_history.append(f"Tool {tool_name} failed: {str(e)}")
        else:
            logger.warning(f"Unknown tool or no tool specified: {tool_name}")
        
        # Continue acquiring or move to reason
        if len(ctx.acquired_data) >= 3:  # Heuristic: if we have 3+ data points, move on
            ctx.state = AgentState.REASON
    
    def _reason(self, ctx: AgentContext) -> None:
        """
        Reason phase: Analyze information and make decision
        
        Args:
            ctx: Agent context
        """
        reason_prompt = f"""
原始任务: {ctx.query}

执行计划: {ctx.plan}

收集的信息:
{json.dumps(ctx.acquired_data, ensure_ascii=False, indent=2, default=str)}

请分析以上信息，并给出：
1. 关键发现
2. 数据支持的结论
3. 推荐的行动方案
4. 潜在风险

请给出详细的分析报告。
"""
        
        messages = [
            {"role": "system", "content": "你是一位资深的投资分析师，擅长综合分析并给出专业建议。"},
            {"role": "user", "content": reason_prompt},
        ]
        
        response = self.llm.chat_completion(messages, temperature=0.7)
        ctx.reasoning = response.content
        ctx.thought_history.append(f"Reasoning: {ctx.reasoning[:200]}...")
        
        logger.info(f"Reasoning completed: {ctx.reasoning[:100]}...")
        
        # Transition to act phase
        ctx.state = AgentState.ACT
    
    def _act(self, ctx: AgentContext) -> None:
        """
        Act phase: Execute final action
        
        Args:
            ctx: Agent context
        """
        act_prompt = f"""
分析结果: {ctx.reasoning}

基于以上分析，请明确最终的行动建议：

1. 具体行动（买入/卖出/持有/观望）
2. 如果是交易，请给出：
   - 股票代码
   - 交易数量
   - 目标价格范围
3. 风险控制措施
4. 后续监控要点

请给出明确可执行的行动方案。
"""
        
        messages = [
            {"role": "system", "content": "你是一位果断的交易决策者，擅长将分析转化为具体行动。"},
            {"role": "user", "content": act_prompt},
        ]
        
        response = self.llm.chat_completion(messages, temperature=0.7)
        ctx.action = response.content
        ctx.result = ctx.action
        
        logger.info(f"Action decided: {ctx.action}")
        
        # Mark as complete
        ctx.state = AgentState.COMPLETE
    
    def _format_tools(self) -> str:
        """Format available tools for display"""
        lines = []
        for name, tool in self.tools.items():
            lines.append(f"- {name}: {tool.description}")
        return "\n".join(lines)
    
    def _extract_tool_name(self, text: str) -> Optional[str]:
        """Extract tool name from LLM response"""
        # Simple extraction - look for tool names in text
        for tool_name in self.tools.keys():
            if tool_name in text:
                return tool_name
        return None
