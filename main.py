from game import SnakeGameAI
from agent import Agent
from librarybantuan.plot import plot


def main():
    #* Variabel
    scores     = [0] # game ke-0 nilainya 0
    best_score = 0

    #* Argumen
    width      = 640
    height     = 480
    speed      = 0      # semakin tinggi semakin cepet, khusus 0 paling cepet
    epsilon    = 100
    max_memory = 100_000

    #* Buat object game dan agent
    agent = Agent(max_memory=max_memory, epsilon=epsilon)
    game = SnakeGameAI(width=width, height=height, speed=speed)
    
    while True:
        # dapatkan state sekarang
        state_old = agent.get_state(game)
        # cari gerakan sesuai dengan state sekarang
        action = agent.get_action(state_old)
        try:
            # lakukan gerakannya
            reward, game_over, caution_death, score = game.play_step(action)
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
            game.reset()
            agent.n_games += 1
            agent.train_long_memory() # latih menggunakan data-data di memori

            if score > best_score:
                best_score = score
                agent.model.save()

            print(f"Game: {agent.n_games}, Score:{score}, Best score:{best_score}, Caution Death:{caution_death}")

            scores.append(score)
            plot(scores, degree=3)

    plot(scores, iterative=False)
            

if __name__ == '__main__':
    main()