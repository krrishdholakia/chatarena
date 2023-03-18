from typing import List
from refactor.agent import Player, Moderator, Agent
from refactor.environment import Environment
from refactor.intelligence import OpenAIChat
from refactor.environment import Conversation


class Arena():
    """
    central module that manages the game environment and players
    """
    def __init__(self, players: List[Player], environment: Environment):
        self.players = players
        self.environment = environment
        self.current_timestep = self.environment.reset()

    @property
    def num_players(self):
        return len(self.players)

    @property
    def all_agents(self) -> List[Agent]:
        return self.players + [self.environment.moderator]

    @staticmethod
    def create_from_config(config):
        raise NotImplementedError()

    def next_step(self):
        """
        take the action and return the next step
        """
        player = self.environment.get_next_player()
        action = player.decide(self.current_timestep.observation)
        timestep = self.environment.step(action)
        self.current_timestep = timestep
        return timestep



# NOTE(zhengyao): this is a test case
if __name__ == "__main__":
    config = {
            "system_desc": "Two players are playing tic-tac-toe. \nTic-tac-toe is played on a three-by-three grid by two players, who alternately place the marks X and O in one of the nine spaces in the grid. \nThe player who succeeds in placing three of their marks in a horizontal, vertical, or diagonal row is the winner.\n\nIn the following example, the first player (X) wins the game in seven steps:\n1. [Player 1]: X: (1, 3)\n| _ |_| X |\n| _ | _ |_|\n| _ | _ |_|\n      \n2. [Player 2]: O: (1, 1)\n| O | _ | X |\n| _ | _ |_|\n| _ |_| _ |\n\n3. [Player 1]: X: (3, 1)\n| O | _ | X |\n| _ |_| _ |\n| X | _ |_|\n\n4.  [Player 2]: O: (2, 2)\n| O | _ | X |\n| _ | O | _ |\n| X | _ |_|\n\n5. [Player 1]: X: (3, 3)\n| O | _ | X |\n| _ | O | _ |\n| X | _ | X |\n\n6. [Player 2]: O: (2, 3)\n| O | _ | X |\n| _ | O |O|\n| X | _ | X |\n\n7. [Player 1]: X: (3, 2)\n| O | _ | X |\n| _ | O |O|\n| X |X| X |\n\n\nX plays first. Players will specify the position of the stone and the moderator will plot the board status.\nIf a position has been marked, future marks cannot be put in the same position.\nOnly the moderator can decide who wins. Players shouldn't declare they win.\nThe players interact with the game by specifying the position of the stones (x, y), where x indicates the row and y indicates the column, so (1, 1) is the top left corner and (3, 3) is the bottom right corner.",
            "next_speaker_strategy": "Round-robin",
            "auto_terminate": True,
            "max_turns": 9,
            "moderator_role": "You are the system of the game.\nYou should first recall the latest move and then display the board status.\n\nFor example, when the last player says: \"X: (1, 2)\"\nIt means the X mark is put in the first row and the second column.\nYou'll output:\n```\nBoard:\n| _ | X | _ |\n| _ |_| _ |\n| _ |_| _ |\n```\n\nIn the next step, another player says: \"O: (3, 1)\"\nIt means the O mark is put in the third row and the first column.\nYou'll output:\n```\nBoard:\n| _ |_| X |\n| _ |_| _ |\n| O | _ |_|\n```\n\n## Termination condition\nIf a player succeeds in placing three of their marks in a horizontal, vertical, or diagonal line, it wins. \nThe horizontal line means there are three same marks in the same row (n, 1) (n, 2) (n, 3), where n can be from 1 to 3.\nThe vertical line means there are three same marks in the same column (1, m) (2, m) (3, m), where m can be from 1 to 3.\nThe diagonal line means three same marks occupy one of the following position combinations: (1, 1) (2, 2) (3, 3) or (1, 3) (2, 2) (3, 1)\n\nYou should declare the winner after displaying the board status if a player wins the game in the last move.\nFor example, you should output the following:\n```\nBoard\n| O | _ | X |\n| _ | X | O |\n| X |X| O |\n\nPlayer 1 (X) wins!\n```\nbecause X marks form a diagonal line on the board, so the player who plays X is the winner. The game ends.\n\n\n\n## Other instructions\nDon't write code.\nDon't instruct the player to do anything.\nDon't output \"Moderator\".",
            "moderator_next_player_prompt": "Who speaks next?",
            "moderator_end_criteria": "If a player wins, the game ends immediately. Is the game ended? Answer yes or no?",
            "moderator_temperature": 0.2,
            "moderator_max_tokens": 50,
            "player1_role": "You play X.\nYou should only output X and the position of the move, for example: \"X: (1, 3)<EOS>\"\nThe position you put the mark on must be empty.\n\nYou shouldn't act as a moderator.\nDo not output \"Moderator\" and the board status.\nDon't say anything besides mark position.",
            "player1_temperature": 0.7,
            "player1_max_tokens": 15,
            "player2_role": "You play O.\nYou should only output O and the position of the move, for example: \"O: (2, 3)<EOS>\"\nThe position you put the mark on must be empty.\n\nYou shouldn't act as a moderator.\nDo not output \"Moderator\" and the board status.\nDon't say anything besides mark position.",
            "player2_temperature": 0.7,
            "player2_max_tokens": 15
    }

    chatgpt = OpenAIChat(temperature=0.1, max_tokens=20)
    player1 = Player(name="Player 1",
                     intelligence_source=OpenAIChat(temperature=config["player1_temperature"],
                                                    max_tokens=config["player1_max_tokens"]),
                     public_prompt=config["system_desc"],
                     private_prompt=config["player1_role"])
    player2 = Player(name="Player 2",
                     intelligence_source=OpenAIChat(temperature=config["player2_temperature"],
                                                    max_tokens=config["player2_max_tokens"]),
                     public_prompt=config["system_desc"],
                     private_prompt=config["player2_role"])

    environment = Conversation(moderator_intelligence_source=OpenAIChat(temperature=config["moderator_temperature"],
                                                                        max_tokens=config["moderator_max_tokens"]),
                              moderator_role_description=config["moderator_role"],
                              public_prompt=config["system_desc"],
                              terminate_prompt=config["moderator_end_criteria"],
                              parallel=False,
                              max_turns=config["max_turns"],
                              auto_terminate=config["auto_terminate"],
                              players=[player1, player2],
                              )

    arena = Arena(players=[player1, player2], environment=environment)
    arena.next_step()
    environment.print_message_pool()

    arena.next_step()
    environment.print_message_pool()


