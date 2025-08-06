from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
import tempfile
import wave
import re

class ASRService:
    def __init__(self):
        self.asr_pipeline = pipeline(
            task=Tasks.auto_speech_recognition,
            model='iic/SenseVoiceSmall',
            model_revision="master",
            disable_update=True
        ) # 新增：disable_update=True禁用funasr自动更新
        
    def recognize(self, audio_buffer):
        """接收音频缓冲区，返回识别文本"""
        try:
            # 尝试直接传入缓冲区（假设模型支持bytes类型）
            # 注意：部分模型需要指定采样率参数（如sample_rate=16000）
            result = self.asr_pipeline(
                input=audio_buffer.getvalue(),  # 改为input参数
                sample_rate=16000  # 显式指定采样率（与录音参数一致）
            )
            print(result)
            # 处理结果格式：可能是列表或字典
            if isinstance(result, list):
                # 若返回列表，取第一个元素的text（根据实际结果结构调整）
                text = result[0].get('text', '') if result else ''
            else:
                # 若返回字典，直接取text
                text = result.get('text', '')
                
            # 处理结果格式（新增：清理特殊标记）
            clean_text = re.sub(r'<\|.*?\|>', '', text)  # 用正则去除<|...|>格式的标记
            return clean_text
            
        except Exception as e:
            print(f"识别异常: {str(e)}")  # 打印调试信息
            # 回退到临时文件方式（兼容处理）
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                wf = wave.open(tmp_file, 'wb')
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16位=2字节
                wf.setframerate(16000)  # 确保与模型要求的采样率一致
                wf.writeframes(audio_buffer.getvalue())
                wf.close()
                # 调用pipeline时显式传递文件路径
                result = self.asr_pipeline(tmp_file.name)
                
                # 同样处理列表/字典结果
                # 处理结果格式（修改后）
                if isinstance(result, list) and len(result) > 0:
                    text = result[0]['text']  # 直接访问text字段（已知结构）
                else:
                    text = result.get('text', '') if isinstance(result, dict) else ''
                    
                return text