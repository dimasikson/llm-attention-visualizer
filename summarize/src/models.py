from transformers import LongT5ForConditionalGeneration, AutoTokenizer


model_mapping = {
    "pszemraj/long-t5-tglobal-base-16384-book-summary": {
        "model": LongT5ForConditionalGeneration,
        "tokenizer": AutoTokenizer,
        "config": {
            "BOS": 0,
            "EOS": 1,
            "SPC": '▁'
        }
    }
}
