"""
State:
    - Budget del AI
    - Budget del Player
    - Proprietà del AI
    - Case del AI
    - Proprietà del Player
    - Case del Player

Reward:
    Tra 0 e 1   - Reward medio
    1           - Reward massimo
    0           - Reward minimo

Action:
    action = 0                  - Non Fare niente
    action - 1 <= 21            - Comprare proprietà di altri
    21 < action - 1 <= 133      - Comprare Casa
    133 < action - 1 <= 245     - Vendere proprietà
"""

import numpy as np
import pygame
from gym import spaces

from Monopoly.Board.MonopolyBoard import Board
from Monopoly.Blocks.MonopolyBlocks import Blocks, EventBlock, Land
from Monopoly.Players.AverangePlayer import AverangePlayer
from Monopoly.Players.Player_ import Player


class env:
    __multiplier = np.array([1.25, 1.5, 0.75, 0.5])

    def __init__(self, player=None):
        self.action_space = spaces.Discrete(246)

        self.board = False
        self.minReward = 0  # reward minimo
        self.maxReward = 1200  # reward massimo
        self.maxPlayer = 2
        self.__time = 0
        self.blocks = None  # lista contenente tutti i blocchi
        self.proprieties = None  # lista contenente tutti le proprietà
        self.lands = None  # lista contenente tutti i terreni
        self.AI = None  # AI
        self.player = player  # Giocatore
        self.log = {'AI': {'StartTurn': '', 'EndTurn': ''}, 'player': {'StartTurn': '', 'EndTurn': ''},
                    'observation': []}

    def step(self, action):
        observation, reward, done = [], 0, False

        self.log = {'AI': {'StartTurn': '', 'EndTurn': ''}, 'player': {'StartTurn': '', 'EndTurn': ''},
                    'observation': []}

        start_position = self.AI.position
        self.log['AI']['StartTurn'] = self.AI.StartTurn()

        if self.AI.CheckLose():
            self.log['done'] = 'L\'AI ha perso'
            return self._GetObs(), self._NormalizeReward(self.minReward), True, self.log

        if start_position > self.AI.position:
            # aumenta questo valore solo se l'AI ha completato un giro sul tabellone
            self.__time += 1

        if self.__time == 50:
            # dopo 50 giri sul tabellone termina
            self.log['done'] = '50 giri sul tabellone effettuati'
            return self._GetObs(), self._NormalizeReward(self.AI.Budget() - self.player.Budget()), True, self.log

        if action == 0:
            reward = (1 / (1 + pow(abs(self.AI.Budget() - self.player.Budget()), 0.175))) * ((self.AI.MaxBudget()/2) / pow(self.AI.Budget() + self.player.Budget(), 0.5))
            observation, done = self._GetObs(), False
            self.log['AI']['EndTurn'] = f'Non ha fatto nulla'
        else:
            action -= 1
            """
                Seglie un azione:
                - action <= 21: Compra una Compra una Casa o un Hotel(id = action)
                - 21 < action <= 133: Vende una Proprietà(id = (action - 22) >> 2) % _len) al 
                        prezzo = _proprieties[idBlock].Price() * self.__multiplier[(action - 22) & 3]
                - 133 < action <= 245: Vende una Proprietà(id = ((action - 134) >> 2) % _len) al 
                        prezzo = _proprieties[idBlock].Price() * self.__multiplier[(action - 134) & 3]
                Se l'azione non è valida il reward è uguale al minimo
            """
            if action <= 21:
                _lands = [land for land in self.lands
                          if land.id in self.AI.OwnedProprietyIDs
                          and land.CanBuyHouse()
                          and self.AI.Budget() > land.PriceHouseOrHotels()
                          ]
                _len = len(_lands)
                if _len > 0:
                    self.log['AI']['EndTurn'] = _lands[action % _len].BuyHouseOrHotels()
                    reward = (_lands[action % _len].Profit() * 0.0015) * pow(self.AI.Budget(), 0.85)
                    observation, done = self._GetObs(), False

            elif 21 < action <= 133:  # comprare
                _proprieties = [propriety for propriety in self.proprieties
                                if propriety.id in self.player.OwnedProprietyIDs]
                _len = len(_proprieties)
                if _len > 0:
                    idBlock = ((action - 22) >> 2) % _len
                    price = _proprieties[idBlock].Price() * self.__multiplier[(action - 22) & 3]
                    if self.AI.Budget() > price:
                        if self.player.SellBehavior(_proprieties[idBlock], price):
                            self.log['AI']['EndTurn'] = _proprieties[idBlock].Sell(self.AI, price)
                            reward = _proprieties[idBlock].Profit() * pow(self.AI.Budget(), 0.50) / pow(self.player.Budget(), 0.6)
                            observation, done = self._GetObs(), False

            elif 133 < action <= 245:  # vendere
                _proprieties = [propriety for propriety in self.proprieties
                                if propriety.id in self.AI.OwnedProprietyIDs]
                _len = len(_proprieties)
                if _len > 0:
                    idBlock = ((action - 134) >> 2) % _len
                    price = _proprieties[idBlock].Price() * self.__multiplier[(action - 134) & 3]
                    if self.player.BuyBehavior(_proprieties[idBlock], price):
                        self.log['AI']['EndTurn'] = _proprieties[idBlock].Sell(self.player, price)
                        reward = _proprieties[idBlock].Profit() * pow(self.player.Budget(), 0.50) / pow(self.AI.Budget(), 0.55) * self.__multiplier[(action - 134) & 3]
                        observation, done = self._GetObs(), False

        # Se il secondo player perde termina
        self.log['player']['StartTurn'] = self.player.StartTurn()
        if not self.player.CheckLose():
            self.log['player']['EndTurn'] = self.player.EndTurnBehavior()
        else:
            self.log['done'] = 'Il player ha perso'
            return self._GetObs(), self._NormalizeReward(self.maxReward), True, self.log

        if reward == 0:
            observation, reward, done = self._GetObs(), self.minReward, False
            self.log['AI']['EndTurn'] += f'Azione non valida'

        self.log['observation'] = observation
        return observation, self._NormalizeReward(reward), done, self.log

    def reset(self):
        def LoopNTimes(n):
            self.__time = 0
            while self.__time < n:
                start_position = self.AI.position
                self.AI.StartTurn()
                if start_position > self.AI.position:
                    # aumenta questo valore solo se l'AI ha completato un giro sul tabellone
                    self.__time += 1
                self.player.StartTurn()

            return not self.player.CheckLose() and not self.AI.CheckLose()

        while True:
            self.blocks = Blocks.reset().list
            self.lands = [x for x in self.blocks if type(x) is Land]
            self.proprieties = [x for x in self.blocks if type(x) is not EventBlock]

            self.AI = Player(id=0, budget=1500, color='red')
            if isinstance(self.player, AverangePlayer):
                self.player = AverangePlayer(budgetWindow=self.player.budgetWindow,
                                             tradeCountdown=self.player.tradeCountdown, id=1, budget=1500, color='blue')
            else:
                self.player = Player(id=1, budget=1500, color='blue')

            if LoopNTimes(2):
                break

        self.board = False
        self.log = {'AI': {'StartTurn': '', 'EndTurn': ''}, 'player': {'StartTurn': '', 'EndTurn': ''},
                    'observation': []}
        self.__time = 0
        return self._GetObs()

    def _NormalizeReward(self, reward, min=0, max=1):
        """Normalizzazione min-max"""
        if reward <= self.minReward:
            return min
        if reward >= self.maxReward:
            return max
        return ((reward - self.minReward) / (self.maxReward - self.minReward) * (max - min)) + min

    def _GetObs(self):
        """
            Calcola lo stato attuale dell'enviroment
            Player1 = AI
            Player2 = Giocatore
            Observation =
            [
                Budget del Player 1,
                Budget del Player 2,
                Proprietà del Player 1,
                Case del Player1
                Proprietà del Player 2,
            ]
        """
        lands = set([land.id for land in self.lands])
        self.AI.OwnedProprietyIDs.sort()
        self.player.OwnedProprietyIDs.sort()
        return \
            [
                self.AI.Budget(),
                self.player.Budget(),
                self.AI.OwnedProprietyIDs,
                [self.blocks[landIDs].GetHouseOrHotel() for landIDs in self.AI.OwnedProprietyIDs if landIDs in lands],
                self.player.OwnedProprietyIDs,
                [self.blocks[landIDs].GetHouseOrHotel() for landIDs in self.player.OwnedProprietyIDs if
                 landIDs in lands],
            ]

    def render(self):

        if not self.board:
            Board.instance().StartGame(blocks=self.blocks, AI=self.AI, player=self.player)
            Board.instance().blockSpriteGroup.update()
            pygame.display.update()
            self.board = True
        else:
            # creates time delay of 10ms
            pygame.time.delay(10)

            Board.instance().update(
                'Azione all\'inizio del Turno\n{}\nAzione alla fine del Turno\n{}'.format(self.log['AI']['StartTurn'],
                                                                                          self.log['AI']['EndTurn']),
                'Azione all\'inizio del Turno\n{}\nAzione alla fine del Turno\n{}'.format(
                    self.log['player']['StartTurn'], self.log['player']['EndTurn']))
