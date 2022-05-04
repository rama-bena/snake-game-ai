import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os

class Linear_QNet(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = self.linear1(x)
        x = F.relu(x)
        x = self.linear2(x)
        return x
    
    def save(self, file_name="mymodel.model"):
        folder_path = './model/'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        file_path = os.path.join(folder_path+file_name)
        torch.save(self.state_dict(), file_path)


class QTrainer:
    def __init__(self, model:Linear_QNet, learning_rate, gamma):
        self.model = model
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.optimizer = optim.Adam(model.parameters(), lr=learning_rate)
        self.criterion = nn.MSELoss()
    
    def train_step(self, state, action, reward, next_state, game_over):
        # jadikan bentuk tensor
        state = torch.tensor(state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)

        if len(state.shape) == 1: # jika 1 dimensi
            # ubah jadi bentuk (1, x)
            state = torch.unsqueeze(state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            next_state = torch.unsqueeze(next_state, 0)
            game_over = (game_over, )

        # 1: Prediksi Q values dengan state sekarang
        prediction = self.model(state) 
        # sementara copy dulu dari prediction
        target = prediction.clone()

        size = len(state)
        for idx in range(size):
            Q_new = reward[idx]
            if not game_over[idx]:
                # 2: Q_new = r + y*max(prediksi berikutnya Q value)
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))

            action_idx = torch.argmax(action[idx]).item() 
            target[idx][action_idx] = Q_new 

        # kosongkan dulu gradian sebelumnya
        self.optimizer.zero_grad()
        # cari nilai loss
        loss = self.criterion(target, prediction)
        # lakukan back propagation
        loss.backward()
        self.optimizer.step()
