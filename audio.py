import pyaudio
import wave


class Audio:
    def __init__(self):
        self.mode = None

    def record(self, process_fn):
        if self.mode is not None:
            self.close()
        self.mode = 'record'

        # Define callback for playback (1)
        def callback(in_data, frame_count, time_info, status):
            process_fn(in_data, frame_count, self.width,
                       self.channels, self.rate)
            # If len(data) is less than requested frame_count, PyAudio automatically
            # assumes the stream is finished, and the stream stops.
            return (in_data, pyaudio.paContinue)

        # Instantiate PyAudio and initialize PortAudio system resources (2)
        self.pa = pyaudio.PyAudio()

        # Open stream using callback (3)
        info = self.pa.get_default_input_device_info()
        self.width = 2
        self.channels = info['maxInputChannels']
        self.rate = int(info['defaultSampleRate'])
        self.stream = self.pa.open(
            format=self.pa.get_format_from_width(self.width),
            channels=self.channels,
            rate=self.rate,
            input=True,
            stream_callback=callback
        )

    def read(self, filename, process_fn):
        if self.mode is not None:
            self.close()
        self.mode = 'read'

        self.wf = wave.open(filename, 'rb')

        # Define callback for playback (1)
        def callback(in_data, frame_count, time_info, status):
            data = self.wf.readframes(frame_count)
            process_fn(data, frame_count, self.width, self.channels, self.rate)
            # If len(data) is less than requested frame_count, PyAudio automatically
            # assumes the stream is finished, and the stream stops.
            return (data, pyaudio.paContinue)

        # Instantiate PyAudio and initialize PortAudio system resources (2)
        self.pa = pyaudio.PyAudio()

        # Open stream using callback (3)
        self.width = self.wf.getsampwidth()
        self.channels = self.wf.getnchannels()
        self.rate = self.wf.getframerate()
        self.stream = self.pa.open(
            format=self.pa.get_format_from_width(self.width),
            channels=self.channels,
            rate=self.rate,
            output=True,
            stream_callback=callback)

    def close(self):
        match self.mode:
            case 'record':
                # Close the stream (5)
                self.stream.close()
                # Release PortAudio system resources (6)
                self.pa.terminate()
            case 'read':
                # Close the stream (5)
                self.stream.close()
                # Release PortAudio system resources (6)
                self.pa.terminate()
                # Close audio file
                self.wf.close()
