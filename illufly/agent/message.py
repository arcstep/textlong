import json
from typing import Union, Dict, Any, List, Tuple

from ..hub import Template

class Message:
    def __init__(self, role: str, content: Union[str, Template]):
        self.role = role
        self.content = content

    def __str__(self):
        return f"{self.role}: {self.content}"

    def __repr__(self):
        return f"Message(role={self.role}, content={self.content})"
    
    @property
    def message(self):
        return {
            "role": self.role,
            "content": self.text
        }

    @property
    def text(self):
        if isinstance(self.content, Template):
            return self.content.get_prompt()
        return self.content

    @property
    def json(self):
        return json.dumps({
            "role": self.role,
            "content": self.content
        })

class Messages:
    """
    使用 Messages 类可以简化消息列表的管理。

    构造函数中的 messages 参数将作为原始的「只读对象」，被保存到 self._messages 中。
    无论你提供的列表元素是字符串、模板、元组还是字典，都会在实例化完成后，生成 Message 对象列表，并被写入到 self.messages 中。
    但类似 {"role": xx, "content": yy} 这种消息列表，是通过 self.to_list 方法「动态提取」的，这主要是为了兼容 Template 对象的模板变量。
    """

    def __init__(self, messages: Union[Message, str, Template, Tuple[str, Union[str, Template]], List[Union[Message, str, Template, dict, Tuple[str, Union[str, Template]]]]]):
        self._messages = messages or []
        self.messages = []
        self._convert_to_message_list()

    def _convert_to_message_list(self) -> None:
        if not isinstance(self._messages, list):
            self._messages = [self._messages]

        for i, msg in enumerate(self._messages):
            self.messages.append(self._convert_to_message(msg, i))

    def _convert_to_message(self, msg: Union[Message, str, Template, dict, Tuple[str, Union[str, Template]]], index: int) -> Message:
        if isinstance(msg, Message):
            return msg
        elif isinstance(msg, str):
            role = self._determine_role(index)
            return Message(role=role, content=msg)
        elif isinstance(msg, Template):
            role = self._determine_role(index)
            return Message(role=role, content=msg)
        elif isinstance(msg, dict):
            if msg.get('role') == 'ai':
                msg['role'] = 'assistant'
            return Message(role=msg.get('role', 'user'), content=msg.get('content', ''))
        elif isinstance(msg, tuple) and len(msg) == 2:
            role, content = msg
            if role == 'ai':
                role = 'assistant'
            if role in ['user', 'assistant', 'system']:
                return Message(role=role, content=content)
            else:
                raise ValueError("Unsupported role type in tuple")
        else:
            print("Unsupported message type: ", msg)
            raise ValueError("Unsupported message type")

    def _determine_role(self, index: int) -> str:
        if index == 0:
            return 'system'
        elif self.messages[0].role == 'system' and index == 1:
            return 'user'
        else:
            last_role = self.messages[-1].role if self.messages else 'user'
            return 'assistant' if last_role == 'user' else 'user'

    def __str__(self):
        return "\n".join([str(message) for message in self.messages])

    def __repr__(self):
        return f"<Messages({self.length} items)>"
    
    def to_list(self):
        return [msg.message for msg in self.messages]
    
    def to_json(self):
        return [msg.json for msg in self.messages]
    
    @property
    def length(self):
        return len(self.messages)

    def input_vars(self):
        vars = {}
        for msg in self.messages:
            if isinstance(msg.content, Template):
                vars.update(msg.content.using_vars)
        return vars

    def append(self, message: Union[Message, str, Template, dict, Tuple[str, Union[str, Template]]]):
        self.messages.append(self._convert_to_message(message, len(self.messages)))

    def extend(self, messages: Union[Message, str, Template, Tuple[str, Union[str, Template]], List[Union[Message, str, Template, dict, Tuple[str, Union[str, Template]]]]]):
        for msg in messages:
            self.append(msg)