import os
import numpy as np
import torch
import random
from collections import deque
import pickle

from librarybantuan.direction import Direction
from game import SnakeGameAI, Point
from model import Linear_QNet, QTrainer
import numpy as np

class Agent:
    def __init__(self, visual_range=9, max_memory=100_000, batch_size=1000, epsilon_rate=1., learning_rate=0.001, gamma=0.9):
        self.VISUAL_RANGE = visual_range
        self.BATCH_SIZE   = batch_size
        self.epsilon_rate = epsilon_rate # randomness exploration -> berapa persen awalnya tingkat random gerakan
        self.n_games      = 0
        self.memory       = deque(maxlen=max_memory) # otomatis pop left jika len memory > max_memory
        self.model        = Linear_QNet(input_size=self.VISUAL_RANGE**2+5, hidden_size=128, output_size=3)
        self.trainer      = QTrainer(self.model, learning_rate, gamma)

        self.model.load()
        try:
            with open('./model/memory.mem', 'rb') as f :
                self.memory = pickle.load(f)
        except:
            pass

    #* ----------------------------- Public Method ---------------------------- #
    def get_state(self, game:SnakeGameAI):
        state_obstacles = self._get_state_obstacles(game, self.VISUAL_RANGE)
        state_food = self._get_state_food(game.head, game.food, game.direction)
        state_iteration = [game.frame_iteration / game.MAX_ITERATION]
        final_state = state_obstacles + state_food + state_iteration
        return final_state

    def get_action(self, state):
        # Random moves: tradeoff exploration / exploitation
        epsilon = 100 - (self.epsilon_rate*self.n_games) # epsilon semakin lama semakin kecil -> semakin sedikit gerakan random
        # OHE dari move = [straight, turn_right, turn_left]
        final_move = [0, 0, 0]

        # 100 artinya persen, jika pilih exploration. Ketika epsilon 0 atau minus, maka tidak akan ada random lagi
        if random.randint(1, 100) <= epsilon: 
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
        memory = list(self.memory)
        states, actions, rewards, next_states, game_overs = zip(*memory)
        self.BATCH_SIZE = len(memory)
        for i in range(0, len(memory), self.BATCH_SIZE):
            batch_states      = states[i:i+self.BATCH_SIZE]
            batch_actions     = actions[i:i+self.BATCH_SIZE]
            batch_rewards     = rewards[i:i+self.BATCH_SIZE]
            batch_next_states = next_states[i:i+self.BATCH_SIZE]
            batch_game_overs  = game_overs[i:i+self.BATCH_SIZE]
            self.trainer.train_step(batch_states, batch_actions, batch_rewards, batch_next_states, batch_game_overs)

    #* ---------------------------- Private Method ---------------------------- #
    def _get_state_food(self, head, food, direction):
        initial_state = [
            1 if food.y < head.y else 0,  # food ada di atas
            1 if food.x > head.x else 0,  # food ada di kanan
            1 if food.y > head.y else 0,  # food ada di bawah
            1 if food.x < head.x else 0  # food ada di kiri
        ]

        if direction == Direction.UP:
            how_many_turn_right = 0
        elif direction == Direction.RIGHT:
            how_many_turn_right = 1
        elif direction == Direction.DOWN:
            how_many_turn_right = 2
        else:
            how_many_turn_right = 3

        state_food = [initial_state[(i+how_many_turn_right)%4] for i in range(4)]
        return state_food
   
    def _get_state_obstacles(self, game:SnakeGameAI, visual_range):
        def point_to_index(point:Point, block_size): # Fungsi bantuan mengubah point menjadi index
            return (point.y//block_size, point.x//block_size)
        def rotate_state(state, direction):
            if direction == Direction.UP:
                return state
            elif direction == Direction.LEFT:
                return list(zip(*state[::-1])) # putar clockwise
            elif direction == Direction.RIGHT:
                return list(zip(*state))[::-1] # putar counter clockwise
            else:
                return list(zip(*list(zip(*state[::-1]))[::-1])) # putar 2 kali

        #* Ambil atribut yang dibutuhkan
        snake = game.snake
        head = snake[0]
        direction = game.direction
        block_size = game.BLOCK_SIZE

        #* Buat state obstacle, 1:ada obstacle, 0:tidak ada
        state_obstacles = [[0 for _ in range(visual_range)] for __ in range(visual_range)]
        titik_awal = Point(head.x-(visual_range//2)*block_size, head.y-(visual_range//2)*block_size)
        kurang = point_to_index(titik_awal, block_size)
        for i in range(visual_range):
            for j in range(visual_range):
                point = Point(titik_awal.x + j*block_size, titik_awal.y + i*block_size)
                if game.is_collision(point) or point==head:
                    idx = point_to_index(point, block_size)
                    idx = (idx[0]-kurang[0], idx[1]-kurang[1])
                    state_obstacles[idx[0]][idx[1]] = 1

        #* Putar state selalu liat atas
        state_obstacles = rotate_state(state_obstacles, direction)
        #* Buat 1 dimensi
        state_obstacles = list(np.array(state_obstacles).reshape(1, -1)[0])
        return state_obstacles

    