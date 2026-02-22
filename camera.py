# ============================================================
#  等距摄像机：跟随玩家，世界坐标→屏幕坐标偏移
# ============================================================
from settings import INTERNAL_WIDTH, INTERNAL_HEIGHT, HALF_W, HALF_H
from utils import world_to_screen


class Camera:
    def __init__(self):
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.smooth = 0.08

    def update(self, target_wx, target_wy):
        """让摄像机平滑跟随目标的世界坐标"""
        sx, sy = world_to_screen(target_wx, target_wy)
        goal_x = sx - INTERNAL_WIDTH // 2
        goal_y = sy - INTERNAL_HEIGHT // 2

        self.offset_x += (goal_x - self.offset_x) * self.smooth
        self.offset_y += (goal_y - self.offset_y) * self.smooth

    def world_to_cam(self, wx, wy):
        """世界坐标 → 摄像机屏幕坐标"""
        sx, sy = world_to_screen(wx, wy)
        return sx - self.offset_x, sy - self.offset_y

    def snap(self, target_wx, target_wy):
        """立即跳转到目标位置（无平滑）"""
        sx, sy = world_to_screen(target_wx, target_wy)
        self.offset_x = sx - INTERNAL_WIDTH // 2
        self.offset_y = sy - INTERNAL_HEIGHT // 2
