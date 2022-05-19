from game import SnakeGameAI
from agent import Agent
from librarybantuan.plot import plot
import pickle

if __name__ == '__main__':
    #* Variabel
    scores     = [0] # game ke-0 nilainya 0
    best_score = 0
    total_reward = 0
    rewards = [0]

    #* Argumen
    width      = 640
    height     = 480
    speed      = 40      # semakin tinggi semakin cepet, khusus 0 paling cepet
    epsilon    = 100
    max_memory = 100_000

    #* Buat object game dan agent
    agent = Agent(max_memory=max_memory, epsilon=epsilon)
    game = SnakeGameAI(width=width, height=height, speed=speed)
    try:
        while True:
            # dapatkan state sekarang
            state_old = agent.get_state(game)
            # cari gerakan sesuai dengan state sekarang
            action = agent.get_action(state_old)
            # no_ui = agent.n_games < 100
            no_ui = False
            try:
                # lakukan gerakannya
                reward, game_over, caution_death, score = game.play_step(action, no_ui)
                total_reward += reward
            except:
                print('SELESAI BELAJAR')
                break
            
            # dapatkan hasil state terbaru setelah melakukan action
            state_new = agent.get_state(game)
            # hasil 1 iterasi taruh di memory
            agent.remember(state_old, action, reward, state_new, game_over)
            # latih menggunakan 1 data yang terakhir
            agent.train_short_memory(state_old, action, reward, state_new, game_over)

            if game_over:
                rewards.append(total_reward)
                scores.append(score)
                plot(scores, rewards)
                game.reset()
                agent.n_games += 1
                if score > best_score:
                    best_score = score
                    agent.model.save()
                print(f"Game: {agent.n_games}")
                # print(f"Epsilon: {agent.epsilon - 1*agent.n_games}%")
                print(f"Score: {score}, Best score: {best_score}")
                print(f"Reward: {total_reward}")
                print(f"Caution Death:{caution_death}")
                print()
                total_reward = 0


                agent.train_long_memory() # latih menggunakan data-data di memori
    except:
        print('selesai')
    finally:
        print('finally')
        with open('./model/memory.mem', "wb") as f:
            pickle.dump(agent.memory, f)
        plot(scores, rewards, iterative=False)
            
