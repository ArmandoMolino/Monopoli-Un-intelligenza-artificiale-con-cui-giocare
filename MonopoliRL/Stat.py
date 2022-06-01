import math
import os

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


class Stat(object):
    def __init__(self, num_episodes, label=''):
        self._episode_lengths = np.zeros(num_episodes)
        self._episode_rewards = np.zeros(num_episodes)
        self._win_rate = np.zeros(2)
        self._winRateLabel = ["Player 0(red)", "Player 1(blue)"]
        self._win_block = np.zeros(40)
        self._blockLabel = ["Via", 'Vicolo\nCorto', 'Probabilità\n1', 'Vicolo\nStretto', "Tassa\nPatrimoniale\n1",
                            "Stazione\nSud", "Bastioni\nGran\nSasso", "Imprevisti\n1", "Viale\nMonterosa",
                            "Viale\nVesuvio", "Transito", "Via\nAccademia", "Società\nElettrica", "Corso\nAteneo",
                            "Piazza\nUniversità", "Stazione\nOvest", "Via\nVerdi", "Probabilità\n2", "Corso\nRaffaello",
                            "Piazza\nDante", "Parcheggio", "Via\nMarco\nPolo", "Imprevisti\n2", "Corso\nMagellano",
                            "Largo\nColombo", "Stazione\nNord", "Viale\nCostantino", "Viale\nTraiano", "Fontane",
                            "Piazza\nGiulio\nCesare", "In\nprigione", "Via\nRoma", "Corso\nImpero", "Probabilità\n3",
                            "Largo\nAugusto", "Stazione\nEst", "Imprevisti\n3", "Viale\ndei\nGiardini",
                            "Tassa\nPatrimoniale\n2", "Parco\ndella\nVittoria", "Prigione"]
        self.label = label

    def __str__(self):
        np.set_printoptions(threshold=np.inf)
        return f'episode_lengths={self._episode_lengths} \n \
        episode_rewards={self._episode_rewards} \n \
        win_rate={self._win_rate} \n \
        _win_block={self._win_block}'

    def __repr__(self):
        return f'episode_lengths={self._episode_lengths} \n \
        episode_rewards={self._episode_rewards} \n \
        win_rate={self._win_rate} \n \
        _win_block={self._win_block}'


    def save(self, dir=''):
        with open(f'{dir}episode_lengths{self.label}.npy', 'wb') as f:
            np.save(f, self._episode_lengths)

        with open(f'{dir}episode_rewards{self.label}.npy', 'wb') as f:
            np.save(f, self._episode_rewards)

        with open(f'{dir}win_rate{self.label}.npy', 'wb') as f:
            np.save(f, self._win_rate)

        with open(f'{dir}win_block{self.label}.npy', 'wb') as f:
            np.save(f, self._win_block)

    def load(self, dir=''):
        with open(f'{dir}episode_lengths{self.label}.npy', 'rb') as f:
            self._episode_lengths = np.load(f)

        with open(f'{dir}episode_rewards{self.label}.npy', 'rb') as f:
            self._episode_rewards = np.load(f)

        with open(f'{dir}win_rate{self.label}.npy', 'rb') as f:
            self._win_rate = np.load(f)

        with open(f'{dir}win_block{self.label}.npy', 'rb') as f:
            self._win_block = np.load(f)

    def set_episode_lengths(self, episode):
        self._episode_lengths[episode] += 1

    def set_episode_rewards(self, episode, reward):
        self._episode_rewards[episode] += reward

    def set_win_rate(self, id):
        self._win_rate[id] += 1

    def set_win_block(self, ids):
        for id in ids:
            self._win_block[id] += 1

    @classmethod
    def plot_stats(cls, stats, width=0.85, noshow=False, title_font=None, ax_font=None, smoothing_window=100):
        if ax_font is None:
            ax_font = {'family': 'serif', 'color': 'black', 'size': 18}
        if title_font is None:
            title_font = {'family': 'serif', 'color': 'darkblue', 'size': 20}

        def show_plt():
            if not noshow:
                plt.show()

        # plot
        with plt.style.context("ggplot"):
            fig, axs = plt.subplots()
            cls._plot_bar(axs, [s._win_rate for s in stats], stats[0]._winRateLabel,
                          "Probabilità di vittoria", "Giocatore", "Probabilità", width=width,
                          title_font=title_font, ax_font=ax_font)
            show_plt()

            fig, axs = plt.subplots()
            cls._plot_bar(axs, [s._win_block for s in stats],  stats[0]._blockLabel,
                          "Probabilità di vittoria", "Giocatore", "Probabilità", width=width,
                          title_font=title_font, ax_font=ax_font)
            show_plt()

            fig, axs = plt.subplots()
            rewards_smoothed = [np.array(pd.Series(s._episode_rewards).rolling(smoothing_window, min_periods=smoothing_window).mean()) for s in stats]
            cls._plot(axs, rewards_smoothed, [s.label for s in stats], "Ricompense per episodio", "Episodio", "Ricompensa Totale",
                          title_font=title_font, ax_font=ax_font)
            show_plt()

    @classmethod
    def _plot_bar(cls, ax, data, label, title, xlabel, ylabel, width=0.85, probabilities=True, labelsize=10, title_font=None, ax_font=None):
        d = []
        for i, k in enumerate(data):
            n = k.sum()
            if probabilities:
                d.append([round(s * 100 / n, 2) for s in k])
            else:
                d.append(k)

        plt.rc('xtick', labelsize=labelsize)
        c = width/2
        bar = []
        for i, k in enumerate(d):
            x = np.arange(0, len(k)*np.ceil(len(d)/2), np.ceil(len(d)/2))
            if len(d) % 2 == 0:
                bar.append(ax.bar(x + c + (i - len(d)/2) * width, k, width))
            else:
                bar.append(ax.bar(x + (i - math.floor(len(d)/2)) * width, k, width))

        ax.set_title(title, fontdict=title_font)

        ax.set_xlabel(xlabel, fontdict=ax_font)
        ax.set_ylabel(ylabel, fontdict=ax_font)

        x = np.arange(0, len(label) * np.ceil(len(d)/2), np.ceil(len(d)/2))
        ax.set_xticks(x, label)
        ax.grid(visible=True)

    @classmethod
    def _plot(cls, ax, data, label, title, xlabel, ylabel, labelsize=12, title_font=None, ax_font=None):

        ax.tick_params(axis='both', which='major', labelsize=labelsize)

        for i, d in enumerate(data):
            ax.plot(d)

        ax.set_title(title, fontdict=title_font)
        ax.legend(labels=label, fontsize=15)
        ax.set_xlabel(xlabel, fontdict=ax_font)
        ax.set_ylabel(ylabel, fontdict=ax_font)

        ax.grid(visible=True)
