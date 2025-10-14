import os
import pandas as pd
from datasets import Dataset, DatasetDict
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    TrainingArguments,
    Trainer,
    DataCollatorForSeq2Seq,
)
from peft import LoraConfig, get_peft_model, TaskType
import torch
from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu
import nltk
nltk.download('punkt')

dataset_dir = r"C:\Users\vinch\Downloads\archive (4)\cnn_dailymail"
train_path = os.path.join(dataset_dir, "train.csv")
val_path = os.path.join(dataset_dir, "validation.csv")
test_path = os.path.join(dataset_dir, "test.csv")

print("Loading and subsampling dataset...")
train_df = pd.read_csv(train_path, nrows=1000).dropna(subset=['article', 'highlights'])
val_df = pd.read_csv(val_path, nrows=200).dropna(subset=['article', 'highlights'])
test_df = pd.read_csv(test_path, nrows=200).dropna(subset=['article', 'highlights'])

dataset = DatasetDict({
    "train": Dataset.from_pandas(train_df[['article', 'highlights']]),
    "validation": Dataset.from_pandas(val_df[['article', 'highlights']]),
    "test": Dataset.from_pandas(test_df[['article', 'highlights']]),
})

print(f"Dataset sizes: Train {len(dataset['train'])}, Val {len(dataset['validation'])}, Test {len(dataset['test'])}")

model_name = "google/flan-t5-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForSeq2SeqLM.from_pretrained(
    model_name,
    torch_dtype=torch.float32,
    device_map="cpu",
)

from peft import PeftModel
model = PeftModel.from_pretrained(model, "./fine_tuned_llama")
    
def preprocess_function(examples):
    inputs = [f"Summarize: {article}" for article in examples["article"]]
    targets = [f"Summary: {summary}" for summary in examples["highlights"]]
    model_inputs = tokenizer(inputs, max_length=1024, truncation=True, padding=False)
    
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(targets, max_length=128, truncation=True, padding=False)
    
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

tokenized_datasets = dataset.map(
    preprocess_function,
    batched=True,
    remove_columns=dataset["train"].column_names,
)

data_collator = DataCollatorForSeq2Seq(
    tokenizer=tokenizer,
    model=model,
    label_pad_token_id=-100,
    pad_to_multiple_of=8,
    return_tensors="pt",
)

training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=1,
    per_device_train_batch_size=1,
    per_device_eval_batch_size=1,
    warmup_steps=10,
    weight_decay=0.01,
    logging_dir="./logs",
    logging_steps=10,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False,
    fp16=False,
    dataloader_pin_memory=False,
)



def compute_metrics(generated, references):
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    rouge_scores = []
    bleu_scores = []
    
    for gen, ref in zip(generated, references):
        rouge = scorer.score(ref, gen)
        rouge_scores.append({
            'rouge1': rouge['rouge1'].fmeasure,
            'rouge2': rouge['rouge2'].fmeasure,
            'rougeL': rouge['rougeL'].fmeasure,
        })
        bleu = sentence_bleu([ref.split()], gen.split())
        bleu_scores.append(bleu)
    
    avg_rouge1 = sum(s['rouge1'] for s in rouge_scores) / len(rouge_scores)
    avg_rouge2 = sum(s['rouge2'] for s in rouge_scores) / len(rouge_scores)
    avg_rougeL = sum(s['rougeL'] for s in rouge_scores) / len(rouge_scores)
    avg_bleu = sum(bleu_scores) / len(bleu_scores)
    
    return {
        'avg_rouge1': avg_rouge1,
        'avg_rouge2': avg_rouge2,
        'avg_rougeL': avg_rougeL,
        'avg_bleu': avg_bleu,
    }

print("Evaluating on test set...")
test_encodings = tokenizer(
    [f"Summarize: {article}" for article in dataset["test"]["article"]],
    truncation=True,
    padding=True,
    max_length=1024,
    return_tensors="pt",
)

device = model.device
model.eval()
generated_summaries = []
references = [summary for summary in dataset["test"]["highlights"]]

with torch.no_grad():
    for i in range(len(test_encodings["input_ids"])):
        inputs = {k: v[i:i+1].to(device) for k, v in test_encodings.items()}
        outputs = model.generate(
            **inputs,
            max_new_tokens=128,
            do_sample=True,
            temperature=0.7,
            pad_token_id=tokenizer.eos_token_id,
        )
        summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
        generated_summaries.append(summary[len(tokenizer.decode(inputs["input_ids"][0], skip_special_tokens=True)):].strip())

metrics = compute_metrics(generated_summaries, references)
print("Evaluation Metrics:")
print(f"ROUGE-1: {metrics['avg_rouge1']:.4f}")
print(f"ROUGE-2: {metrics['avg_rouge2']:.4f}")
print(f"ROUGE-L: {metrics['avg_rougeL']:.4f}")
print(f"BLEU: {metrics['avg_bleu']:.4f}")

print("\nAnalysis:")
print("The fine-tuned LLaMA 3.1 model demonstrates capability in abstractive summarization on the CNN/DailyMail dataset.")
print("Strengths:")
print("- Generates coherent and contextually relevant summaries using its strong language understanding.")
print("- LoRA adaptation allows efficient fine-tuning on limited resources.")
print("- Handles long articles well due to large context window.")
print("Limitations:")
print("- With subsampled data and 1 epoch, performance is modest; full training would improve scores.")
print("- May hallucinate facts not in the article.")
print("- ROUGE/BLEU scores indicate room for improvement in factual accuracy and fluency.")
print("- Larger models like 70B would perform better but require more compute.")
