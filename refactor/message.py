from typing import List, Dict, Tuple, Union
from dataclasses import dataclass
import time
from uuid import uuid1
import hashlib

def _hash(input: str):
    hex_dig = hashlib.sha256(input.encode()).hexdigest()
    return hex_dig

@dataclass
class Message():
    agent_name: str
    content: str
    turn: int
    timestamp: int = time.time_ns()
    visible_to: Union[str, List["Agent"]] = "all"

    @property
    def msg_id(self):
        # Generate a unique message id given the content, timestamp and role
        return _hash(f"msg: {self.content}\ntimestamp: {str(self.timestamp)}\nrole: {self.agent_name}")


class MessagePool():
    """
    A message pool to manage the messages. This allows a unified treatment of the visibility of the messages.
    Draft design:
    The message pool is a list of (named) tuples, where each tuple has (turn, role, content).

    There should be two potential configurations for step definition: multiple players can act in the same turn (rock-paper-scissors).
    The agent can only see the messages that
    1) before the current turn, and
    2) visible to the current role
    """

    conversation_id: str
    def __init__(self):
        self._messages = []

    def reset(self):
        self._messages = []

    def append_message(self, message: Message):
        self._messages.append(message)

    def print(self):
        for message in self._messages:
            print(f"{message.content}")

    @property
    def last_turn(self):
        if len(self._messages) == 0:
            return 0
        else:
            return self._messages[-1].turn

    def get_visible_messages(self, agent: "Agent", turn: int) -> List[Message]:
        """
        get the messages that are visible to the agent before the specified turn
        """

        # Get the messages before the current turn
        prev_messages = [message for message in self._messages if message.turn < turn]

        visible_messages = []
        for message in prev_messages:
            if message.visible_to == "all" or agent in message.visible_to:
                visible_messages.append(message)
        return visible_messages
