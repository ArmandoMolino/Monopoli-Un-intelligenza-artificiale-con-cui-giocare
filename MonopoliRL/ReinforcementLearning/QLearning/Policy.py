import random

import numpy as np


def epsilon_greedy(ee_rate, M, q_table):
    r = random.uniform(0, 1)

    if r > ee_rate:
        for rull in q_table:
            # Seglie un'azione ottimale rispetto al q-table
            action_index = np.argmax(rull)
            M.append(action_index)
    else:
        for rull in q_table:
            # Seglie un'azione casuale
            action_index = random.randint(0, q_table.shape[1] - 1)
            M.append(action_index)
