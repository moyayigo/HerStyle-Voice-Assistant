import pyaudio
import numpy as np
import time
import io

class AudioCapturer:
    def __init__(self, rate=16000, chunk_size=1024, 
                 silence_threshold=500, silence_duration=3):
        self.rate = rate
        self.chunk_size = chunk_size
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.buffer = io.BytesIO()
        self._is_recording = False
        
    def get_rms(self, data):
        samples = np.frombuffer(data, dtype=np.int16)
        return np.sqrt(np.mean(samples**2))
    
    def start_capture(self, max_duration=30):
        self.buffer = io.BytesIO()  # 新增：重置缓冲区
        self._is_recording = True
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=self.rate,
                        input=True,
                        frames_per_buffer=self.chunk_size)
        
        silent_start = None
        recording_start = time.time()
        
        while self._is_recording:
            data = stream.read(self.chunk_size)
            self.buffer.write(data)
            
            volume = self.get_rms(data)
            if volume < self.silence_threshold:
                if silent_start is None:
                    silent_start = time.time()
                elif time.time() - silent_start >= self.silence_duration:
                    break
            else:
                silent_start = None
                
            if time.time() - recording_start >= max_duration:
                break
                
        stream.stop_stream()
        stream.close()
        p.terminate()
        return self.buffer
    
    def stop(self):
        self._is_recording = False
