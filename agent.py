import torch
import random
from collections import deque

from librarybantuan.direction import Direction
from game import SnakeGameAI, Point
from model import Linear_QNet, QTrainer

class Agent:
    def __init__(self, max_memory=100_000, batch_size=1000, epsilon=100, learning_rate=0.001, gamma=0.9):
        self.BATCH_SIZE = batch_size
        self.epsilon    = epsilon # randomness exploration -> berapa persen awalnya tingkat random gerakan
        self.n_games    = 0
        self.memory     = deque(maxlen=max_memory) # otomatis pop left jika len memory > max_memory
        self.model      = Linear_QNet(input_size=11, hidden_size=64, output_size=3)
        self.trainer    = QTrainer(self.model, learning_rate, gamma)
        self.model.load()
        
    #* ----------------------------- Public Method ---------------------------- #
    def get_state(self, game:SnakeGameAI): #? ubah menjadi beberapa fungsi?
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

        return list(map(int, state))

    def get_action(self, state):
        # Random moves: tradeoff exploration / exploitation
        new_epsilon = self.epsilon-self.n_games # epsilon semakin lama semakin kecil -> semakin sedikit random gerakan
        # OHE dari move = [straight, turn_right, turn_left]
        final_move = [0, 0, 0]

        # 100 artinya persen, jika pilih exploration. Ketika epsilon 0 atau minus, maka tidak akan ada random lagi
        if random.randint(1, 100) <= new_epsilon: 
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            # Jadikan bentuk tensor dulu statenya
            state = torch.tensor(state, dtype=torch.float)
            # Lakukan prediksi gerakan
            prediction = self.model(state)
            # Ambil gerakan yang nilainya paling tinggi
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move

    def remember(self, state, action, reward, next_state, game_over):
        if (state, action, reward, next_state, game_over) not in self.memory: # hanya masukin data yang tidak ada di memory
            self.memory.append((state, action, reward, next_state, game_over)) 

    def train_short_memory(self, state, action, reward, next_state, game_over):
        self.trainer.train_step(state, action, reward, next_state, game_over)
        
    def train_long_memory(self):
        ## Ambil sampel dari memory sebanyak batch_size atau seluruh memory jika memory lebih kecil dari batch_size
        # mini_size = min(len(self.memory), self.BATCH_SIZE)
        # mini_sample = random.sample(self.memory, mini_size)
        mini_sample = self.memory #? gak pakek batch. Kode diatas pakai batch
        
        # Ekstrak setiap paramater lalu train
        states, actions, rewards, next_states, game_overs = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, game_overs)

    #* ---------------------------- Private Method ---------------------------- #
