from PyQt5.QtCore import QObject, pyqtSignal
from audio_capture import AudioCapturer
from asr_service import ASRService
from recording_answer_thread import RecordingAnswerThread  # 新增：导入拆分后的类
import ollama  # 导入单例客户端

class VoiceAssistantService(QObject):
    # 修正：信号参数与子线程一致（仅传递当前发言文本）
    recognition_finished = pyqtSignal(str)  # 原错误行：pyqtSignal(str, list)
    response_generated = pyqtSignal(dict)
    recording_completed = pyqtSignal()
    recognition_empty = pyqtSignal()  # 新增信号
    newtalk_requested = pyqtSignal()  # 新增：服务层转发新话题信号

    def __init__(self):
        super().__init__()
        self.capturer = AudioCapturer()
        self.asr = ASRService()
        self.thread = None
        self.conversation_history = None
        # 新增：单例客户端初始化
        self.ollama_client = ollama.Client()  # 全局唯一客户端实例

    def start_recording(self):
        # 创建线程时传递客户端实例
        self.thread = RecordingAnswerThread(
            self.capturer, 
            self.asr, 
            self.conversation_history,
            self.ollama_client  # 传入单例客户端
        )
        # 绑定信号（参数匹配后即可正常连接）
        self.thread.recognition_finished.connect(self.recognition_finished)
        # 绑定新增的识别为空信号
        self.thread.recognition_empty.connect(self.recognition_empty)
        # 绑定子线程信号到当前服务的信号
        self.thread.recording_completed.connect(self.recording_completed)
        # 绑定信号（响应生成）
        self.thread.response_generated.connect(self.response_generated)
        # 绑定信号（context更新）
        self.thread.context_updated.connect(self.handle_context_update)
        self.thread.newtalk_requested.connect(self.newtalk_requested)  # 转发子线程信号
        self.thread.start()  # 启动子线程（不会阻塞主线程）

    def stop_recording(self):
        if self.thread and self.thread.isRunning():
            self.capturer.stop()  # 停止录音
            self.thread.quit()  # 终止子线程（根据实际需求调整）

    def handle_context_update(self, new_context):
        """处理上下文更新"""
        self.conversation_history = new_context  # 更新父类的上下文变量

    def clear_context(self):
        """清空对话上下文"""
        self.conversation_history = None
        print("Service context cleared")