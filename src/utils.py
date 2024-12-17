import numpy as np

class PlayerStats:
    def __init__(self, name: str):
        self.name: str = name
        self.accuracy: int = 0
        self.acpl: int = 0
        self.inaccuracy: int = 0
        self.mistake: int = 0
        self.blunder: int = 0
        self.move_times: list[list[int]] = []
        self.clocks: list[list[int]] = []
        self.disadvantages: int = 0
        self.comebacks: int = 0
        self.advantages: int = 0
        self.wins: int = 0
        self.games: int = 0

    def __repr__(self):
        return (f'Name: {self.name}, \n'
                f'Accuracy: {self.accuracy}, \n'
                f'ACPL: {self.acpl}, \n'
                f'InAccuracy: {self.inaccuracy}, \n'
                f'Mistake: {self.mistake}, \n'
                f'Blunder: {self.blunder}, \n'
                f'Advantages: {self.advantages}, \n'
                f'Disadvantages: {self.disadvantages}, \n'
                f'Comebacks: {self.comebacks}, \n'
                f'Wins: {self.wins}, \n'
                #f'MoveTimes: {self.move_times}, \n'
                f'Games: {self.games} \n')

    def average_move_times_list(self) -> list[int]:
        print(self.move_times)
        max_length = max(len(lst) for lst in self.move_times)
        padded_lists = np.array([lst + [np.nan] * (max_length - len(lst)) for lst in self.move_times])

        sums = np.nansum(padded_lists, axis=0)
        counts = np.sum(~np.isnan(padded_lists), axis=0)
        average_list = sums / counts
        return average_list

    def mean_move_times_list(self) -> list[int]:
        print(self.move_times)
        max_length = max(len(lst) for lst in self.move_times)
        padded_lists = np.array([lst + [np.nan] * (max_length - len(lst)) for lst in self.move_times])

        mean_list = np.nanmean(padded_lists, axis=0)
        return mean_list
