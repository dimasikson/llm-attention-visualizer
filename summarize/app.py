import json

from src.tokenize import EncodeRequestProcessor, DecodeRequestProcessor
from src.generate import GenerateRequestProcessor
from src.models import model_mapping


HUGGING_FACE_PATH = "pszemraj/long-t5-tglobal-base-16384-book-summary"


def init():
    """
    This is a standard method for Azure ML endpoints.
    It is called once when the endpoint is initialized.
    """

    global model
    global tokenizer
    global config
    global encoder
    global decoder
    global generator

    model = model_mapping[HUGGING_FACE_PATH]["model"].from_pretrained(HUGGING_FACE_PATH)
    tokenizer = model_mapping[HUGGING_FACE_PATH]["tokenizer"].from_pretrained(HUGGING_FACE_PATH)
    config = model_mapping[HUGGING_FACE_PATH]["config"]

    encoder = EncodeRequestProcessor(config, tokenizer)
    decoder = DecodeRequestProcessor(config, tokenizer)
    generator = GenerateRequestProcessor(config, model)


def run(data):
    """
    This is a standard method for Azure ML endpoints.
    It is called once for every request to the endpoint.

    URL: /score (POST)

    Input `data`
        {
            "name": "encode",
            "body": {
                ...
            }
        }

    Output `res`
        {
            ...
        }
    """

    # Azure ML endpoints send JSON input
    data_dict = json.loads(data)

    # The request name is used to determine which processor to use
    request_name = data_dict["name"]
    request_body = data_dict["body"]
    
    # Run the request processor
    res = _run(request_body, request_name)

    # Azure ML endpoints require JSON output
    return json.dumps(res)


def _run(body, name):
    if name == "encode":
        return encoder.process(body)

    if name == "decode":
        return decoder.process(body)

    if name == "generate":
        return generator.process(body)

    return {"error": "Invalid request name"}
