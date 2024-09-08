# one of these two ought to get the job done ... 
import ctypes
import pywin32
# import ssl


"""
# processaudio
use ActivateAudioInterfaceAsync with AUDIOCLIENT_PROCESS_LOOPBACK_PARAMS to get 
the audio from one process. 

# links
ActivateAudioInterfaceAsync
- https://learn.microsoft.com/en-us/windows/win32/api/mmdeviceapi/nf-mmdeviceapi-activateaudiointerfaceasync
AUDIOCLIENT_PROCESS_LOOPBACK_PARAMS
- https://learn.microsoft.com/en-us/windows/win32/api/audioclientactivationparams/ns-audioclientactivationparams-audioclient_process_loopback_params

"""

