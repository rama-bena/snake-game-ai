import numpy as np
import torch
import random
from collections import deque

from librarybantuan.nameValue import Point
from game import SnakeGameAI
from model import Linear_QNet, QTrainer
from captum.attr import IntegratedGradients
import matplotlib.pyplot as plt
import numpy as np
from IPython import display

class Agent:
    def __init__(self, max_memory=5_000, batch_size=500, epsilon=100, learning_rate=0.001, gamma=0.9):
        self.BATCH_SIZE = batch_size
        self.epsilon    = epsilon # randomness exploration -> berapa persen awalnya tingkat random gerakan
        self.memory     = deque(maxlen=max_memory) # otomatis pop left jika len memory > max_memory
        self.n_games    = 0
        self.model      = Linear_QNet(input_size=30, hidden_size1=64, output_size=4)
        self.trainer    = QTrainer(self.model, learning_rate, gamma)
    
    #* ----------------------------- Public Method ---------------------------- #
    def get_state(self, game:SnakeGameAI):
        state_obstacles = self._get_state_obstacles(game, 5) # 9x9
        
        state_food = [
            1 if game.food.y < game.head.y else 0,  # food ada di atas
            1 if game.food.x > game.head.x else 0,  # food ada di kanan
            1 if game.food.y > game.head.y else 0,  # food ada di bawah
            1 if game.food.x < game.head.x else 0   # food ada di kiri
        ]
        
        state_iteration = [game.frame_iteration / game.MAX_ITERATION]
        
        final_state = state_obstacles + state_food + state_iteration
        return final_state

    def get_action(self, state):
        # Random moves: tradeoff exploration / exploitation
        new_epsilon = self.epsilon - (0.5 * self.n_games) # epsilon semakin lama semakin kecil -> semakin sedikit random gerakan
        # OHE dari move = [left, right, up, down]
        final_move = [0, 0, 0, 0]

        # 100 artinya persen, jika pilih exploration. Ketika epsilon 0 atau minus, maka tidak akan ada random lagi
        if random.randint(1, 100) <= new_epsilon: 
            # candidate_move = []
            # if state[31]==1: candidate_move.append(0)
            # if state[41]==1: candidate_move.append(1)
            # if state[49]==1: candidate_move.append(2)
            # if state[39]==1: candidate_move.append(3)
            # move = random.choice(candidate_move) if len(candidate_move)>0 else 0
            move = random.randint(0, 3)
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
        self._plot(states)
        for i in range(0, len(memory), self.BATCH_SIZE):
            batch_states      = states[i:i+self.BATCH_SIZE]
            batch_actions     = actions[i:i+self.BATCH_SIZE]
            batch_rewards     = rewards[i:i+self.BATCH_SIZE]
            batch_next_states = next_states[i:i+self.BATCH_SIZE]
            batch_game_overs  = game_overs[i:i+self.BATCH_SIZE]
            self.trainer.train_step(batch_states, batch_actions, batch_rewards, batch_next_states, batch_game_overs)

    #* ---------------------------- Private Method ---------------------------- #
    def _get_state_obstacles(self, game:SnakeGameAI, visual_range):
        def point_to_index(point:Point, block_size): # Fungsi bantuan mengubah point menjadi index
            return (point.y//block_size, point.x//block_size)

        #* Ambil atribut yang dibutuhkan
        snake = game.snake
        head = snake[0]
        block_size = game.BLOCK_SIZE

        #* Variabel yang dibutuhkan
        state_obstacles = [[1 for _ in range(visual_range)] for __ in range(visual_range)]
        start_point = Point(head.x-(visual_range//2)*block_size, head.y-(visual_range//2)*block_size)
        minus = point_to_index(start_point, block_size)
        
        #* Buat state obstacle, 1:ada obstacle, 0:tidak ada
        for i in range(visual_range):
            for j in range(visual_range):
                point = Point(start_point.x + j*block_size, start_point.y + i*block_size)
                if game.is_collision(point) or point==head:
                    idx = point_to_index(point, block_size)
                    idx = (idx[0]-minus[0], idx[1]-minus[1])
                    state_obstacles[idx[0]][idx[1]] = 0

        #* Buat 1 dimensi
        state_obstacles = list(np.array(state_obstacles).reshape(1, -1)[0])
        return state_obstacles

    def _plot(self, state):
        ig = IntegratedGradients(self.model)
        state = torch.tensor(state, dtype=torch.float)        
        state.requires_grad_()
        feature_names = list(np.arange(25)) + ['up', 'right', 'down', 'left', 'iteration']
        x_pos = (np.arange(len(feature_names)))
       
        display.clear_output(wait=True)
        display.display(plt.gcf())
        plt.clf()
        plt.figure(2)
        plt.title("Average Feature Importances")
        plt.xlabel("Features")
        plt.xticks(x_pos, feature_names, wrap=True, rotation=45)        
        
        for target in range(4):
            attr, delta = ig.attribute(state,target=target, return_convergence_delta=True)
            attr = attr.detach().numpy()
            importances =  np.mean(attr, axis=0)
            plt.bar(x_pos, importances, align='center')
        
        plt.show(block=False)
        plt.pause(.1)