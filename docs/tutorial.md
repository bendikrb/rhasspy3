# Tutorial


## Installing Rhasspy 3

```sh
git clone https://github.com/rhasspy/rhasspy3
cd rhasspy3
script/setup
```


## Microphone

configuration.yaml:

```yaml
programs:
  mic:
    arecord:
      command: |
        arecord -q -r 16000 -c 1 -f S16_LE -t raw -
      adapter: |
        mic_adapter_raw.py --rate 16000 --width 2 --channels 1

pipelines:
  default:
    mic:
      name: arecord
```

Mic test:

```sh
script/run bin/mic_test_energy.py
```

CTRL+C to quit


## Voice Activity Detection

Install [Silero](https://github.com/snakers4/silero-vad/):

```sh
cp -R programs/vad/silero config/programs/vad/
config/programs/vad/silero/script/setup
```

configuration.yaml:

```yaml
programs:
  mic: ...
  vad:
    silero:
      command: |
        .venv/bin/python3 bin/silero_stream.py share/silero_vad.onnx

pipelines:
  default:
    mic: ...
    vad:
      name: silero
```


TODO: test

TODO: alternative energy


## Speech to Text

Install [Vosk](https://alphacephei.com/vosk/):

```sh
cp -R programs/asr/vosk config/programs/asr/
config/programs/asr/vosk/script/setup
config/programs/asr/vosk/script/download.py en_small
```

configuration.yaml:

```yaml
programs:
  mic: ...
  vad: ...
  asr:
    vosk:
      command: |
        script/raw2text ${model}
      adapter: |
        asr_adapter_raw2text.py
      template_args:
        model: "share/vosk-model-small-en-us-0.15"

pipelines:
  default:
    mic: ...
    vad: ...
    asr:
      name: vosk
```

Transcribe WAV:

```sh
script/run bin/asr_transcribe_wav.py --debug etc/what_time_is_it.wav
```

Transcribe stream:

```sh
script/run bin/pipeline_run.py --debug --stop-after asr
```

(say something)

Set up HTTP server:

```sh
script/setup_http_server
```

Run HTTP server:

```sh
script/http_server --debug
```

Transcribe WAV over HTTP:

```sh
curl -X POST -H 'Content-Type: audio/wav' --data-binary @etc/what_time_is_it.wav 'localhost:12101/api/speech-to-text'
```

Install websocket tool:

```sh
tools/asr/websocket-client/script/setup
```

Transcribe WAV over WebSocket:

```sh
tools/asr/websocket-client/script/wav2text 'ws://localhost:12101/api/stream-to-text' etc/what_time_is_it.wav
```

### Client/Server

configuration.yaml:

```yaml
programs:
  mic: ...
  vad: ...
  asr:
    vosk: ...
    vosk.client:
      command: |
        client_unix_socket.py var/run/vosk.socket

servers:
  asr:
    vosk:
      command: |
        script/server ${model}
      template_args:
        model: "share/vosk-model-small-en-us-0.15"

pipelines:
  default:
    mic: ...
    vad: ...
    asr:
      name: vosk.client
```

Run server standalone:

```sh
script/run bin/server_run.py asr vosk
```

Run with HTTP server:

```sh
script/http_server --debug --server asr vosk
```


## Wake Word Detection

Install [Porcupine](https://github.com/Picovoice/porcupine):

```sh
cp -R programs/wake/porcupine1 config/programs/wake/
config/programs/wake/porcupine1/script/setup
```

configuration.yaml:

```yaml
programs:
  mic: ...
  vad: ...
  asr: ...
  wake:
    porcupine1:
      command: |
        .venv/bin/python3 bin/porcupine_raw_text.py --model porcupine_linux.ppn
      adapter: |
        wake_adapter_raw.py

servers:
  asr: ...

pipelines:
  default:
    mic: ...
    vad: ...
    asr: ...
    wake:
      name: porcupine1
```

Use `_raspberry-pi.ppn` instead of `_linux.ppn` on Raspberry Pi.

Test wake word detection:

```sh
script/run bin/wake_detect.py --debug
```

(say "porcupine")

See available models:

```sh
find config/programs/wake/porcupine1 -name '*.ppn'
```

Run wake + speech to text:

```sh
script/run bin/pipeline_run.py --debug --stop-after asr
```

(say "porcupine", *pause*, voice command)

Reduce the pause length:

```sh
script/run bin/pipeline_run.py --debug --stop-after asr --asr-chunks-to-buffer 5
```

Test with HTTP server:

```sh
curl -X POST 'localhost:12101/api/wait-for-wake'
```

(say "porcupine")

Test full voice command:

```sh
curl -X POST 'localhost:12101/api/listen-for-command'
```

(say "porcupine", *pause*, voice command)



## Intent Handling

configuration.yaml:

```yaml
programs:
  mic: ...
  vad: ...
  asr: ...
  wake: ...
  handle:
    date_time:
      command: |
        bin/date_time.py
      adapter: |
        handle_adapter_text.py

servers:
  asr: ...

pipelines:
  default:
    mic: ...
    vad: ...
    asr: ...
    wake: ...
    handle:
      name: date_time

```

Install date time script:

```sh
cp -R programs/handle/date_time config/programs/handle/
```

Test input:

```sh
echo 'What time is it?' | script/run bin/handle_handle.py --debug
```

```sh
script/run bin/pipeline_run.py --debug --stop-after handle
```

(say "porcupine", *pause*, "what time is it?")