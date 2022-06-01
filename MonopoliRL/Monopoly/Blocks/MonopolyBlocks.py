import enum
import json
import random
from abc import abstractmethod
import numpy as np


class Blocks:

    list = []

    _instance = None

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    @classmethod
    def reset(cls):
        if cls.list:
            for b in cls.list:
                if isinstance(b, APropriety):
                    b.Reset()
            return cls._instance
        return cls.instance()

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            with open('Monopoly/Blocks/BlocksData.json') as json_file:
                blocks = json.load(json_file)['blocks']
            blocks.sort(key=lambda x: int(x["id"]))
            for b in blocks:
                if b['Type'] == 'Land':
                    cls.list.append(Land(block=b))
                elif b['Type'] == 'Society':
                    cls.list.append(Society(block=b))
                elif b['Type'] == 'Station':
                    cls.list.append(Station(block=b))
                else:
                    temp = EventBlock(block=b)
                    cls.list.append(temp)
        return cls._instance


class APropriety:

    def __init__(self, id, name, price, profit, mortgage):
        self._isMortgage = False
        self.owner = None
        self._free = True
        self.id = id
        name = name.replace("\n", " ")
        self.name = name
        self._price = price
        self._profit = profit
        self._mortgage = mortgage

    @abstractmethod
    def NumberInSeries(self):
        pass

    @abstractmethod
    def Price(self):
        return self._price

    @abstractmethod
    def IsSeries(self):
        pass

    @abstractmethod
    def Profit(self):
        return self._profit

    @abstractmethod
    def MeanProfit(self):
        pass

    def __str__(self):
        idPlayer = "-1" if self.owner is None else self.owner.idPlayer
        return "id:{0}\tName: {1}\nOwner: Player{2}\nPrice: {3}\nProfit: {4}\n".format(self.id, self.name, idPlayer , self._price, self._profit)

    @abstractmethod
    def Buy(self, player):
        player.AddOwnerships(self.id)

        if self.owner is not None:
            self.owner.RemoveOwnerships(self.id)

        self._free = False
        self.owner = player
        return f'Comprato {self.name} al prezzo di {self.Price()}€'

    @abstractmethod
    def Sell(self, toPlayer, price: int):
        self.owner.RemoveOwnerships(self.id)

        fromPlayer = self.owner
        self.owner = toPlayer

        self.owner.AddOwnerships(self.id)
        fromPlayer.Budget(price)
        toPlayer.Budget(-price)
        return f'Scambiata la proprità {self.name}\nalla cifra di {price}€\ndal giocatore {fromPlayer} al {toPlayer}'

    @abstractmethod
    def Reset(self):
        self._isMortgage = False
        self.owner = None
        self._free = True

    @abstractmethod
    def CheckSeries(self, list):
        for item in list:
            if item.owner != self.owner:
                return False
        return True

    def IsFree(self):
        return self._free

    def _NumberInSeries(self, list):
        i = 0
        for item in list:
            if item.owner == self.owner:
                i = i+1
        return i, len(list)

    def Pay(self, player):
        temp = self.Profit()
        player.Budget(-temp)
        self.owner.Budget(temp)
        return f'Pagato {self.Profit()}€ al giocatore {self.owner.color}'

    def MortgageValue(self):
        return self._mortgage['Value']

    def GetMortgage(self):
        return self._isMortgage

    def Mortgage(self):

        if self._isMortgage:
            if self.owner.Budget() >= self._mortgage['Cost']:
                self.owner.Budget(-self._mortgage['Cost'])
                self._isMortgage = not self._isMortgage
        else:
            self.owner.Budget(self._mortgage['Value'])
            self._isMortgage = not self._isMortgage


class EventBlock:
    def __init__(self, block):
        self.id = block['id']
        name = block['Name'].replace("\n", " ")
        self.name = name

        self._actions = [lambda p: "Non fa nulla"]

        if "Vai in Prigione" == self.name:
            self._actions = [lambda p: self._Imprison(p)]

        if "Start" == self.name:
            self._actions = [lambda p: "Passa dal via e guadagna 200€"]

        elif "Tassa" in self.name:
            self._actions = [lambda p: self._SubBudgetToPlayer(p, 200)]

        elif self.name == "Probabilità":
            self._actions = [lambda p: self._AddBudgetToPlayer(p, 10),
                             lambda p: self._AddBudgetToPlayer(p, 10),
                             lambda p: self._AddBudgetToPlayer(p, 100),
                             lambda p: self._AddBudgetToPlayer(p, 100),
                             lambda p: self._AddBudgetToPlayer(p, 100),
                             lambda p: self._AddBudgetToPlayer(p, 200),
                             lambda p: self._AddBudgetToPlayer(p, 50),
                             lambda p: self._AddBudgetToPlayer(p, 25),
                             lambda p: self._AddBudgetToPlayer(p, 20),
                             lambda p: self._MoveAction(p, 0, True),
                             lambda p: self._Imprison(p),
                             lambda p: self._SubBudgetToPlayer(p, 100),
                             lambda p: self._SubBudgetToPlayer(p, 50),
                             lambda p: self._SubBudgetToPlayer(p, 50),
                             ]
        elif self.name == "Imprevisti":
            self._actions = [lambda p: self._AddBudgetToPlayer(p, 50),
                             lambda p: self._AddBudgetToPlayer(p, 150),
                             lambda p: self._MoveAction(p, 0, True),
                             lambda p: self._MoveAction(p, 5, True),
                             lambda p: self._MoveAction(p, 11, True),
                             lambda p: self._MoveAction(p, 24, True),
                             lambda p: self._MoveAction(p, [5, 15, 25, 35].pop(int(np.argmin([abs(p.position-5), abs(p.position-15), abs(p.position-25), abs(p.position-25)])))),
                             lambda p: self._MoveAction(p, [12, 28].pop(int(np.argmin([abs(p.position-12), abs(p.position-28)])))),
                             lambda p: self._MoveAction(p, 39),
                             lambda p: self._Imprison(p),
                             lambda p: self._SubBudgetToPlayer(p, 50),
                             lambda p: self._SubBudgetToPlayer(p, 15),
                             ]

    def Reset(self):
        return None

    def Action(self, player):
        return self._actions[random.randrange(0, len(self._actions))](player)

    def _SubBudgetToPlayer(self, player, budget):
        player.Budget(-budget)
        return f'Paga {budget}€'

    def _AddBudgetToPlayer(self, player, budget):
        player.Budget(budget)
        return f'Guadagna {budget}€'

    def _MoveAction(self, player, position, passThroughStart=False):
        msg = f'Va avanti fino alla posizione {position}'
        if passThroughStart == True and player.position > position:
            player.Budget(200)
            msg = f'{msg}\ned è passato dal via guadagnando 200€'

        player.position = position
        return msg

    def _Imprison(self, player):
        player.imprisoned = True
        player.position = 10
        return "Vai in prigione"

    def _FreePrisonExit(self, player):
        player.freePrisonExit = True
        return "Ha ottenuto un'uscita\ngratis dalla prigione"


class Land(APropriety):
    class EColor(enum.Enum):
        BROWN = 0
        CYAN = 1
        MAGENTA = 2
        ORANGE = 3
        RED = 4
        YELLOW = 5
        GREEN = 6
        BLUE = 7

    _bundledLands = [[[], False], [[], False], [[], False], [[], False], [[], False], [[], False], [[], False], [[], False]]

    def __init__(self, block):
        super().__init__(block['id'], block['Name'], block['Prices'], block['Profits'], block['Mortgage'])
        self._color = self.EColor(block['Color'])
        self._n_house = 0
        self._hotel = False
        self._bundledLands[self._color.value][0].append(self)

    def NumberInSeries(self):
        return self._NumberInSeries(self._bundledLands[self._color.value][0])

    def Price(self) -> int:
        return self._price['Land']

    def IsSeries(self):
        return self._bundledLands[self._color.value][1]

    def Profit(self) -> int:
        temp = self._profit['Single']

        if self.IsSeries():
            temp = self._profit['Series']

        if self._n_house > 0:
            temp = self._profit['House'][self._n_house - 1]

        if self._hotel:
            temp = self._profit['Hotel']
        return temp

    def MeanProfit(self):
        p = 0
        for profit in self._profit['House']:
            p += profit
        return round((self._profit['Single'] + self._profit['Series'] + p + self._profit['Hotel']) / 7)

    def Buy(self, player):
        log = super().Buy(player)

        player.Budget(-self._price['Land'])
        self._bundledLands[self._color.value][1] = self.CheckSeries(self._bundledLands[self._color.value][0])
        return log

    def Sell(self, toPlayer, price: int):
        wasSeries = False
        if self.IsSeries():
            wasSeries = True
            for x in self._bundledLands[self._color.value][0]:
                x._n_house = 0
                x._hotel = False

        super().Sell(toPlayer, price)

        self._bundledLands[self._color.value][1] = False if wasSeries else self.CheckSeries(self._bundledLands[self._color.value][0])
        return f'Venduto: {self.name} a {toPlayer.idPlayer} al prezzo di {price}'

    def Reset(self):
        super().Reset()
        self._n_house = 0
        self._hotel = False
        self._bundledLands[self._color.value][1] = False

    def GetColor(self):
        return self._color

    def PriceHouseOrHotels(self) -> int:
        if not self._hotel:
            return self._price['House']
        else:
            return self._price['Hotel']

    def CanBuyHouse(self):

        if self.IsSeries() and not self._isMortgage:
            if not self._hotel:
                for item in self._bundledLands[self._color.value][0]:
                    if self._n_house > item._n_house and not item._hotel:
                        return False
            else:
                return False

            return True

        return False

    def BuyHouseOrHotels(self):
        if self.CanBuyHouse():
            if self._n_house < 4:
                self._n_house += 1
                self.owner.Budget(-self._price['House'])
                return 'Comprata una casa su {}\n alla cifra di {}€'.format(self.name, self._price['House'])
            else:
                self._n_house = 0
                self._hotel = True
                self.owner.Budget(-self._price['Hotel'])
                return 'Comprata un hotel su {}\n alla cifra di {}€'.format(self.name, self._price['House'])

    def GetHouseOrHotel(self):
        if self._hotel:
            return 5
        if self._n_house <= 4:
            return self._n_house
        return 0


class Society(APropriety):
    _bundledSociety = []

    def __init__(self, block):
        super().__init__(block['id'], block['Name'], block['Prices'], block['Profits'], block['Mortgage'])
        self._isSeries = False
        self._bundledSociety.append(self)

    def NumberInSeries(self):
        return self._NumberInSeries(self._bundledSociety)

    def Price(self) -> int:
        return self._price

    def IsSeries(self):
        return self._isSeries

    def Profit(self) -> int:
        temp = self._profit[0] if not self._isSeries else self._profit[1]
        roll = random.randrange(1, 6) + random.randrange(1, 6)
        return temp * roll

    def MeanProfit(self) -> int:
        return 49

    def Buy(self, player):
        log = super().Buy(player)
        player.Budget(-self._price)

        self._isSeries = self.CheckSeries(self._bundledSociety)
        return log

    def Sell(self, toPlayer, price: int):
        super().Sell(toPlayer, price)
        self._isSeries = self.CheckSeries(self._bundledSociety)

    def Reset(self):
        super().Reset()
        self._isSeries = False


class Station(APropriety):
    _bundledStation = []

    def __init__(self, block):
        super().__init__(block['id'], block['Name'], block['Prices'], block['Profits'], block['Mortgage'])
        self._isSeries = False
        self._bundledStation.append(self)

    def NumberInSeries(self):
        return self._NumberInSeries(self._bundledStation)

    def Price(self) -> int:
        return self._price

    def IsSeries(self):
        return self._isSeries

    def Profit(self) -> int:
        n = -1
        for item in self._bundledStation:
            if item.owner == self.owner:
                n += 1
        return self._profit * pow(2, n)

    def MeanProfit(self) -> int:
        return 94

    def Buy(self, player):
        log = super().Buy(player)
        player.Budget(-self._price)

        self._isSeries = self.CheckSeries(self._bundledStation)
        return log

    def Sell(self, toPlayer, price: int):
        super().Sell(toPlayer, price)
        self._isSeries = self.CheckSeries(self._bundledStation)

    def Reset(self):
        super().Reset()
        self._isSeries = False
