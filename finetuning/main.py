
import os
os.environ["HF_HUB_DISABLE_XET"] = "1"


from transformers import (
    AutoModelForCausalLM, 
    AutoTokenizer, 
    TrainingArguments, 
    Trainer
)
from datasets import load_dataset, concatenate_datasets
from peft import LoraConfig, get_peft_model, TaskType
from pathlib import Path
import torch
import huggingface_hub

PERCENTAGE = 0.05 


def _patch_windows_long_paths():
    if os.name != 'nt':
        return
    original_incomplete_path = huggingface_hub._local_folder.LocalDownloadFilePaths.incomplete_path
    def patched_incomplete_path(self, etag: str) -> Path:
        path = original_incomplete_path(self, etag)
        resolved_str = str(path.resolve())
        if len(resolved_str) > 255 and not resolved_str.startswith(r"\\?\\"):
            return Path(r"\\?\\{}".format(resolved_str))
        return path
    huggingface_hub._local_folder.LocalDownloadFilePaths.incomplete_path = patched_incomplete_path

_patch_windows_long_paths()

# Login 
from huggingface_hub import login
login(token="")


device = torch.device("cuda")

import torch

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
)

from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training,
    TaskType,
)

assert torch.cuda.is_available(), "CUDA is not available!"

model_name = "google/gemma-3-4b-it"


bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=(
        torch.bfloat16
        if torch.cuda.is_bf16_supported()
        else torch.float16
    ),
    bnb_4bit_use_double_quant=True,
)


model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map={"": 0},
    torch_dtype=(
        torch.bfloat16
        if torch.cuda.is_bf16_supported()
        else torch.float16
    ),
    trust_remote_code=True,
    token="",
)

tokenizer = AutoTokenizer.from_pretrained(
    model_name,
    trust_remote_code=True,
    padding_side="right",
    token="",
)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model.config.use_cache = False

model.gradient_checkpointing_enable()


model = prepare_model_for_kbit_training(model)

lora_config = LoraConfig(
    r=16,
    lora_alpha=8,
    target_modules = [
    "q_proj",
    "k_proj",
    "v_proj",
    "o_proj",
    ],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
)


model = get_peft_model(model, lora_config)


model.print_trainable_parameters()


print("CUDA available:", torch.cuda.is_available())
print("GPU:", torch.cuda.get_device_name(0))
print("Model device:", next(model.parameters()).device)

DATA_DIR = r"D:\dionigi\Documents\RAG\LawInstruct\data\lawinstruct\data"
MAX_SEQ_LENGTH = 256

files = [str(p) for p in Path(DATA_DIR).glob("*.jsonl.xz")]

datasets_list = []
for file in files:
    try:
        ds = load_dataset(
            "json",
            data_files=file,
            split="train",
        )

        ds = ds.shuffle(seed=3407)

        sample_size = int(len(ds) * PERCENTAGE)

        ds = ds.select(range(sample_size))

        def format_example(example):
            text = f"""### Instruction:
{example['instruction']}

### Input:
{example['prompt']}

### Response:
{example['answer']}"""

            return {"text": text}

        ds = ds.map(format_example)

        ds = ds.remove_columns(
            [c for c in ds.column_names if c != "text"]
        )

        datasets_list.append(ds)

        print(f"Loaded {sample_size} samples from: {file}")

    except Exception as e:
        print(f"Failed: {file}")
        print(e)

dataset = concatenate_datasets(datasets_list)

print(f"Dataset size: {len(dataset)}")

def tokenize_function(examples):
    return tokenizer(
        examples["text"],
        truncation=True,
        max_length=MAX_SEQ_LENGTH,
        padding=False,
        return_tensors=None,
    )


tokenized_dataset = dataset.map(
    tokenize_function,
    batched=True,
    remove_columns=dataset.column_names,
    desc="Tokenizing dataset",
)

training_args = TrainingArguments(
    output_dir="gemma3-pretrain",
    per_device_train_batch_size=1,
    gradient_accumulation_steps=2,
    warmup_steps=2,
    max_steps=1000,
    learning_rate=2e-4,
    logging_steps=10,
    optim="adamw_8bit",  
    weight_decay=0.01,
    lr_scheduler_type="cosine",
    seed=3407,
    fp16=not torch.cuda.is_bf16_supported(),
    bf16=torch.cuda.is_bf16_supported(),
    report_to="none",
    save_steps=500, 
    save_total_limit=2,  
    logging_dir="./logs",
    gradient_checkpointing=True,  
    ddp_find_unused_parameters=False,  
    no_cuda=False
)


from transformers import DataCollatorForLanguageModeling

data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False,  
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    data_collator=data_collator,
    tokenizer=tokenizer,
)


trainer.train()

model.save_pretrained("gemma3-pretrain")
tokenizer.save_pretrained("gemma3-pretrain")

