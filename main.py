import pygame, sys
from player import Player
import obsticale
from alien import Alien, Extra
import random
from laser import Laser

class Game:
    def __init__(self):
        #Настройка игрока
        player_sprite = Player((screen_width/2,screen_height), screen_width, 5)
        self.player = pygame.sprite.GroupSingle(player_sprite)


        #Очки здоровья
        self.lives = 3
        self.live_surf = pygame.image.load('graphics/Space_Ship5.png').convert_alpha()
        self.live_x_start_pos = screen_width - (self.live_surf.get_size()[0]*2+20)
        self.score = 0
        self.font = pygame.font.Font('font/Pixeled.ttf', 20)

        #Установка препятствия
        self.shape = obsticale.shape
        self.block_size = 6
        self.blocks = pygame.sprite.Group()
        self.obsticle_amount = 4
        self.obsticle_x_position = [num *(screen_width/self.obsticle_amount) for num in range(self.obsticle_amount)]
        self.create_multiple_obstacles(*self.obsticle_x_position, x_start = screen_width / 15, y_start=480)
        
        #Настройка Пришельцев
        self.aliens = pygame.sprite.Group()
        self.alien_setup(rows=6,cols=8)
        self.alien_direction = 1
        self.alien_lasers = pygame.sprite.Group()

        #Настройка летающей тарелки
        self.extra = pygame.sprite.GroupSingle()
        self.extra_spawn_timer = random.randint(40,80)


        #Музыка для игры
        music = pygame.mixer.Sound('sounds/music.wav')
        music.set_volume(0.2)
        music.play(loops=-1)
        #Звуки для выстрелов
        self.laser = pygame.mixer.Sound('sounds/laser.wav')
        self.laser.set_volume(0.3)
        self.explosion=pygame.mixer.Sound('sounds/explosion.wav')
        self.explosion.set_volume(0.5)


    def create_obstacle(self, x_start, y_start, offset_x):
        for row_index,row in enumerate(self.shape):
            for column_index, col in enumerate(row):
                if col == 'x':
                    x = x_start + column_index * self.block_size + offset_x
                    y = y_start + row_index * self.block_size
                    block = obsticale.Block(self.block_size,(241,79,80),x,y)
                    self.blocks.add(block)
    
    def create_multiple_obstacles(self,*offset,x_start, y_start,):
        for offset_x in offset:
            self.create_obstacle(x_start, y_start, offset_x)

    def alien_position_cheker(self):
        all_aliens = self.aliens.sprites()
        for alien in all_aliens:
            if alien.rect.right >= screen_width:
                self.alien_direction = -1
                self.alien_move_down(1)
            elif alien.rect.left <= 0:
                self.alien_direction = 1
                self.alien_move_down(1)
                
    def alien_setup(self, rows, cols, x_distance = 60, y_distance = 48, x_offset = 70,y_offset = 100):
        for row_index, row in enumerate(range(rows)):
            for col_index, col in enumerate(range(cols)):
                x = col_index * x_distance + x_offset
                y = row_index * y_distance + y_offset
                if row_index == 0:
                    alien_sprite=Alien('yellow',x,y)
                elif 1 <= row_index <=2: 
                    alien_sprite = Alien('green',x,y)
                else:
                    alien_sprite = Alien('red',x,y)
                self.aliens.add(alien_sprite)

    def alien_move_down(self, distance):
        if self.aliens:
            for alien in self.aliens.sprites():
                alien.rect.y += distance

    def alien_shoot(self):
        if self.aliens.sprites():
            random_alien = random.choice(self.aliens.sprites())
            laser_sprite = Laser(random_alien.rect.center, 6, screen_height)
            self.alien_lasers.add(laser_sprite)
            self.laser.play()

    def extra_alien_timer(self):
        self.extra_spawn_timer -= 1
        if self.extra_spawn_timer <=0:
            self.extra.add(Extra(random.choice(['right', 'left']), screen_width))
            self.extra_spawn_timer = random.randint(400, 800)

    def collisions_checks(self):
        #Для начала коллизия на выстрелы моего корабля!
        if self.player.sprite.lasers:
            for laser in self.player.sprite.lasers:
                #Ну и сами столкновения с препятствиями
                if pygame.sprite.spritecollide(laser, self.blocks, True):
                    laser.kill()
                    

                aliens_hit = pygame.sprite.spritecollide(laser, self.aliens, True)
                if aliens_hit:
                    for alien in aliens_hit:
                        self.score += alien.value
                    laser.kill()
                    self.explosion.play()
                            #Коллизия для летающей тарелки
                if pygame.sprite.spritecollide(laser, self.extra, True):
                    self.score += 500
                    laser.kill()
                

        #Коллизия выстрелов пришельцев
        if self.alien_lasers:
            for laser in self.alien_lasers:
            
                if pygame.sprite.spritecollide(laser,self.blocks, True):
                    laser.kill()
                    
                if pygame.sprite.spritecollide(laser, self.player, False):
                    laser.kill()
                    self.lives -= 1
                    if self.lives <= 0:
                        pygame.quit()
                        sys.exit()

        #Коллизия ПРИШЕЛЬЦЕВ
        if self.aliens:
            for alien in self.aliens:
                pygame.sprite.spritecollide(alien, self.blocks, True)
                if pygame.sprite.spritecollide(alien, self.player, True):
                    pygame.quit()
                    sys.exit()
   
    def display_lives(self):
        for live in range(self.lives - 1):
            x = self.live_x_start_pos + (live * (self.live_surf.get_size()[0]+10))
            screen.blit(self.live_surf,(x,8))
                
    def display_score(self):
        score_surf = self.font.render(f'Score: {self.score}', False, 'white')
        score_rect = score_surf.get_rect(topleft=(10,-10))
        screen.blit(score_surf, score_rect)

    def victory_message(self):
        if not self.aliens.sprites():
            victory = self.font.render('You WON!', False, 'white')
            victory_rect = victory.get_rect(center=(screen_width/2, screen_height/2))
            screen.blit(victory,victory_rect)

    def run(self):
        self.player.sprite.lasers.draw(screen)
        self.aliens.update(self.alien_direction)
        self.alien_position_cheker()
        self.alien_lasers.update()
        self.extra_alien_timer()
        self.extra.update()
        self.collisions_checks()
        self.display_lives()
        self.victory_message()


        self.player.draw(screen)
        self.player.update()
        self.blocks.draw(screen)
        self.aliens.draw(screen)
        self.alien_lasers.draw(screen)
        self.extra.draw(screen)
        self.display_score()

  


class CRT:
    def __init__(self):
        self.tv = pygame.image.load('graphics/tv.png').convert_alpha()
        self.tv = pygame.transform.scale(self.tv, (screen_width,screen_height))

    def create_crt_lines(self):
        line_height = 3
        line_amount = int(screen_height/line_height)
        for line in range(line_amount):
            y_pos = line * line_height
            pygame.draw.line(self.tv, 'black', (0,y_pos), (screen_width, y_pos), 1)

    def draw(self):
        self.tv.set_alpha(random.randint(75, 90))
        self.create_crt_lines()
        screen.blit(self.tv,(0,0))
    

        


if __name__ == '__main__':
    pygame.init()
    screen_width = 600
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    game = Game()
    crt = CRT()


    ALIENLASER = pygame.USEREVENT + 1
    pygame.time.set_timer(ALIENLASER,800)
    background_image = pygame.image.load('graphics/bckg.png')
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == ALIENLASER:
                game.alien_shoot()
        screen.blit(background_image, (0,0))
        pygame.display.update()
        game.run()
        crt.draw()

        pygame.display.flip()
        clock.tick(60)