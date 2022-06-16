import random
from abc import abstractmethod

from Monopoly.Blocks.MonopolyBlocks import APropriety, Blocks, EventBlock, Land


class APlayer:  # template method design pattern

    _maxBudget = 4000

    def __init__(self, id=0, position=0, budget=1500, color='red', infinite_money=False):
        self.position = position
        self.step = 0
        self.color = color
        self.idPlayer = id
        self._budget = budget
        self.canRoll = False
        self.imprisoned = False
        self.freePrisonExit = False
        self.attempt = 0
        self.infinite_money = infinite_money
        self.OwnedProprietyIDs = []

    def __str__(self) -> str:
        return f"Player {self.idPlayer} ({self.color})"

    def Budget(self, v=0):
        self._budget += v
        if self._budget >= self._maxBudget or self.infinite_money:
            self._budget = self._maxBudget
        return self._budget

    def MaxBudget(self):
        return self._maxBudget

    def RemoveOwnerships(self, id):
        self.OwnedProprietyIDs.remove(id)

    def AddOwnerships(self, id):
        self.OwnedProprietyIDs.append(id)

    def CheckLose(self) -> bool:
        if self._budget < 0:
            self._Lose()
            return True
        return False

    def _Lose(self):
        for id in self.OwnedProprietyIDs:
            Blocks.instance().list[id].Reset()

    def _Roll(self):

        attempt = 0
        dice1, dice2 = random.randrange(1, 6), random.randrange(1, 6)
        diceroll = dice1 + dice2

        while dice1 == dice2 and attempt < 3:
            dice1, dice2 = random.randrange(1, 6), random.randrange(1, 6)
            diceroll += dice1 + dice2
            attempt += 1

        if attempt < 3:
            self.step = diceroll
        else:
            self.position = 10
            self.imprisoned = True

    def StartTurn(self):
        self.step = 0
        if self.imprisoned:
            self.TryToExitFromPrison()
            if self.imprisoned:
                return 'In prigione'

        if self.step == 0:
            self._Roll()
            if self.imprisoned:
                return 'Troppi lanci doppi di dadi\nVAI IN PRIGIONE'

        temp = self.position
        self.position = (self.position + self.step) % 40

        if (temp > self.position):
            self._budget += 200

        if not isinstance(Blocks.instance().list[self.position], EventBlock):
            return self._DoActionOnBlock(Blocks.instance().list[self.position])
        else:
            return Blocks.instance().list[self.position].Action(player=self)

    def _DoActionOnBlock(self, block: APropriety):

        if block.owner is not None and block.owner.idPlayer == self.idPlayer:
            return f'{block.name} di sua proprietà'

        if not block.IsFree():
            return block.Pay(player=self)

        else:
            if block.Price() >= self._budget:
                return f'Non compra {block.name}'

            if isinstance(block, Land):
                landsOwner = [x.owner for x in Blocks.instance().list if isinstance(x, Land) and x.GetColor() == block.GetColor()]
                if self.idPlayer in [x.idPlayer for x in landsOwner if x is not None]:
                    return block.Buy(player=self)
                else:
                    tot = len(landsOwner)
                    n = len([x for x in landsOwner if x is None])

                    if n == tot:
                        return block.Buy(player=self)
                    elif n > int(tot/2) and random.randrange(0, 100) < 10:
                        return block.Buy(player=self)
            else:
                blockOwner = [x.owner for x in Blocks.instance().list if isinstance(x, type(block))]
                if self.idPlayer in [x.idPlayer for x in blockOwner if x is not None]:
                    return block.Buy(player=self)
                else:
                    tot = len(blockOwner)
                    n = len([x for x in blockOwner if x is None])

                    if n == tot:
                        return block.Buy(player=self)
                    elif n > int(tot/2) and random.randrange(0, 100) < 10:
                        return block.Buy(player=self)

        return f'Non compra {block.name}'

    @abstractmethod
    def BuyBehavior(self, propriety: APropriety, price) -> bool:
        # comportamento ad una proposta di acquisto, cioè se accetta o rifiuta la proposta
        pass

    @abstractmethod
    def SellBehavior(self, propriety: APropriety, price) -> bool:
        # comportamento ad una proposta di vendita, cioè se accetta o rifiuta la proposta
        pass

    @abstractmethod
    def EndTurnBehavior(self):
        pass

    def TryToExitFromPrison(self):
        self.attempt = 0
        if self.freePrisonExit:
            self.freePrisonExit = False
            self.imprisoned = False

        elif self._budget > 50:
            if self.attempt < 3 and random.randrange(0, 100) < 25:
                dice1, dice2 = random.randrange(1, 6), random.randrange(1, 6)
                if dice1 == dice2:
                    self.imprisoned = False
                    self.attempt = 0
                    self.step = dice1 + dice2
            else:
                self.Budget(-50)
                self.imprisoned = False
                self.attempt = 0
        elif self.attempt < 3:
            dice1, dice2 = random.randrange(1, 6), random.randrange(1, 6)
            if dice1 == dice2:
                self.imprisoned = False
                self.attempt = 0
                self.step = dice1 + dice2
        else:
            self.Budget(-50)
            self.imprisoned = False
            self.attempt = 0



class Player(APlayer):

    def BuyBehavior(self, propriety: APropriety, price) -> bool:
        return True

    def SellBehavior(self, propriety: APropriety, price) -> bool:
        return True

    def EndTurnBehavior(self):
        pass
