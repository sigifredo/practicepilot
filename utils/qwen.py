from . import log

import time
import torch
import transformers

MODEL_NAME = 'Qwen/Qwen3-4B-Instruct-2507'


class Qwen:
    def __init__(self, seed: int | None = None):
        if not torch.cuda.is_available():
            raise RuntimeError('CUDA no disponible')

        self.system_prompt = ''
        self.model_name = MODEL_NAME
        self.seed = seed  # None => semilla variable

        try:
            quant_config = transformers.BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type='nf4',
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.float16,
            )
        except Exception:
            quant_config = None

        self.tokenizer = transformers.AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=False,
            use_fast=True,
        )

        self.model = transformers.AutoModelForCausalLM.from_pretrained(
            self.model_name,
            quantization_config=quant_config,
            device_map='auto',
            trust_remote_code=False,
        )

        self.model.eval()
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model.generation_config.pad_token_id = self.tokenizer.eos_token_id

    def _seed_everything(self):
        if self.seed is None:
            seed = int(time.time_ns() % (2**32 - 1))
        else:
            seed = int(self.seed) % (2**32 - 1)

        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)

        return seed

    def device(self):
        return self.model.device

    def dtype(self):
        return self.model.dtype

    def run_prompt(self, user_prompt: str) -> str:
        start = time.perf_counter()
        used_seed = self._seed_everything()

        messages = [
            {'role': 'system', 'content': self.system_prompt},
            {'role': 'user', 'content': user_prompt},
        ]

        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        inputs = self.tokenizer(text, return_tensors='pt').to(self.model.device)

        with torch.inference_mode():
            output = self.model.generate(
                **inputs,
                max_new_tokens=512,
                do_sample=True,
                temperature=0.8,  # más alto => más variedad (demasiado alto => deriva)
                top_p=0.9,
                top_k=50,
                repetition_penalty=1.05,
                use_cache=True,
            )

        new_tokens = output[0, inputs['input_ids'].shape[-1] :]
        response = self.tokenizer.decode(new_tokens, skip_special_tokens=True)

        end = time.perf_counter()
        log.info(f'Tiempo: {end - start:0.2f}s | seed={used_seed}')

        return response

    def set_system_prompt(self, prompt: str) -> None:
        self.system_prompt = prompt
