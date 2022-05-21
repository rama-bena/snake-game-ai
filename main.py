from game import SnakeGameAI
from agent import Agent
import pickle
import time

from librarybantuan.plot import plot
from librarybantuan.nameValue import Path

def format_time(seconds):
    second = seconds % 60
    minute = seconds // 60
    hour = int(minute // 60)
    minute = int(minute % 60)

    return f"{hour}h {minute}m {round(second,2)}s"


if __name__ == '__main__':
    #* Variabel
    scores     = [0] # game ke-0 nilainya 0
    best_score = (0, 0) # nilai best score, game menghasilkan best score
    total_reward = 0

    #* Argumen
    speed        = 0      # semakin tinggi semakin cepet, khusus 0 paling cepet
    epsilon_rate = 1      # pengurangan gerakan random, lebih atau sama dengan 100 -> tanpa random
    max_memory   = 1000
    visual_range = 9
    title = f"vr={visual_range}, eps={epsilon_rate if epsilon_rate<100 else 'no_eps'}"

    #* Buat object game dan agent
    agent = Agent(visual_range=visual_range, max_memory=max_memory, epsilon_rate=epsilon_rate)
    game = SnakeGameAI(speed=speed)
    try:
        start = time.time()
        while True:
            # dapatkan state sekarang
            state_old = agent.get_state(game)
            # cari gerakan sesuai dengan state sekarang
            action = agent.get_action(state_old)
            with_ui = agent.n_games > 100
            with_ui = True
            try:
                # lakukan gerakannya
                reward, game_over, caution_death, score = game.play_step(action, with_ui)
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
                scores.append(score)
                plot(scores, title=title)
                game.reset()
                agent.n_games += 1
                if score > best_score[0]:
                    best_score = (score, agent.n_games)
                    agent.model.save()
                print(f"Game: {agent.n_games}")
                print(f"Time: {format_time(time.time()-start)}")
                print(f"Randomness: {max(100 - agent.epsilon_rate*agent.n_games, 0)}%")
                print(f"Score: {score}, Best score: {best_score[0]}, {best_score[1]}")
                print(f"Reward: {total_reward}")
                print(f"Caution Death:{caution_death}")
                print()
                total_reward = 0
                if agent.n_games == 500:
                    break
                agent.train_long_memory() # latih menggunakan data-data di memori
    except:
        print('keluar paksa')
    finally:
        print('finally')
        with open(Path.MEMORY, "wb") as f:
            pickle.dump(agent.memory, f)
        plot(scores, title=title, interative=False)
            
