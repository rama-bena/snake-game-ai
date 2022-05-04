from math import gamma
import torch
import random
import numpy as np
from collections import deque

from librarybantuan.direction import Direction, Turn
from librarybantuan.plot import plot
from game import SnakeGameAI, Point
from model import Linear_QNet, QTrainer

class Agent:
    def __init__(self, max_memory=100_000, batch_size=1000, epsilon=50, learning_rate=0.001, gamma=0.9):
        self.BATCH_SIZE = batch_size
        self.EPSILON    = epsilon # randomness exploration -> berapa persen awalnya tingkat random gerakan
        self.n_games    = 0
        self.memory     = deque(maxlen=max_memory)
        self.model      = Linear_QNet(input_size=11, hidden_size=256, output_size=3)
        self.trainer    = QTrainer(self.model, learning_rate, gamma)
    
    #* ----------------------------- Public Method ---------------------------- #
    def get_state(self, game:SnakeGameAI): #? ubah menjadi fungsi?
        head = game.head
        direction = game.direction

        point_l = Point(head.x-game.BLOCK_SIZE, head.y)
        point_r = Point(head.x+game.BLOCK_SIZE, head.y)
        point_u = Point(head.x, head.y-game.BLOCK_SIZE)
        point_d = Point(head.x, head.y+game.BLOCK_SIZE)

        dir_l = direction==Direction.LEFT
        dir_r = direction==Direction.RIGHT
        dir_u = direction==Direction.UP
        dir_d = direction==Direction.DOWN


        state = [
            # Danger straight
            (dir_l and game.is_collision(point_l)) or 
            (dir_r and game.is_collision(point_r)) or 
            (dir_u and game.is_collision(point_u)) or 
            (dir_d and game.is_collision(point_d)), 

            # Danger Right
            (dir_l and game.is_collision(point_u)) or 
            (dir_r and game.is_collision(point_d)) or 
            (dir_u and game.is_collision(point_r)) or 
            (dir_d and game.is_collision(point_l)),

            # Danger Left
            (dir_l and game.is_collision(point_d)) or 
            (dir_r and game.is_collision(point_u)) or 
            (dir_u and game.is_collision(point_l)) or 
            (dir_d and game.is_collision(point_r)),

            # Move Direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,

            # Food location
            game.food.x < head.x, # food di kiri
            game.food.x > head.x, # food di kanan
            game.food.y < head.y, # food di atas
            game.food.y > head.y  # food di bawah
        ]

        return np.array(state, dtype=int)

    def get_action(self, state):
        # Random moves: tradeoff exploration / exploitation
        new_epsilon =  self.EPSILON - self.n_games # epsilon semakin lama semakin kecil -> semakin sedikit random gerakan
        # OHE dari move = [straight, turn_right, turn_left]
        final_move = [0, 0, 0]

        # 100 artinya persen, jika pilih exploration. Ketika epsilon 0 atau minus, maka tidak akan ada random lagi
        if random.randint(1, 100) <= new_epsilon: 
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            # Jadikan bentuk tensor dulu statenya
            state0 = torch.tensor(state, dtype=torch.float)
            # Lakukan prediksi gerakan, hasil masih berupa one hot encoding
            prediction = self.model(state0)
            # Ubah OHE ke bentuk index
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move

    def remember(self, state, action, reward, next_state, game_over):
        self.memory.append((state, action, reward, next_state, game_over)) # otomatis pop left jika len memory > max_memory
    
    def train_short_memory(self, state, action, reward, next_state, game_over):
        self.trainer.train_step(state, action, reward, next_state, game_over)
        
    def train_long_memory(self):
        # Ambil sampel dari memory sebanyak batch_size atau seluruh memory jika memory lebih kecil dari batch_size
        mini_size = min(len(self.memory), self.BATCH_SIZE)
        mini_sample = random.sample(self.memory, mini_size)
        
        # Ekstrak setiap paramater lalu train
        states, actions, rewards, next_states, game_overs = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, game_overs)

    #* ---------------------------- Private Method ---------------------------- #

#* ------------------------------- Main Function ------------------------------ #
def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    best_score = 0
    game = SnakeGameAI(speed=50)
    agent = Agent()

    while True:
        # dapatkan state sekarang
        state_old = agent.get_state(game)

        # cari gerakan sesuai dengan state sekarang
        final_move = agent.get_action(state_old)

        # lakukan gerakannya dan dapatkan state hasil gerakan
        reward, game_over, score = game.play_step(final_move)
        state_new = agent.get_state(game)

        # hasil 1 iterasi taruh di memory
        agent.remember(state_old, final_move, reward, state_new, game_over)
        
        # latih menggunakan 1 data yang terakhir
        agent.train_short_memory(state_old, final_move, reward, state_new, game_over)

        if game_over:
            game.reset()
            agent.n_games += 1
            agent.train_long_memory() # latih menggunakan data-data di memori

            if score > best_score:
                best_score = score
                agent.model.save()

            print(f"Game: {agent.n_games}, Score:{score}, Best score:{best_score}")

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)

            # plot(plot_scores, plot_mean_scores)
            

if __name__ == '__main__':
    train()