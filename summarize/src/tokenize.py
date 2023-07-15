from .base import LLMRequestProcessor
from .helpers import map_substring_indices, find_sentences


class EncodeRequestProcessor(LLMRequestProcessor):
    def __init__(self, config, tokenizer):
        super().__init__(config)
        self.tokenizer = tokenizer

    def process(self, body):
        """
        Input:
            {
                "text": "This is a sentence"
            }

        Output:
            {
                "token_ids": [1, 54, 23, ..., 2],
                "token_mapping": [[0, 4], [5, 7], [8, 9], [10, 18]],
                "sentence_mapping": [[0, 19], [20, 39]]
            }
        """

        text = body["text"]

        # encode text into a list of token id's
        token_ids = self.tokenizer.encode(text, return_tensors="pt").squeeze(0).tolist()

        # split text into tokens in text form
        token_text_list = [self.tokenizer.decode(token_id) for token_id in token_ids]

        # map token id's to their corresponding indices in the original text
        token_mapping = map_substring_indices(text, token_text_list)
        sentence_mapping = map_substring_indices(text, find_sentences(text))

        return {
            "token_ids": token_ids,
            "token_mapping": token_mapping,
            "sentence_mapping": sentence_mapping
        }


class DecodeRequestProcessor(LLMRequestProcessor):
    def __init__(self, config, tokenizer):
        super().__init__(config)
        self.tokenizer = tokenizer
        self.space_char = self.config["SPC"]

    def process(self, body):
        """
        Input:
            {
                "token_ids": [1, 54, 23, ..., 2]
            }
        
        Output:
            {
                "text": "This is a sentence",
                "token_mapping": [[0, 4], [5, 7], [8, 9], [10, 18]],
                "sentence_mapping": [[0, 19], [20, 39]]
            }
        """

        token_ids = body["token_ids"]

        # split text into tokens in text form
        token_text_list = self.tokenizer.convert_ids_to_tokens(token_ids)

        # join tokens into a single string
        token_text = "".join(token_text_list).replace(self.space_char, " ").strip()

        # remove special tokens
        token_text_list = [s.replace(self.space_char, "") for s in token_text_list]

        # map token id's to their corresponding indices in the final text
        token_mapping = map_substring_indices(token_text, token_text_list)
        sentence_mapping = map_substring_indices(token_text, find_sentences(token_text))

        return {
            "text": token_text,
            "token_mapping": token_mapping,
            "sentence_mapping": sentence_mapping
        }
