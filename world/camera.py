# ============================================================
#  Isometric camera: follows player, world-to-screen offset
# ============================================================
from core.settings import INTERNAL_WIDTH, INTERNAL_HEIGHT, HALF_W, HALF_H
from core.utils import world_to_screen


class Camera:
    def __init__(self):
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.smooth = 0.08

    def update(self, target_wx, target_wy):
        """Smoothly follow the target's world coordinates."""
        sx, sy = world_to_screen(target_wx, target_wy)
        goal_x = sx - INTERNAL_WIDTH // 2
        goal_y = sy - INTERNAL_HEIGHT // 2

        self.offset_x += (goal_x - self.offset_x) * self.smooth
        self.offset_y += (goal_y - self.offset_y) * self.smooth

    def world_to_cam(self, wx, wy):
        """World coordinates -> camera screen coordinates."""
        sx, sy = world_to_screen(wx, wy)
        return sx - self.offset_x, sy - self.offset_y

    def snap(self, target_wx, target_wy):
        """Instantly snap to target position (no smoothing)."""
        sx, sy = world_to_screen(target_wx, target_wy)
        self.offset_x = sx - INTERNAL_WIDTH // 2
        self.offset_y = sy - INTERNAL_HEIGHT // 2
