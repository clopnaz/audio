import pyaudiowpatch as pyaudio
import logging
import socket
import time


logging.basicConfig(level=logging.INFO)


class Client:
    HOST = 'localhost'
    PORT = 35511

    def __init__(self):
        self.clientaudio = ClientAudio()
        self.BUFFER = self.clientaudio.BYTES_PER_CALLBACK

    def communicate(self, data):
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.socket:
                self.socket.connect((self.HOST, self.PORT))
                self.socket.sendall(data)
                self.clientaudio.start(self.recv_pyaudio_callback_simple)
                print(dir(self.clientaudio.output_stream))
                print()
                while self.clientaudio.output_stream.is_active():
                    load = self.clientaudio.output_stream.get_cpu_load()
                    output_latency = self.clientaudio.output_stream.get_output_latency()
                    input_latency = self.clientaudio.output_stream.get_input_latency()
                    audio_time = self.clientaudio.output_stream.get_time()
                    is_active = self.clientaudio.output_stream.is_active()
                    is_stopped = self.clientaudio.output_stream.is_stopped()
                    print(f"\rLoad: {load:4.2} {input_latency=:2.4} {output_latency=:>4} {audio_time=:>8.3} active={is_active} stopped: {is_stopped}", end='')
                    time.sleep(1)
                time.sleep(1)
                print()
                print("Stream is not active. Restarting!") 
    
    def recv_pyaudio_callback_simple(self, in_data, frame_count, time_info, status):
        in_data = self.socket.recv(self.BUFFER)
        return (in_data, pyaudio.paContinue)

    def recv_pyaudio_callback_complex(self, in_data, frame_count, time_info, status):
        # set this as a socketserver callback to stream the audio from device

        in_data = bytes()
        bytes_remaining = self.clientaudio.BYTES_PER_CALLBACK
        while bytes_remaining > self.BUFFER:
            in_data += self.socket.recv(self.BUFFER)
            bytes_remaining = self.clientaudio.BYTES_PER_CALLBACK - len(in_data)
        # if by some fluke we still need to get less than BUFFER bytes
        if bytes_remaining:
            in_data += self.socket.recv(bytes_remaining)
            bytes_remaining = self.clientaudio.BYTES_PER_CALLBACK - len(in_data)
        assert(not(bytes_remaining))
        # print(f'receive {len(in_data)}')

        # self.sample_size = pyaudio.get_sample_size(self.clientaudio.FORMAT)
        # expected_len = self.clientaudio.BYTES_PER_CALLBACK
        # actual_len = len(in_data)
        # print(f"{expected_len=}")
        # print(f"{actual_len=}")
        return (in_data, pyaudio.paContinue)
    
    def handle_data(self,data):
        self.num_data += 1 
        print(f"\rreceived {len(data)} ({self.num_data})", end='')


class ClientAudio:
    VOLUME = 0.025
    FORMAT = pyaudio.paInt32
    FRAMES_PER_BUFFER=8

    def __init__(self):
        self.pyaudio = pyaudio.PyAudio()
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
        self.SAMPLE_RATE = int(self.output_device["defaultSampleRate"])
        self.NUM_OUTPUT_CHANNELS = self.output_device["maxInputChannels"]
        sample_size = pyaudio.get_sample_size(self.FORMAT)
        self.BYTES_PER_CALLBACK = sample_size * self.NUM_OUTPUT_CHANNELS * self.FRAMES_PER_BUFFER


    def start(self, callback):
        self.output_stream = self.pyaudio.open(
            format=self.FORMAT,
            channels=self.NUM_OUTPUT_CHANNELS,
            rate=int(self.SAMPLE_RATE),
            output=True,
            frames_per_buffer=self.FRAMES_PER_BUFFER,
            # stream_callback=self.generate_sine,
            stream_callback=callback,
            input_device_index=self.output_device["index"],
        )

    def example_callback(self, in_data=None, frame_count=None, time_info=None, status=None):
        """
        - in_data: a buffer of audio
          type(in_data): bytes
          len(in_data): sample_size * channels * frames_per_buffer
        """
        # change OUTPUT to INPUT if the stream's `input` is True.
        assert(len(in_data) == sample_size * self.NUM_OUTPUT_CHANNELS * self.FRAMES_PER_BUFFER) 
        return (in_data, pyaudio.paContinue)

    def print_level(self, in_data, frame_count, time_info, status):
        """Write frames and return PA flag (what is PA flag?!)"""

        print(f"\rLevel: {statistics.mean(in_data)}", end="")
        return (in_data, pyaudio.paContinue)






if __name__ == "__main__":
    client = Client()
    client.communicate("hello, server!".encode())
