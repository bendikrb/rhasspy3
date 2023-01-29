#!/usr/bin/env python3
import argparse
import asyncio
import json
import logging
from typing import IO, Optional, Union

from rhasspy3.asr import Transcript
from rhasspy3.core import Rhasspy
from rhasspy3.event import Event
from rhasspy3.handle import Handled, NotHandled
from rhasspy3.intent import Intent, NotRecognized
from rhasspy3.pipeline import run as run_pipeline
from rhasspy3.wake import Detection

_LOGGER = logging.getLogger("pipeline_run")


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        required=True,
        help="Configuration directory",
    )
    parser.add_argument("pipeline", help="Name of pipeline to run")

    parser.add_argument("--wake-name")
    parser.add_argument("--asr-wav")
    parser.add_argument("--asr-text")
    parser.add_argument("--intent-json")
    parser.add_argument("--handle-text")
    parser.add_argument("--tts-wav")

    parser.add_argument("--samples-per-chunk", type=int, default=1024)
    parser.add_argument("--asr-chunks-to-buffer", type=int, default=0)
    parser.add_argument("--debug", action="store_true", help="Log DEBUG messages")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    wake_detection: Optional[Detection] = None
    if args.wake_name:
        wake_detection = Detection(name=args.wake_name)

    asr_wav_in: Optional[IO[bytes]] = None
    if args.asr_wav:
        asr_wav_in = open(args.asr_wav, "rb")

    asr_transcript: Optional[Transcript] = None
    if args.asr_text:
        asr_transcript = Transcript(text=args.asr_text)

    intent_result: Optional[Union[Intent, NotRecognized]] = None
    if args.intent_json:
        intent_event = Event.from_dict(json.loads(args.intent_json))
        if Intent.is_type(intent_event.type):
            intent_result = Intent.from_event(intent_event)
        elif NotRecognized.is_type(intent_event.type):
            intent_result = NotRecognized.from_event(intent_event)

    handle_result: Optional[Union[Handled, NotHandled]] = None
    if args.handle_text:
        handle_result = Handled(text=args.handle_text)

    tts_wav_in: Optional[IO[bytes]] = None
    if args.tts_wav:
        tts_wav_in = open(args.tts_wav, "rb")

    rhasspy = Rhasspy.load(args.config)
    await run_pipeline(
        rhasspy,
        args.pipeline,
        samples_per_chunk=args.samples_per_chunk,
        asr_chunks_to_buffer=args.asr_chunks_to_buffer,
        wake_detection=wake_detection,
        asr_wav_in=asr_wav_in,
        asr_transcript=asr_transcript,
        intent_result=intent_result,
        handle_result=handle_result,
        tts_wav_in=tts_wav_in,
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass