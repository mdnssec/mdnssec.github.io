import json
from typing import List, Dict, Any
from openai import OpenAI
from openai.types.chat.chat_completion import Choice

class LLMHandler:
    """
    封装与大语言模型（LLM）交互的逻辑，包括API调用和结果缓存。
    """
    def __init__(self, api_key: str, base_url: str):
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.cache = {}

    def _chat(self, messages: List[Dict[str, str]]) -> Choice:
        completion = self.client.chat.completions.create(
            model="moonshot-v1-auto",
            messages=messages,
            temperature=0.3,
            tools=[
                {
                    "type": "builtin_function",
                    "function": {"name": "$web_search"},
                }
            ]
        )
        return completion.choices[0]

    def _search_impl(self, arguments: Dict[str, Any]) -> Any:
        return arguments

    def describe_service(self, service_name: str) -> str:
        """
        使用大模型对服务名进行语义描述，带缓存。
        """
        if service_name in self.cache:
            return self.cache[service_name]

        messages = [
            {"role": "system", "content": "Using English to Answer the following questions"},
            {"role": "user", "content": f'What service is "{service_name}"? Briefly, summarize the application scenarios, common devices, and service types of the service in a few sentences.'}
        ]

        finish_reason = None
        while finish_reason is None or finish_reason == "tool_calls":
            choice = self._chat(messages)
            finish_reason = choice.finish_reason
            messages.append(choice.message)
            if finish_reason == "tool_calls":
                for tool_call in choice.message.tool_calls:
                    tool_call_name = tool_call.function.name
                    tool_call_arguments = json.loads(tool_call.function.arguments)
                    if tool_call_name == "$web_search":
                        tool_result = self._search_impl(tool_call_arguments)
                    else:
                        tool_result = f"Error: unable to find tool by name '{tool_call_name}'"
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call_name,
                        "content": json.dumps(tool_result),
                    })
        
        text = choice.message.content
        print(f"LLM Description for '{service_name}':\n{text}\n")
        self.cache[service_name] = text
        return text

    def batch_describe(self, services: List[str]) -> Dict[str, str]:
        """
        批量获取服务名解释，并返回完整的缓存。
        """
        for name in services:
            self.describe_service(name)
        return self.cache
