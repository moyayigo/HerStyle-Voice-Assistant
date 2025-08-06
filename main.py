from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                            QPushButton, QTextEdit, QLabel, 
                            QProgressBar, QWidget, QSizePolicy)
from PyQt5.QtCore import QTimer, Qt
import pyttsx3  # 新增：导入语音库
from voice_assistant_service import VoiceAssistantService  # 引入服务类
import sys

class VoiceAssistantGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("智能语音助手 Qt版")
        self.setGeometry(100, 100, 600, 500)
        self.init_ui()
        self.init_service()  # 初始化服务
        self.engine = pyttsx3.init()  # 新增：初始化语音引擎（避免重复创建）
    
    def init_service(self):
        self.service = VoiceAssistantService()
        # 绑定新增的识别为空信号
        self.service.recognition_empty.connect(self.handle_recognition_empty)
        # 绑定新增的录音完成信号
        self.service.recording_completed.connect(self.on_recording_completed)
        self.service.recognition_finished.connect(self.update_history)
        self.service.response_generated.connect(self.handle_response)
        self.service.newtalk_requested.connect(self.new_talk)  # 绑定新话题信号到方法
    
    # 在init_ui中添加重置按钮
    def init_ui(self):
        # 设置全屏
        self.showFullScreen()
        
        # 创建中央部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignCenter)
        
        # 录音控制按钮
        self.record_btn = QPushButton("开始对话", self)
        self.record_btn.setFixedWidth(200)
        self.record_btn.setFixedHeight(100)
        self.record_btn.setStyleSheet("margin: 20px;font-size:24px;color:#FFF3BC")
        self.record_btn.clicked.connect(self.toggle_recording)
        layout.addWidget(self.record_btn, 0, Qt.AlignCenter)
        
        # 进度条
        self.progress = QProgressBar()
        self.progress.setFixedHeight(16)
        self.progress.setFixedWidth(800)
        layout.addWidget(self.progress, 0, Qt.AlignCenter)
        
        # 状态标签
        self.status_label = QLabel("准备就绪")
        self.status_label.setStyleSheet("margin: 20px; color: white;font-size:42px")
        layout.addWidget(self.status_label, 0, Qt.AlignCenter)
        
        # 对话历史
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        self.history_text.setFixedHeight(100)
        self.history_text.setFixedWidth(500)
        self.history_text.setStyleSheet("padding: 20px;")
        layout.addWidget(self.history_text, 0, Qt.AlignCenter)
        
        # 设置窗口样式
        self.setStyleSheet("background-color: #FE2E2E; color: white;font-family: 微软雅黑;font-size: 18px;")
        
    def toggle_recording(self):
        if not hasattr(self, 'is_recording'):
            self.is_recording = False
        if self.is_recording:
            self.service.stop_recording()  # 修正：调用服务类的停止方法
        else:
            self.start_recording()

    def start_recording(self):
        self.is_recording = True
        self.record_btn.setText("正在聆听")
        self.record_btn.setEnabled(False)
        self.status_label.setText("声纹捕获中...")  # 阶段1：录音开始
        self.progress.setRange(0, 0)
        self.service.start_recording()

    def on_recording_completed(self):
        self.record_btn.setText("请稍后")
        self.status_label.setText("识别中...")  # 阶段2：录音结束，进入识别
        self.progress.setRange(0, 100)
        self.progress.setValue(30)

    def update_history(self, text):
        self.history_text.append(text)  # 仅更新UI显示的历史文本
        # 移除：self.service.update_conversation_history(text)  # 不再同步文本到服务类
        self.progress.setValue(60)
        self.status_label.setText("助手思考中...")  # 阶段3：识别完成，进入模型思考

    def text_to_speech(self, text):
        """新增：文本转语音方法"""
        self.engine.setProperty('rate', 150)  # 设置语速（可根据需求调整）
        self.engine.setProperty('volume', 0.9)  # 设置音量（0-1）
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice',voices[3].id) 
        self.engine.say(text)
        self.engine.runAndWait()  # 注意：此方法会阻塞主线程，简单场景可直接使用

    def handle_response(self, response):
        assistant_text = f"助手: {response['response']}"
        self.update_history(assistant_text)
        self.status_label.setText("回答中...")
        self.progress.setValue(90)
        # 语音播报完成后自动重启录音
        self.text_to_speech(response['response'])
        # 更新UI状态为准备接受新输入
        self.record_btn.setText("正在聆听")
        self.status_label.setText("请继续说话...")  # 修改状态提示
        #self.record_btn.setEnabled(True)
        self.progress.setRange(0, 0)
        # 延迟500毫秒后自动开始新录音
        QTimer.singleShot(500, self.start_recording)  # 新增自动重启逻辑
        self.is_recording = False
        self.progress.setValue(100)

    def handle_recognition_empty(self):
        # 重置录音按钮
        self.record_btn.setText("开始对话")
        self.record_btn.setEnabled(True)
        self.is_recording = False
        # 重置状态标签
        self.status_label.setText("准备就绪")
        # 重置进度条
        self.progress.setValue(0)
        self.history_text.append("**对话已停止**")
    
    def new_talk(self):
        self.service.clear_context()
        self.history_text.clear()
        self.record_btn.setText("正在聆听")
        self.status_label.setText("已开启新话题，请继续说话...")
        self.progress.setRange(0, 0)
        QTimer.singleShot(500, self.start_recording)
        self.is_recording = False
        self.progress.setValue(100)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VoiceAssistantGUI()
    window.show()
    sys.exit(app.exec_())
