import pyaudiowpatch as pyaudio
import logging
import math
import statistics
import time
import numpy

""" 
record desktop audio
- example
  https://github.com/s0d3s/PyAudioWPatch/blob/master/examples/pawp_record_wasapi_loopback.py
"""

logging.basicConfig(level=logging.INFO)


class DesktopAudio:
    SINE_FREQUENCY = 800
    SINE_PERIOD = 1 / SINE_FREQUENCY 
    VOLUME = 0.025
    PERIODS = 100
    DURATION = PERIODS * SINE_PERIOD
    py_audio = pyaudio.PyAudio()

    def __init__(self):
        print(f"duration = {self.DURATION}s") 
        try:
            # get default WASAPI info
            wasapi_info = self.py_audio.get_host_api_info_by_type(pyaudio.paWASAPI)
            logging.debug("wasapi_info: %s", wasapi_info)
        except OSError:
            logging.error(
                "Looks like WASAPI is not available on the system. Exiting..."
            )
            exit(2)

        self.output_device = self.py_audio.get_device_info_by_index(
            wasapi_info["defaultOutputDevice"]
        )

        # we need a loopback device ...
        if not self.output_device["isLoopbackDevice"]:
            # this device isn't but there will be a loopback device with the same name
            for loopback_device in self.py_audio.get_loopback_device_info_generator():
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
        self.CHUNK_SIZE = int(numpy.floor(self.DURATION * self.SAMPLE_RATE))
        self.in_data = numpy.ndarray([0])
        self.NUM_INPUT_CHANNELS = self.output_device["maxInputChannels"]
        self.NUM_OUTPUT_CHANNELS = 2

        # with py_audio.open(
        self.input_stream = self.py_audio.open(
            format=pyaudio.paFloat32,
            channels=self.output_device["maxInputChannels"],
            rate=int(self.SAMPLE_RATE),
            frames_per_buffer=self.CHUNK_SIZE,
            input=True,
            input_device_index=self.output_device["index"],
            stream_callback=self.record_data,
        )  # as stream:
        # time.sleep(10)
        print(self.output_device)

        self.output_stream = self.py_audio.open(
            format=pyaudio.paFloat32,
            channels=self.NUM_OUTPUT_CHANNELS,
            rate=int(self.SAMPLE_RATE),
            output=True,
            frames_per_buffer=self.CHUNK_SIZE,
            # stream_callback=self.generate_sine,
            stream_callback=self.loop_back,
            input_device_index=self.output_device["index"],
        )

    def print_level(self, in_data, frame_count, time_info, status):
        """Write frames and return PA flag (what is PA flag?!)"""

        print(f"\rLevel: {statistics.mean(in_data)}", end="")
        return (in_data, pyaudio.paContinue)

    def record_data(self, in_data, frame_count, time_info, status):
        # print(f"{in_data=}")
        in_data = numpy.frombuffer(in_data, dtype=numpy.float32)
        in_data = numpy.reshape(in_data, (self.CHUNK_SIZE, self.NUM_INPUT_CHANNELS))
        self.in_data = in_data

        return (in_data, pyaudio.paContinue)

    prev_time = 0
    curr_time = 0
    def generate_sine(self, in_data=None, frame_count=None, time_info=None, status=None):
        """Write frames and return PA flag (what is PA flag?!)"""
        # print(f"{in_data=}")
        # print(f"{frame_count=}")
        # print(f"{time_info=}")
        # print(f"{status=}")
        
        v = (self.VOLUME
            * numpy.sin(
                2
                * numpy.pi
                * numpy.arange(self.SAMPLE_RATE * self.DURATION)
                * self.SINE_FREQUENCY
                / self.SAMPLE_RATE,
            )).astype(numpy.float32).tobytes()
        self.go = False
        return (v, pyaudio.paContinue)

    def loop_back(self, in_data=None, frame_count=None, time_info=None, status=None):
        return (self.in_data.tobytes(), pyaudio.paContinue)
    


if __name__ == "__main__":
    dummy_indicator = None  # something to write to and see if we detect audio
    desktop_audio = DesktopAudio()
    # a = desktop_audio.generate_sine()[0]
    # print(type(numpy.frombuffer(a)))
    # __import__('pdb').set_trace()
    # sina = desktop_audio.generate_sine()[0]
    # desktop_audio.output_stream.write(sina)
    while True:
        time.sleep(10)
    logging.info("DONE")
