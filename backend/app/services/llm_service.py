"""LLM服务模块"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from ..config import get_settings
import os

# 全局LLM实例
_llm_instance = None


def get_llm() -> ChatOpenAI:
    """
    获取LLM实例(单例模式)
    
    Returns:
        ChatOpenAI实例
    """
    global _llm_instance
    
    if _llm_instance is None:
        settings = get_settings()
        
        # 从环境变量获取LLM配置
        llm_api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        llm_base_url = os.getenv("LLM_BASE_URL") or settings.openai_base_url
        llm_model = os.getenv("LLM_MODEL_ID") or settings.openai_model
        
        if not llm_api_key:
            raise ValueError("LLM_API_KEY或OPENAI_API_KEY未配置")
        
        _llm_instance = ChatOpenAI(
            api_key=llm_api_key,
            base_url=llm_base_url,
            model=llm_model,
            temperature=0.7,
            max_tokens=4096
        )
        
        print(f"✅ LLM服务初始化成功")
        print(f"   提供商: OpenAI兼容")
        print(f"   模型: {llm_model}")
        print(f"   Base URL: {llm_base_url}")
    
    return _llm_instance


def reset_llm():
    """重置LLM实例(用于测试或重新配置)"""
    global _llm_instance
    _llm_instance = None


def run_prompt(prompt: str, input_data: dict = None) -> str:
    """
    运行提示词并返回结果
    
    Args:
        prompt: 系统提示词模板
        input_data: 输入数据字典
        
    Returns:
        LLM响应字符串
    """
    llm = get_llm()
    output_parser = StrOutputParser()
    
    if input_data:
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", prompt),
            ("human", "{input}")
        ])
        chain = prompt_template | llm | output_parser
        result = chain.invoke({"input": ""})
    else:
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", prompt)
        ])
        chain = prompt_template | llm | output_parser
        result = chain.invoke({})
    
    return result