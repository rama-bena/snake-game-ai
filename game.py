import pygame
import random
from librarybantuan.direction import Direction, Turn
from librarybantuan.color import Color
from collections import namedtuple
Point = namedtuple('Point', ['x', 'y'])

class SnakeGameAI:
    def __init__(self, width=640, height=420, block_size=20, speed=20):
        #* Init Konstanta
        self.WIDTH         = width
        self.HEIGHT        = height
        self.BLOCK_SIZE    = block_size
        self.SPEED         = speed
        self.POINT_BORDER  = self.BLOCK_SIZE // 5
        self.SIZE_BORDER   = self.BLOCK_SIZE*3//5
        self.MAX_ITERATION = (self.WIDTH//self.BLOCK_SIZE) * (self.HEIGHT//self.BLOCK_SIZE) # sesuai dengan banyaknya block yang ada

        #* Init pygame
        pygame.init()
        self.font = pygame.font.SysFont('arial', 25)
        self.display = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption('Snake Game by Rama Bena')
        self.clock = pygame.time.Clock()
        
        #* Init game state
        self.reset()
        
    #* ----------------------------- Public Method ----------------------------- #
    def reset(self):
        """ Untuk me-reset semua variabel game ke awal
            Dipakai ketika pertama kali main atau tiap mati mau ulang game
        """        
        
        #* Init snake state
        self.direction = Direction.RIGHT
        self.head = Point(((self.WIDTH//2)//self.BLOCK_SIZE)*self.BLOCK_SIZE, 
                            ((self.HEIGHT//2)//self.BLOCK_SIZE)*self.BLOCK_SIZE)
        self.snake = [self.head,                                            # Isi snake awal yaitu kepala
                      Point(self.head.x-self.BLOCK_SIZE, self.head.y),      # badan pertama di kiri kepala
                      Point(self.head.x-(2*self.BLOCK_SIZE), self.head.y)]  # badan kedua 2 kali di kiri kepala 
        
        #* Init score dan food
        self.score = 0         
        self.food = None
        self._place_food()
        self.frame_iteration = 0

        #* Terakhir update UI
        self._update_ui()

    def play_step(self, action):
        """`Description`:
            Fungsi utama untuk menjalankan ular sesuai dengan action
        `Args`:
            action ([straight, turn_right, turn_left]): Arah gerakan
        `Returns`:
            (reward, game_over, caution_death, self.score): bentuk tuple dengan 4 element 
        """        
        
        #* Init variabel
        reward        = 0
        game_over     = False
        caution_death = 'not die'
        distance_before_move = self._distance(self.head, self.food)
        self.frame_iteration += 1

        #* Cek pencet keluar
        self._quit_listener()

        #* Gerak
        self._move(action)
        self.snake.insert(0, self.head)
        distance_after_move = self._distance(self.head, self.food)
        # reward = 0.1 if distance_after_move<distance_before_move else -0.15

        #* Cek Game Over
        if self.is_collision():
            reward = -10
            game_over = True
            caution_death = 'nabrak diri' if self.head in self.snake[1:] else 'nabrak tembok'
            return reward, game_over, caution_death, self.score

        if self.frame_iteration > self.MAX_ITERATION:
            reward = -10
            game_over = True
            caution_death = 'lama gak makan'
            return reward, game_over, caution_death, self.score

        #* Cek makan food atau tidak
        if self.head == self.food:
            reward = 10
            self.score += 1
            self.frame_iteration = 0
            self._place_food()
        else:
            self.snake.pop()

        #* Update UI dan beri delay 
        self._update_ui()
        self.clock.tick(self.SPEED)

        return reward, game_over, caution_death, self.score

    def is_collision(self, pt=None):
        """`Description`:
            Cek apakah nabrak (tembok/diri)
        `Args`:
            pt (Point, optional): Point apa yang di cek. Defaultnya head.
        `Returns`:
            bool
        """        
        if pt is None:
            pt = self.head

        hits_boundary = (pt.x>self.WIDTH-self.BLOCK_SIZE or pt.x<0) or (pt.y>self.HEIGHT-self.BLOCK_SIZE or pt.y<0)
        hits_itself = pt in self.snake[1:]
        return hits_boundary or hits_itself

    #* ----------------------------- Private Method ---------------------------- #
    def _place_food(self):
        #* Buat daftar koordinat yang tidak isi ular
        empty_space = []
        for i in range(0, self.WIDTH-self.BLOCK_SIZE, self.BLOCK_SIZE):
            for j in range(0, self.HEIGHT-self.BLOCK_SIZE, self.BLOCK_SIZE):
                if Point(i,j) not in self.snake:
                    empty_space.append((i, j))
        #* Pilih random tempat food
        x, y = random.choice(empty_space)
        self.food = Point(x, y)

    def _update_ui(self):
        #* Warnain background dan border display
        self.display.fill(Color.BACKGROUND)
        pygame.draw.rect(self.display, Color.BORDER, pygame.Rect(0, 0, self.WIDTH-(self.WIDTH%self.BLOCK_SIZE), self.HEIGHT-(self.HEIGHT%self.BLOCK_SIZE)), 1)

        #* Gambar kepala
        pygame.draw.rect(self.display, Color.SNAKE_BORDER, pygame.Rect(self.head.x, self.head.y, self.BLOCK_SIZE, self.BLOCK_SIZE))

        #* Gambar badan snake
        for point in self.snake[1:]:
            pygame.draw.rect(self.display, Color.SNAKE_BODY, pygame.Rect(point.x, point.y, self.BLOCK_SIZE, self.BLOCK_SIZE))
            pygame.draw.rect(self.display, Color.SNAKE_BORDER, pygame.Rect(point.x+self.POINT_BORDER, point.y+self.POINT_BORDER, self.SIZE_BORDER, self.SIZE_BORDER))
        
        #* Gambar food
        pygame.draw.rect(self.display, Color.FOOD, pygame.Rect(self.food.x, self.food.y, self.BLOCK_SIZE, self.BLOCK_SIZE))
        
        #* Gambar score
        text = self.font.render(f"Score: {self.score}", True, Color.SCORE)
        self.display.blit(text, (0, 0))
        
        #* Update semua
        pygame.display.flip() 

    def _quit_listener(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

    def _move(self, action): # ? cek tipe data action
        x = self.head.x
        y = self.head.y

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if action == Turn.RIGHT:
            idx = (idx+1) % 4
        elif action == Turn.LEFT:
            idx = (idx-1) % 4
        
        self.direction = clock_wise[idx]

        if self.direction == Direction.LEFT:
            x -= self.BLOCK_SIZE
        elif self.direction == Direction.RIGHT:
            x += self.BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= self.BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += self.BLOCK_SIZE
        
        self.head = Point(x, y)

    def _distance(self, point1, point2):
        # Manhattan Distance 2 point        
        return (abs(point1.x-point2.x) + abs(point1.y-point2.y)) // self.BLOCK_SIZE