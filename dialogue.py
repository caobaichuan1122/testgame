# ============================================================
#  对话树：节点、选项、条件分支
# ============================================================


class DialogueManager:
    """管理所有对话数据"""

    def __init__(self):
        self.dialogues = {}  # id → DialogueTree
        self.active_dialogue = None
        self.active_node = None
        self.speaker_name = ""
        # 打字机效果
        self._full_text = ""
        self._display_text = ""
        self._char_index = 0
        self._typewriter_speed = 2  # 每N帧显示一个字符
        self._tick = 0
        self._finished = False  # 当前文本是否打完

    def register(self, dialogue_id, nodes):
        """注册一棵对话树
        nodes: dict of node_id → {
            "text": str,
            "options": [{"label": str, "next": node_id, "condition": fn, "callback": fn}],
        }
        """
        self.dialogues[dialogue_id] = nodes

    def start(self, dialogue_id, speaker=""):
        """开始对话"""
        if dialogue_id not in self.dialogues:
            # 动态生成简单对话
            self.dialogues[dialogue_id] = {
                "start": {
                    "text": "...",
                    "options": [{"label": "OK", "next": None}],
                }
            }
        self.active_dialogue = self.dialogues[dialogue_id]
        self.active_node = self.active_dialogue.get("start")
        self.speaker_name = speaker
        self._start_typewriter()

    def _start_typewriter(self):
        """重置打字机状态"""
        if self.active_node:
            self._full_text = self.active_node.get("text", "")
        else:
            self._full_text = ""
        self._display_text = ""
        self._char_index = 0
        self._tick = 0
        self._finished = False

    def update_typewriter(self):
        """每帧推进打字机效果"""
        if self._finished or not self.active_node:
            return
        self._tick += 1
        if self._tick >= self._typewriter_speed:
            self._tick = 0
            self._char_index += 1
            if self._char_index >= len(self._full_text):
                self._char_index = len(self._full_text)
                self._finished = True
            self._display_text = self._full_text[:self._char_index]

    def skip_typewriter(self):
        """跳过打字机，立即显示全部文本"""
        self._display_text = self._full_text
        self._char_index = len(self._full_text)
        self._finished = True

    @property
    def typewriter_done(self):
        return self._finished

    def get_current_text(self):
        if self.active_node:
            return self._display_text
        return ""

    def get_options(self):
        if not self.active_node:
            return []
        options = self.active_node.get("options", [])
        # 过滤有条件的选项
        result = []
        for opt in options:
            cond = opt.get("condition")
            if cond is None or cond():
                result.append(opt)
        return result

    def select_option(self, index, game=None):
        """选择选项，返回是否对话结束"""
        options = self.get_options()
        if index < 0 or index >= len(options):
            return True

        opt = options[index]

        # 执行回调
        callback = opt.get("callback")
        if callback and game:
            callback(game)

        # 跳转到下一节点
        next_id = opt.get("next")
        if next_id is None:
            self.close()
            return True

        self.active_node = self.active_dialogue.get(next_id)
        if self.active_node is None:
            self.close()
            return True
        self._start_typewriter()
        return False

    def close(self):
        self.active_dialogue = None
        self.active_node = None
        self.speaker_name = ""

    @property
    def is_active(self):
        return self.active_node is not None
