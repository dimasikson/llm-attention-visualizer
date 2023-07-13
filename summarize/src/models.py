from transformers import LongT5ForConditionalGeneration, AutoTokenizer


model_mapping = {
    "pszemraj/long-t5-tglobal-base-16384-book-summary": {
        "model": LongT5ForConditionalGeneration,
        "tokenizer": AutoTokenizer,
        "config": {
            "token_start": 0,
            "token_end": 1,
            "token_unknown": 2,
            "space_character": '▁'
        }
    }
}
