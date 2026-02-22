"""自动运行游戏几帧并截图保存"""
import pygame
from game import Game
from settings import STATE_PLAYING, STATE_MENU

game = Game()

# 截图1: 菜单界面
for _ in range(5):
    game.handle_events()
    game.update()
    game.draw()
    game.clock.tick(60)

pygame.image.save(game.screen, "screenshot_menu.png")
print("Menu screenshot saved.")

# 切换到游戏状态
game.state = STATE_PLAYING
game.load_level()

# 模拟玩家右移+跳跃几帧
for i in range(40):
    game.handle_events()
    # 模拟按键
    if i < 20:
        game.player.vel_x = 2
    if i == 10:
        game.player.vel_y = -6
        game.player.on_ground = False
    game.player._move_and_collide(game.tilemap)
    game.camera.update(game.player.rect)
    game.draw()
    game.clock.tick(60)

pygame.image.save(game.screen, "screenshot_game.png")
print("Game screenshot saved.")

pygame.quit()
