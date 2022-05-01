import pygame
import random
from direction import Direction
from color import Color
from collections import namedtuple

Point = namedtuple('Point', 'x, y')

#* --------------------------------- Konstanta -------------------------------- #
BLOCK_SIZE = 20
SPEED = 40
#* ---------------------------- Inisialisasi pygame --------------------------- #
pygame.init()
font = pygame.font.SysFont('arial', 25)

class SnakeGame:
    def __init__(self, width=640, height=480):
        self.width = width
        self.height = height
        
        #* init display
        self.display = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Snake Game by Rama Bena')
        self.clock = pygame.time.Clock()

        #* init snake state
        self.direction = Direction.RIGHT
        self.head = Point(self.width//2, self.height//2)
        self.snake = [self.head,    # Isi snake awal, kepala
                      Point(self.head.x-BLOCK_SIZE, self.head.y),   # badan di kiri kepala
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]   # badan kedua 2 kali dikiri kepala 

        #* init another variable
        self.score =0         
        self.food = None
        self._place_food()


    def play_step(self):
        # 1. collect user input
   
        # 2. move

        # 3. check if game over
        game_over = False
        # 4. place new food or just move

        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)

        # 6. return game over and score
        return game_over, self.score


    def _place_food(self):
        # buat daftar koordinat yang tidak isi ular
        empty_space = []
        for i in range(0, self.width, BLOCK_SIZE):
            for j in range(0, self.height, BLOCK_SIZE):
                if Point(i,j) not in self.snake:
                    empty_space.append((i, j))
        # pilih random tempat food
        x, y = random.choice(empty_space)
        self.food = Point(x, y)

    def _update_ui(self):
        self.display.fill(Color.BACKGROUND)

        #* gambar snake
        coor_border = BLOCK_SIZE // 5
        size_border = BLOCK_SIZE*3//5
        for point in self.snake:
            pygame.draw.rect(self.display, Color.SNAKE_BODY, pygame.Rect(point.x, point.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, Color.SNAKE_BORDER, pygame.Rect(point.x+coor_border, point.y+coor_border, size_border, size_border))
        
        #* gambar food
        pygame.draw.rect(self.display, Color.FOOD, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
        
        #* gambar score
        text = font.render(f"Score: {self.score}", True, Color.SCORE)
        self.display.blit(text, (0, 0))
        
        #* update
        pygame.display.flip() 


if __name__ == '__main__':
    game = SnakeGame()

    while True:
        game_over, score = game.play_step()


        if game_over:
            break

    print(f"Final Score {score}")
    pygame.quit()



