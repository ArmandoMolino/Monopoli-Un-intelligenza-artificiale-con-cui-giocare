import numpy as np

from Monopoly.Blocks import MonopolyBlocks
from Monopoly.Players.Player_ import APlayer


class AverangePlayer(APlayer):

    _recentTrade = np.zeros(40)

    def __init__(self, budgetWindow=600, tradeCountdown=3, id=0, position=0, budget=1500, color='red', infinite_money=False):
        self.budgetWindow = budgetWindow
        self.tradeCountdown = tradeCountdown
        super().__init__(id=id, position=position, budget=budget, color=color, infinite_money=infinite_money)

    def BuyBehavior(self, propriety: MonopolyBlocks.APropriety, price) -> bool:
        n, tot = propriety.NumberInSeries()
        if self._recentTrade[propriety.id] == 0 and n <= int(tot/2) and self.budgetWindow < (self._budget - price):
            self._recentTrade[propriety.id] = self.tradeCountdown
            return True
        return False

    def SellBehavior(self, propriety: MonopolyBlocks.APropriety, price) -> bool:
        n, tot = propriety.NumberInSeries()
        minSellPrice = propriety.Price() * (1.25 if self._budget < self.budgetWindow else 0.5)
        if self._recentTrade[propriety.id] == 0 and n <= int(tot/2) and minSellPrice <= price:
            self._recentTrade[propriety.id] = self.tradeCountdown
            return True
        return False

    def EndTurnBehavior(self):
        self._recentTrade = [x-1 if x > 0 else x for x in self._recentTrade]
        lands = [x for x in self.OwnedProprietyIDs if type(MonopolyBlocks.Blocks.instance().list[x]) is MonopolyBlocks.Land]
        while len(lands) > 0:
            land = MonopolyBlocks.Blocks.instance().list[max(lands)]
            if land.CanBuyHouse() and self._budget - land.PriceHouseOrHotels() > self.budgetWindow:
                return land.BuyHouseOrHotels()
            lands.remove(max(lands))

        return f'Non ha fatto nulla'