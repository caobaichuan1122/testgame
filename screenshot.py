"""Auto-run the game for a few frames and save screenshots."""
import pygame
from game import Game
from settings import STATE_PLAYING, STATE_MENU

game = Game()

# Screenshot 1: menu screen
for _ in range(5):
    game.handle_events()
    game.update()
    game.draw()
    game.clock.tick(60)

pygame.image.save(game.screen, "screenshot_menu.png")
print("Menu screenshot saved.")

# Switch to playing state
game.state = STATE_PLAYING
game.load_level()

# Simulate player moving right and jumping
for i in range(40):
    game.handle_events()
    # Simulate key presses
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
