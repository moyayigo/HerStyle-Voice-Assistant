
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QProgressBar, 
                            QVBoxLayout, QWidget, QPushButton, QTextEdit, QLabel)  # 补充QLabel导入
from PyQt5.QtCore import Qt

class FullScreenProgress(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # 设置全屏
        self.showFullScreen()
        
        # 创建中央部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignCenter)
        
        # 添加上方按钮（宽度100px）
        self.button = QPushButton("按钮")
        self.button.setFixedWidth(200)
        self.button.setFixedHeight(100)
        self.button.setStyleSheet("margin: 20px;font-size:24px;color:#FFF3BC")
        layout.addWidget(self.button, 0, Qt.AlignCenter)
        
        # 添加进度条（高度100px）
        self.progress = QProgressBar()
        self.progress.setFixedHeight(10)
        self.progress.setFixedWidth(800)
        layout.addWidget(self.progress, 0, Qt.AlignCenter)
        
        # 新增：进度条下方标签
        self.label = QLabel("这是进度条下方的标签")  # 创建标签
        self.label.setStyleSheet("margin: 20px; color: white;font-size:42px")  # 保持20px外边距，文字颜色与窗口一致
        layout.addWidget(self.label, 0, Qt.AlignCenter)  # 添加到布局并居中
        
        # 添加下方文本编辑框（宽度100px）
        self.text_edit = QTextEdit("这是标签下方的文本编辑框")
        self.text_edit.setFixedHeight(100)
        self.text_edit.setFixedWidth(500)
        self.text_edit.setStyleSheet("padding: 20px;")
        layout.addWidget(self.text_edit, 0, Qt.AlignCenter)
        
        # 设置窗口样式
        self.setStyleSheet("background-color: #FE2E2E; color: white;font-family: 微软雅黑;font-size: 18px;")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FullScreenProgress()
    sys.exit(app.exec_())