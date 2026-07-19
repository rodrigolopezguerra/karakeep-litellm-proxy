import os
from typing import Literal, Optional, Union

from litellm.caching.caching import DualCache
from litellm.integrations.custom_logger import CustomLogger
from litellm.proxy._types import UserAPIKeyAuth


class MiniMaxThinkingDisabler(CustomLogger):
    async def async_pre_call_hook(
        self,
        user_api_key_dict: UserAPIKeyAuth,
        cache: DualCache,
        data: dict,
        call_type: Literal[
            "completion",
            "text_completion",
            "embeddings",
            "image_generation",
            "moderation",
            "audio_transcription",
            "pass_through_endpoint",
            "rerank",
        ],
    ) -> Optional[Union[Exception, str, dict]]:
        print(f"[CALLBACK] async_pre_call_hook called: call_type={call_type}, model={data.get('model')}", flush=True)
        if call_type != "completion":
            return data

        model = data.get("model", "") or ""
        if "MiniMax" not in model:
            return data

        extra = data.setdefault("extra_body", {})
        extra["thinking"] = {"type": "disabled"}
        extra["reasoning_split"] = True
        print(f"[CALLBACK] injected extra_body={extra}", flush=True)
        return data


proxy_handler = MiniMaxThinkingDisabler()
print("[CALLBACK] module loaded", flush=True)