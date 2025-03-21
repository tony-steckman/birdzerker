""" My first game written from scratch, about the advetnures of a flying bird! """

import arcade
import os
from random import randint, choice
import sys

SCREEN_TITLE = 'Birdzerker!'
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class StartGameView(arcade.View):

    def init(self):
        super().__init__()
    
    def on_show_view(self):
        self.window.background_color = arcade.csscolor.LIGHT_SKY_BLUE
        self.window.default_camera.use()
        sprite_image = resource_path("resources/images/frame-2.png")
        self.bird = arcade.Sprite(
            sprite_image, scale = 0.1
        )
        self.bird.center_x, self.bird.center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        self.sprites_list = arcade.SpriteList()
        self.sprites_list.append(self.bird)

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """ If the user presses the mouse button, re-start the game. """
        game_view = GameView()
        game_view.setup()
        self.window.show_view(game_view)

    def on_draw(self):
        """ Draw this view """
        self.clear()
        self.sprites_list.draw()
        arcade.draw_text("Click anywhere on the screen to start flying", self.window.width / 2, self.window.height / 2-75,
                         arcade.color.WHITE, font_size=20, anchor_x="center")

class Player(arcade.Sprite):

    def __init__(self, textures, scale):
        super().__init__(textures[0], scale=scale)
        self.current_frame = 0
        self.last_frame = len(textures)
        self.textures = textures
    
    def update(self, delta_time: float = 1/60):
        self.center_x += self.change_x
        self.center_y += self.change_y
        if self.current_frame < self.last_frame - 1:
            self.current_frame += 1
        else:
            self.current_frame = 0
        self.texture = self.textures[self.current_frame]

class Enemy(arcade.Sprite):

    def __init__(self, textures, dead_textures, scale):
        super().__init__(textures[0], scale=scale)
        self.current_frame = 0
        self.last_frame = len(textures)
        self.textures = textures
        self.dead_textures = dead_textures
        self.hit = False
        self.dead = False
        self.died_sound = arcade.Sound(
            resource_path('resources/sounds/enemy_died.flac'),
            streaming = True
        )
        self.player_hit_sound = arcade.Sound(
            resource_path('resources/sounds/player_hit.wav'),
            streaming = True
        )
        self.played_died_sound = False
        self.played_player_hit_sound = False
        self.last_y_direction = 0
    
    def update(self, delta_time: float = 1/60):
        self.center_x += self.change_x
        self.center_y += self.change_y
        if self.current_frame < self.last_frame - 1:
            self.current_frame += 1
        else:
            self.current_frame = 0
        if not self.dead:
            self.texture = self.textures[self.current_frame]
        else:
            self.texture = self.dead_textures[self.current_frame]

    def play_died_sound(self):
        if not self.played_died_sound:
            arcade.play_sound(self.died_sound)
            self.played_died_sound = True

    def play_player_hit_sound(self):
        if not self.played_player_hit_sound:
            arcade.play_sound(self.player_hit_sound)
            self.played_player_hit_sound = True

        
class GameView(arcade.View):

    def __init__(self):
        super().__init__()
        self.score = 0
        self.player = None
        self.player_health = 10
        self.player_max_health = 15
        self.sprite_frame = 0
        self.sprite_frames = ['frame-1.png',
                              'frame-2.png',
                              'frame-3.png',
                              'frame-4.png',
                              'frame-5.png',
                              'frame-6.png',
                              'frame-7.png',
                              'frame-8.png'
                              ]
        self.enemy_frames = ['enemy/frame-1.png',
                             'enemy/frame-2.png']
        self.dead_enemy_frames = ['enemy/dead/frame-1.png',
                                  'enemy/dead/frame-2.png']
        self.clouds = []
        cloud_count = 1
        while cloud_count < 49:
            cloud_count_str = f'{cloud_count}'
            if cloud_count < 10:
                cloud_count_str = f'0{cloud_count}'
            self.clouds.append(f'resources/images/clouds/cloud_{cloud_count_str}.png')
            cloud_count += 1
        self.window.set_mouse_visible(False)
        self.window.set_background_color = arcade.csscolor.LIGHT_SKY_BLUE
        self.chimed = False
        self.enemy_countdown = 20
        self.enemy_bird_speed = 0.5
        self.game_over = False
        self.cloud_countdown = 30
        self.cloud_speed = 0.1
        self.orb_countdown = 50
        self.orb_speed = 0.7
        self.spikes_countdown = 40
        self.spikes_speed = 0.2
        self.health_pickup_sound = arcade.Sound(
            resource_path('resources/sounds/health_pickup.wav'),
            streaming = True
        )
        self.game_over_sound = arcade.Sound(
            resource_path('resources/sounds/game_over.mp3'),
            streaming = True
        )
        self.player_speed = 1

    def setup(self):
        self.spikes_list = arcade.SpriteList()
        self.spikes_hit = {}
        self.clouds_list = arcade.SpriteList()
        self.orbs_list = arcade.SpriteList()
        self.enemies_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.player_textures = []
        for frame in self.sprite_frames:
            texture = arcade.load_texture(resource_path(
                f'resources/images/{frame}'
                )
            )
            self.player_textures.append(texture)
        self.player = Player(
            self.player_textures, scale = 0.1
        )
        self.player.center_x, self.player.center_y = 100, SCREEN_HEIGHT // 2
        self.player_list.append(self.player)
        self.enemy_textures = []
        for frame in self.enemy_frames:
            texture = arcade.load_texture(resource_path(
                f'resources/images/{frame}'
                )
            )
            self.enemy_textures.append(texture)
        self.dead_enemy_textures = []
        for frame in self.dead_enemy_frames:
            texture = arcade.load_texture(resource_path(
                f'resources/images/{frame}'
                )
            )
            self.dead_enemy_textures.append(texture)
        self.add_cloud(0)
        self.add_cloud(0.5)
        self.add_cloud(1)
        self.add_enemy(0)
        self.player_hit_sound = arcade.Sound(
            resource_path('resources/sounds/player_hit.wav'),
            streaming = True
        )
        arcade.schedule(
            function_pointer=self.add_enemy, interval=self.enemy_countdown
        )
        arcade.schedule(
            function_pointer=self.add_cloud, interval=self.cloud_countdown
        )
        arcade.schedule(
            function_pointer=self.add_orb, interval=self.orb_countdown
        )
        arcade.schedule(
            function_pointer=self.add_spikes, interval=self.spikes_countdown
        )

    def add_cloud(self, dt:float):
        if not self.game_over:
            new_cloud_image = self.clouds[randint(0, 47)]
            new_cloud = arcade.Sprite(
                resource_path(new_cloud_image),
                scale = 6
            )
            if len(self.clouds_list) < 3:
                new_cloud.center_x = randint(30, SCREEN_WIDTH - 30)
            else:
                new_cloud.center_x = SCREEN_WIDTH + 50
            new_cloud.center_y = randint(20, SCREEN_HEIGHT - 20)
            self.clouds_list.append(new_cloud)

    def add_enemy(self, dt:float):
        if not self.game_over:
            new_enemy = Enemy(
                self.enemy_textures, self.dead_enemy_textures, scale = 0.1
            )
            new_enemy.center_x = SCREEN_WIDTH
            new_enemy.center_y = randint(30, SCREEN_HEIGHT - 30)
            self.enemies_list.append(new_enemy)
            self.enemy_countdown -= 2
            if self.enemy_countdown < 2:
                self.enemy_countdown = 2
            if self.enemy_bird_speed < 2:
                self.enemy_bird_speed += 0.1
            arcade.unschedule(function_pointer=self.add_enemy)
            arcade.schedule(
                function_pointer=self.add_enemy, interval=self.enemy_countdown
            )

    def add_orb(self, dt:float):
        if not self.game_over:
            new_orb = arcade.Sprite(
                resource_path('resources/images/orbs/golden_orb.png'),
                scale = 0.03
            )
            new_orb.center_x = SCREEN_WIDTH
            new_orb.center_y = randint(30, SCREEN_HEIGHT - 30)
            self.orbs_list.append(new_orb)
            self.orb_countdown += 5
            self.orb_speed += 0.5
            arcade.unschedule(function_pointer=self.add_orb)
            arcade.schedule(
                function_pointer=self.add_orb, interval=self.orb_countdown
            )

    def add_spikes(self, dt:float):
        if not self.game_over:
            direction = randint(0,1)
            if direction == 0:
                new_spikes = arcade.Sprite(
                    resource_path('resources/images/spikes/spikes_down.png'),
                    scale = 0.3
                )
                center_y = SCREEN_HEIGHT - 50
            else:
                new_spikes = arcade.Sprite(
                    resource_path('resources/images/spikes/spikes_up.png'),
                    scale = 0.3
                )
                center_y = 50
            new_spikes.center_x = SCREEN_WIDTH
            new_spikes.center_y = center_y
            self.spikes_list.append(new_spikes)
            self.spikes_hit[new_spikes] = False
            self.spikes_countdown -= 1
            self.spikes_speed += 0.05
            arcade.unschedule(function_pointer=self.add_spikes)
            arcade.schedule(
                function_pointer=self.add_spikes, interval=self.spikes_countdown
            )

    
    def on_update(self, delta_time):
        spike_hits = arcade.check_for_collision_with_list(
            sprite=self.player, sprite_list=self.spikes_list
            )
        for spike_hit in spike_hits:
            if not self.spikes_hit[spike_hit]:
                self.player_health -=1
                self.spikes_hit[spike_hit] = True
                arcade.play_sound(self.player_hit_sound)         
        bird_hits = arcade.check_for_collision_with_list(
            sprite=self.player, sprite_list=self.enemies_list
            )
        for bird_hit in bird_hits:
            if not bird_hit.hit:
                if bird_hit.center_y < self.player.center_y:
                    self.score += 10
                    bird_hit.hit = True
                    bird_hit.dead = True
                    bird_hit.play_died_sound()
                else:
                    self.player_health -= 1
                    bird_hit.hit = True
                    bird_hit.play_player_hit_sound()
        if self.player_health < 1:
            # unschedule schedulers
            self.game_over = True
            if not self.chimed:
                arcade.play_sound(self.game_over_sound)
                self.chimed = True
        orb_hits = arcade.check_for_collision_with_list(
            sprite=self.player, sprite_list=self.orbs_list
            )
        for orb_hit in orb_hits:
            self.player_health += 1
            arcade.play_sound(self.health_pickup_sound)
            orb_hit.remove_from_sprite_lists()
        orb_collisions = []    
        for enemy in self.enemies_list:
            orb_collisions = arcade.check_for_collision_with_list(
                sprite = enemy, sprite_list=self.orbs_list
                )
        for orb in orb_collisions:
            orb.remove_from_sprite_lists()
        if self.player.change_y != 1:
            self.player.change_y = -0.5
        if self.player.center_y < 30:
            self.player.center_y = 30
        if self.player.center_y > SCREEN_HEIGHT - 30:
            self.player.center_y = SCREEN_HEIGHT - 30
        if self.sprite_frame < 7:
            self.sprite_frame += 1
        else:
            self.sprite_frame = 0
        self.player_texture = self.player_textures[self.sprite_frame]
        for enemy in self.enemies_list:
            enemy.change_x = -(self.enemy_bird_speed) * self.player_speed
            choice_list = [-0.5, 0, 1]
            choice_list.append(enemy.last_y_direction)
            enemy.change_y = choice(choice_list)
            if enemy.center_y < 30:
                enemy.center_y = 30
            if enemy.center_y > SCREEN_HEIGHT - 30:
                enemy.center_y = SCREEN_HEIGHT - 30
            if enemy.center_x < -30:
                enemy.remove_from_sprite_lists()
        for spikes in self.spikes_list:
            spikes.change_x = -(self.spikes_speed) * self.player_speed
            if spikes.center_x < -50:
                spikes.remove_from_sprite_lists()
        for cloud in self.clouds_list:
            cloud.change_x = -(self.cloud_speed) * self.player_speed
            if cloud.center_x < -50:
                cloud.remove_from_sprite_lists()
        for orb in self.orbs_list:
            orb.change_x = -(self.orb_speed) * self.player_speed
            if orb.center_x < -30:
                orb.remove_from_sprite_lists()
        self.spikes_list.update()
        self.clouds_list.update()
        self.orbs_list.update()
        self.enemies_list.update()
        self.player_list.update()
        
    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP:
            self.player.change_y = 1
        elif key == arcade.key.RIGHT:
            if self.player_speed < 3:
                self.player_speed += 1
        elif key == arcade.key.LEFT:
            if self.player_speed > 1:
                self.player_speed -= 1

    def on_key_release(self, key, modifiers):
        if key == arcade.key.UP:
            self.player.change_y = 0
    
    def on_draw(self):
        self.clear()
        self.spikes_list.draw()
        self.clouds_list.draw()
        self.orbs_list.draw()
        self.enemies_list.draw()
        self.player_list.draw()
        # health bar
        length = self.player_health * 20
        start_x = 20
        arcade.draw_line(start_x, 20, start_x + length, 20, arcade.color.YELLOW, 10)
        self.score_text = arcade.Text(
            f"Score: {self.score}",
            SCREEN_WIDTH - 100,
            20,
            arcade.color.BLACK,
            12
        )
        self.score_text.draw()
        

def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = StartGameView()
    window.show_view(start_view)
    arcade.run()

if __name__ == "__main__":
    main()
