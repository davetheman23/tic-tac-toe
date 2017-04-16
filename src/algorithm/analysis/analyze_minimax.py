import random
import time

from src.algorithm.minimax import MinimaxAlgorithm, Game


if __name__ == '__main__':

    class Player:
        def __init__(self, winning_reward):
            self.winning_reward = winning_reward

        def __str__(self):
            return "'({}) Reward Player'".format(self.get_winning_reward())

        def get_winning_reward(self):
            return self.winning_reward

    for num_rows in range(3, 6):
        for num_cols in range(3, 6):
            num_connects_to_win = min(num_rows, num_cols)
            g = Game(num_rows, num_cols, num_connects_to_win, [Player(1), Player(-1)])
            minimax = MinimaxAlgorithm(g)
            print("building best policies according to minimax algorithm")
            start = time.clock()
            best_policy = minimax.get_best_policy()
            with open("best_policies.txt", "w") as f:
                for state, policy in best_policy.iteritems():
                    value, move = policy
                    f.write("state is {}, best move is {}, best value is {}\n".format(state, move, value))
            end = time.clock()
            print("Total time to build minimax best policy is: {} seconds".format(str(end - start)))

            with open("game_results_{}_{}.txt".format(num_rows, num_cols), "w") as f:
                print("Running games of size {} x {} ...".format(num_rows, num_cols))
                f.write("Total time to build minimax best policy is: {} seconds".format(str(end - start)))
                for game_idx in range(10):
                    print("Running game {}".format(game_idx))
                    f.write("\n#########################################\n")
                    f.write("Start playing game {}\n".format(game_idx))
                    g = Game(num_rows, num_cols, num_connects_to_win, [Player(1), Player(-1)])
                    # set a random start location
                    g.make_move(random.randint(0, num_rows * num_cols - 1))
                    f.write(str(g) + "\n")
                    f.write("============\n")
                    while not g.is_game_over():
                        time.sleep(0.1)
                        minimax_move = best_policy[tuple(g.game_state)][1]
                        g.make_move(minimax_move)
                        f.write(str(g) + "\n")
                        f.write("============\n")
                    winner = g.get_winner()
                    if winner == 0:
                        f.write("its a draw\n")
                        print("its a draw")
                    else:
                        f.write("the winner is {}\n".format(winner))
                        print("the winner is {}".format(winner))
