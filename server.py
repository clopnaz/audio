import pyaudiowpatch as pyaudio
import logging
import socketserver
import time


logging.basicConfig(level=logging.INFO)


class Handler(socketserver.BaseRequestHandler):
    data = "Hello client!".encode()


    def handle(self):
        self.server.serveraudio.start(self.sendall_pyaudio_callback)
        while True:
            time.sleep(1)
     
    def sendall_pyaudio_callback(self, in_data, frame_count, time_info, status):
        # set this as a socketserver callback to stream the audio from device
        # self.request.sendall(in_data)
        # print(f"send {len(in_data)}")
        self.request.sendall(in_data)
        return (in_data, pyaudio.paContinue)

    def handle_input(self, data):
        data = self.request.recv(1024)
        # handle whatever the client sends us. 
        print(data.decode()) # for now I have no ideas




class SocketServer(socketserver.TCPServer):
    allow_reuse_address = True
    def __init__(self, serveraudio, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serveraudio = serveraudio


class ServerAudio:
    FRAMES_PER_BUFFER = 8
    FORMAT=pyaudio.paInt32
    pyaudio = pyaudio.PyAudio()

    def __init__(self):
        self.in_data = bytes()
        try:
            # get default WASAPI info
            wasapi_info = self.pyaudio.get_host_api_info_by_type(pyaudio.paWASAPI)
            logging.debug("wasapi_info: %s", wasapi_info)
        except OSError:
            logging.error(
                "Looks like WASAPI is not available on the system. Exiting..."
            )
            exit(2)

        self.output_device = self.pyaudio.get_device_info_by_index(
            wasapi_info["defaultOutputDevice"]
        )

        # we need a loopback device ...
        if not self.output_device["isLoopbackDevice"]:
            # this device isn't but there will be a loopback device with the same name
            for loopback_device in self.pyaudio.get_loopback_device_info_generator():
                if self.output_device["name"] in loopback_device["name"]:
                    # we found the device.
                    self.output_device = loopback_device
                    break
            else:
                logging.error(
                    "".join(
                        [
                            "Default loopback output device not found. \n\nRun `python ",
                            "-m pyaudiowpatch` to check available devices.\nExiting...",
                            "\n",
                        ]
                    )
                )
                exit(3)
        logging.info("Recording device found!")
        logging.debug("Device: {%s: %s}", self.output_device["index"], self.output_device["name"])
        self.SAMPLE_RATE = self.output_device["defaultSampleRate"]
        assert(self.SAMPLE_RATE.is_integer())
        self.SAMPLE_RATE = int(self.SAMPLE_RATE)
        self.NUM_INPUT_CHANNELS = self.output_device["maxInputChannels"]
        self.NUM_OUTPUT_CHANNELS = 2

    def start(self, callback):
        self.input_stream = self.pyaudio.open(
            format=self.FORMAT,
            channels=self.NUM_INPUT_CHANNELS,
            rate=self.SAMPLE_RATE,
            frames_per_buffer=self.FRAMES_PER_BUFFER,
            input=True,
            input_device_index=self.output_device["index"],
            stream_callback=callback
        ) 

    def store_a_frame(self, in_data, frame_count, time_info, status):
        """
        INFO:root:frame_count=1024
        INFO:root:time_info={
            'input_buffer_adc_time': 141453.65598563335,
            'current_time': 141453.6606523,
            'output_buffer_dac_time': 0.0
        }
        INFO:root:status=0
        """
        self.in_data = in_data
        return (in_data, pyaudio.paContinue)


class Server:
    HOST = ''
    PORT = 35511
    BUFFER = 1024
    def __init__(self, *args, **kwargs):
        self.serveraudio = ServerAudio()
        self.socketserver = SocketServer(self.serveraudio, (self.HOST, self.PORT), Handler)

    def serve(self):
        with self.socketserver:
            self.socketserver.serve_forever()



if __name__ == "__main__":
    server = Server()
    server.serve()
