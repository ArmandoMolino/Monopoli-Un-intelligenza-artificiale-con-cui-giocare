#!/Path to/MonopolyVenv/bin/python
import glob
import os
import tarfile
import sys
import getopt
import re

from Monopoly import MonopolyEnv
from FuzzyQLearning import StateVariable
from FuzzyQLearning import FuzzySet
from FuzzyQLearning import FQL
from FuzzyQLearning import FIS

from Monopoly.Players.AverangePlayer import AverangePlayer
from Stat import Stat

# Create FIS
x1 = StateVariable.InputStateVariable(FuzzySet.Trapeziums(0, 750, 1250, 1500),
                                      FuzzySet.Trapeziums(1250, 1500, 2250, 2750),
                                      FuzzySet.Trapeziums(2250, 2750, 3750, 4000))

x2 = StateVariable.InputStateVariable(FuzzySet.Triangles(0, 1000, 1250),
                                      FuzzySet.Triangles(1000, 1250, 1700),
                                      FuzzySet.Trapeziums(1250, 1700, 4000, 4000))

x3 = StateVariable.InputStateVariable(FuzzySet.Estate([1, 3]),
                                      FuzzySet.Estate([6, 8, 9]),
                                      FuzzySet.Estate([11, 13, 14]),
                                      FuzzySet.Estate([16, 18, 19]),
                                      FuzzySet.Estate([21, 23, 24]),
                                      FuzzySet.Estate([26, 27, 29]),
                                      FuzzySet.Estate([31, 32, 34]),
                                      FuzzySet.Estate([37, 39]),
                                      FuzzySet.Estate([5, 15, 25, 35]),
                                      FuzzySet.Estate([12, 28]))

x4 = StateVariable.InputStateVariable(FuzzySet.Houses([-0.00001, 4, 5, 5], 'trapeziums'))

fis = FIS.Build(x1, x2, x3, x4, x3, x4)
env = MonopolyEnv.env(player=AverangePlayer(budgetWindow=1000))
observation = env.reset()


def Load(m, s) -> int:
    f = glob.glob(f'*{m}.tar.gz')
    i = int(re.findall(r'\d+', f[0])[0])
    t = tarfile.open(f[0], "r:gz")
    t.extractall()
    m.load()
    s.load()

    files = glob.glob(f'*{m}.npy')
    for file in files:
        os.remove(file)
    return i


def Save(m, s, e):
    m.save()
    s.save()
    file = glob.glob(f'*{m}.tar.gz')
    try:
        os.remove(file[0])
    except:
        pass

    tar = tarfile.open(f"result({e}){model}.tar.gz", "w:gz")
    files = glob.glob(f'*{model}.npy')
    for f in files:
        tar.add(f)
        os.remove(f)
    tar.close()


def Training(model, stat, episodes=1000, start=0, print_info=100, save=False, save_step=0, record_stat=False,
             render=False,
             log=True):
    for i_episode in range(start, start + episodes):
        if i_episode % print_info == 0:
            print("\rEpisode {}/{}.".format(i_episode - start, episodes))
            sys.stdout.flush()
        if save and (i_episode % save_step == 0):
            Save(model, stat, i_episode)

        observation = env.reset()
        if render:
            env.render()
        action = model.get_initial_action(observation)
        done = False
        while not done:
            observation, reward, done, msg = env.step(action)
            if render:
                env.render()
            action = model.run(observation, reward)
            if record_stat:
                stat.set_episode_lengths(i_episode)
                stat.set_episode_rewards(i_episode, reward)
            if log:
                print(msg['AI'])
                print(msg['player'])
                print(msg['observation'])
                print("\n")

        if log:
            print(msg['done'])

        if record_stat:
            if not env.AI.CheckLose():
                stat.set_win_block(env.AI.OwnedProprietyIDs)
                stat.set_win_rate(env.AI.idPlayer)
            else:
                stat.set_win_rate(env.player.idPlayer)

    return stat


try:
    opts, args = getopt.getopt(sys.argv[1:], "ls:pr", ["load", "save=", "plot", "render", "no_log"])
except getopt.GetoptError as err:
    print(err)
    sys.exit(2)

save = False
load = False
plot = False
training = False
render = False
log = True
save_step = 0
i = 0
q_initial_value = 'zeros'
for o, a in opts:
    if o in ["-l", "--load"]:
        load = True
    if o in ["-s", "--save"]:
        save = True
        save_step = int(a)
    if o in ["-p", "--plot"]:
        plot = True
    if o in ["-r", "--render"]:
        render = True
    if o in ["--no_log"]:
        log = False

if len(args) < 4:
    print("Usage: {} [options] <episodes> <gamma> <alpha> <ee_rate>".format(sys.argv[0]))
    sys.exit(0)

episode, gamma, alpha, ee_rate = int(args[0]), float(args[1]), float(args[2]), float(args[3])

model = FQL.Model(gamma=gamma, alpha=alpha, ee_rate=ee_rate, action_set_length=env.action_space.n,
                  q_initial_value="zeros", fis=fis)

stat = (Stat(episode, label=model))

if load:
    i = Load(model, stat)

stat = Training(model, stat=stat, episodes=episode, start=i, save=save, save_step=save_step, render=render, log=log)

if save:
    Save(model, stat, episode)

if plot:
    Stat.plot_stats([stat], smoothing_window=int(len(stat._episode_lengths)/5))
