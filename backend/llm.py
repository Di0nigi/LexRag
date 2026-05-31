import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel

#tok: 

#print(tokenizer.decode(output[0], skip_special_tokens=True))

retrieved = ["ALDISERT, Circuit Judge. may not serve as a legitimate substitute for positive evidence. Moreover, the statement that “[t]hey did have a rent-concession policy that they used under certain conditions, if it was in order . . . .”, ibid, at 423a, is no more supportive of the district court’s conclusion than Wiggins’ testimony. The district court erred in assuming a conclusion, contrary to the evidence adduced at trial, to support its legal determination of an illicit group boycott. Score: 1.4775","GROOMS, District Judge: person may not be considered as evidence in the case against any person who was not present and heard the statement made, or saw the act done.” . “[T]hey [the exhibits] are only to be considered for the purpose of testing the veracity of the testimony of the various witnesses. “They shall not be considered for the truth of their contents. For example, the letters should not be considered as evidence of the truth of any statements made therein. They can be considered only for the limited purposes. Score: 0.1931"]

query = "explain evidences"

def generateResponse(model,tokenizer,query, retrieved):

    prompt = f"""
        ### Instruction:
        You are a system that answers questions using the provided documents.

        Rules:
        Use ONLY the provided documents to answer the question.

        Rules:
        - Use ONLY the information inside the documents.
        - If the documents do not contain the answer, say: "The documents do not contain enough information."
        - Do not use outside knowledge WITHOUT specifying that you are.
        - Do NOT guess or infer missing facts.
        - Prefer quoting or closely paraphrasing the documents.

        ### Documents:
        {retrieved}

        ### Question:
        {query}

        ### Answer:
        """

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=400,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
        )

    response = tokenizer.decode(output[0], skip_special_tokens=True)


    return response

def loadModel2B():

    model_name = "Qwen/Qwen2.5-3B-Instruct"

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
        trust_remote_code=True,
        token="",
    )

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        quantization_config=bnb_config,
        torch_dtype=torch.bfloat16,
        trust_remote_code=True,
        token="",
    )

    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        padding_side="right",
        trust_remote_code=True,
        token="",
    )

    tokenizer.pad_token = tokenizer.eos_token

    model.eval()

    return model, tokenizer



def loadModel4B():

    model_name = "google/gemma-3-4b-it"

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
        trust_remote_code=True,
        token="",
    )

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        quantization_config=bnb_config,
        torch_dtype=torch.bfloat16,
        trust_remote_code=True,
        token="",
    )

    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        padding_side="right",
        trust_remote_code=True,
        token="",
    )

    tokenizer.pad_token = tokenizer.eos_token

    model.eval()

    return model, tokenizer    

def loadModel4BF():
    
    model_name = "google/gemma-3-4b-it"
    adapter_path = "/files/gemma3-pretrain"

    # same quantization config you trained with
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
        trust_remote_code=True,
        token="",
    )

    # load base model
    base_model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        quantization_config=bnb_config,
        torch_dtype=torch.bfloat16,
        trust_remote_code=True,
        token="",
    )

    tokenizer = AutoTokenizer.from_pretrained(model_name,trust_remote_code=True,padding_side="right",token="",)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # load LoRA adapter
    model = PeftModel.from_pretrained(base_model, adapter_path)

    model.eval()
    return model, tokenizer



# mod,tok =loadModel()

# resp = generateResponse(mod,tok,query,retrieved)

# print(resp)