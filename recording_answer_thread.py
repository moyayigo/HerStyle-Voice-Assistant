from PyQt5.QtCore import QThread, pyqtSignal
import re

class RecordingAnswerThread(QThread):
    recording_completed = pyqtSignal()  # 录音完成信号
    recognition_finished = pyqtSignal(str)  # 识别完成信号
    response_generated = pyqtSignal(dict)  # 响应生成信号
    recognition_empty = pyqtSignal()  # 识别内容为空信号
    context_updated = pyqtSignal(list)  # 上下文更新信号
    newtalk_requested = pyqtSignal()  # 新增：触发新话题信号

    def __init__(self, capturer, asr, conversation_history, ollama_client):  # 新增客户端参数
        super().__init__()
        self.capturer = capturer
        self.asr = asr
        self.current_context = conversation_history
        self.client = ollama_client  # 接收服务类传入的客户端

    def clear_context(self):
        """清空对话上下文（重置会话），开始新的对话"""
        self.current_context = None
        self.context_updated.emit(None)
        print("Context cleared.")

    def run(self):
        # 1. 录音
        audio_buffer = self.capturer.start_capture()
        self.recording_completed.emit()  # 发射录音完成信号（触发UI更新）

        # 2. 识别
        text = self.asr.recognize(audio_buffer)
        clean_text = re.sub(r'<\|.*?\|>', '', text)
        
        # 新增：检测识别内容是否为空（去除前后空格后判断）
        if not clean_text.strip() or clean_text.strip() == "停止":
            self.recognition_empty.emit()  # 发射识别内容为空信号
            return  # 终止后续流程
        elif clean_text.strip() == "新话题":  # 去除前后空格后判断
            self.newtalk_requested.emit()  # 修正：补全信号名称为 newtalk_requested
            return  # 终止后续流程

        user_utterance = f"用户: {clean_text}"  # 格式化为用户发言
        self.recognition_finished.emit(user_utterance)  # 发射识别完成信号

        # 3. 生成响应（传递context，不开启raw模式）
        # 构建 generate 方法的参数
        try:
            generate_kwargs = {
                'model': 'qwen2.5-coder:0.5b',
                'prompt': clean_text,
                'stream': True
            }
            # 如果存在上一次的上下文，则将其传递给模型
            if self.current_context:
                generate_kwargs['context'] = self.current_context
            # 调用generate方法
            response_stream = self.client.generate(**generate_kwargs)
            full_response_content = ""  # 初始化回复内容
            new_context = None  # 初始化新的上下文
            eval_count = 0  # 初始化eval计数器
            last_token = ""  # 初始化上一个token
            response = {}  # 初始化原始响应对象
            for chunk in response_stream:
                if 'response' in chunk:
                    full_response_content += chunk['response']
                if 'context' in chunk and chunk['context']:
                    new_context = chunk['context']
                if 'eval_count' in chunk:  # 实时获取每个chunk的eval_count
                    eval_count = chunk['eval_count']
            # 打印最终eval_count（最后一个chunk的值）
            print(f'Token count: {eval_count}')
            # 添加空值检查并优化注释
            if new_context and len(new_context) >= 2:  # 确保存在足够的上下文token
                last_token = str(new_context[-2:])  # 显示最新的两个上下文token（调试用）
            
            # 4. 提取模型返回的context（token ID列表）并追加到历史中
            # 更新当前的上下文，确保获取到最终的context
            if new_context:
                self.current_context = new_context
                self.context_updated.emit(self.current_context)  # 发射更新后的上下文
            response = {
                'response': full_response_content.strip(),  # 完整的回复内容
                'context': last_token,  # 最新的上下文（token ID列表）
                'eval_count': eval_count  # 最新的eval_count
            }
        except Exception as e:
            print(f"Error during generation: {e}")
            self.clear_context() # 出现错误时，清除上下文，避免后续请求继续使用错误状态

        # 5. 发射响应生成信号（包含原始响应数据）
        self.response_generated.emit(response)