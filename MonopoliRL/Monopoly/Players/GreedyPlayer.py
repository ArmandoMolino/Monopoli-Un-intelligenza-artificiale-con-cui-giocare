import numpy as np

from Monopoly.Blocks import MonopolyBlocks
from Monopoly.Players.Player_ import APlayer


class GreedyPlayer(APlayer):

    _recentTrade = np.zeros(40)

    def __init__(self, budgetWindow=600, tradeCountdown=3, id=0, position=0, budget=1500, color='red', infinite_money=False):
        self.budgetWindow = budgetWindow
        self.tradeCountdown = tradeCountdown
        super().__init__(id=id, position=position, budget=budget, color=color, infinite_money=infinite_money)

    def BuyBehavior(self, propriety: MonopolyBlocks.APropriety, price) -> bool:
        return True

    def SellBehavior(self, propriety: MonopolyBlocks.APropriety, price) -> bool:
        return False

    def EndTurnBehavior(self):
        self._recentTrade = [x-1 if x > 0 else x for x in self._recentTrade]
        lands = [x for x in self.OwnedProprietyIDs if type(MonopolyBlocks.Blocks.instance().list[x]) is MonopolyBlocks.Land]
        while len(lands) > 0:
            land = MonopolyBlocks.Blocks.instance().list[max(lands)]
            if land.CanBuyHouse() and self._budget - land.PriceHouseOrHotels() > self.budgetWindow:
                land.BuyHouseOrHotels()
            lands.remove(max(lands))

        return f'Non ha fatto nulla'