import numpy as np
import torch

from .base import LLMRequestProcessor


class GenerateRequestProcessor(LLMRequestProcessor):
    def __init__(self, config, model):
        super().__init__(config)
        self.model = model
        self.remove_tokens = [
            self.config["BOS"],
            self.config["EOS"],
        ]

    def reduce_cross_attentions(self, cross_attentions):
        """
        Cross-attention dimensions:
          - O, the number of tokens in the output sequence
          - L, the number of layers in the model
          - B, the number of batches (always 1 in our case)
          - H, the number of heads in each layer
          - M, the number of beams in beam search (for now, always 1)
          - I, the number of tokens in the input sequence

        Input:
            cross_attentions: (O, L, B, H, M, I)

        Output:
            cross_attentions: (O, I)
        """

        # iter over O
        token_cross_attentions_list = []
        for token_cross_attentions in cross_attentions:

            # iter over L
            layer_cross_attentions_list = []
            for layer_cross_attentions in token_cross_attentions:

                # (B, H, M, I) -> (H, I)
                layer_cross_attentions = layer_cross_attentions[0, :, 0, :].detach().numpy()

                # append to list
                layer_cross_attentions_list.append(layer_cross_attentions)

            # (L, H, I)
            layer_cross_attentions_list = np.array(layer_cross_attentions_list)

            # append to list
            token_cross_attentions_list.append(layer_cross_attentions_list)

        # (O, L, H, I)
        attentions_array = np.array(token_cross_attentions_list)

        # (O, L, H, I) -> (O, H, I), mean over the layers
        attentions_array = attentions_array.mean(axis=1)

        # (O, H, I) -> (O, I), mean over the heads
        attentions_array = attentions_array.mean(axis=1)

        # (O, I)
        return attentions_array.tolist()

    def process(self, body):
        """
        Input:
            {
                "token_ids": [1, 54, 23, ..., 2]
            }

        Output:
            {
                "token_ids": [1, 54, 23, ..., 2],
                "cross_attentions": [
                    [0.1, 0.2, ..., 0.3],
                    [0.4, 0.5, ..., 0.6],
                    [..., ..., ..., ...],
                    [0.7, 0.8, ..., 0.9]
                ]
            }
        """

        token_ids = body["token_ids"]
        input_token_ids = torch.tensor(token_ids).unsqueeze(0)

        model_output = self.model.generate(
            input_token_ids,
            max_length=512,
            num_beams=1,
            early_stopping=True,
            output_attentions=True,
            output_scores=True,
            return_dict_in_generate=True,
        )

        output_token_ids = model_output.sequences.squeeze(0).tolist()
        cross_attentions = self.reduce_cross_attentions(model_output.cross_attentions)

        # NOTE: remove BOS and EOS tokens
        output_token_ids = [token_id for token_id in output_token_ids if token_id not in self.remove_tokens]

        # NOTE: cross attentions always start with the BOS token
        cross_attentions = cross_attentions[1:]

        return {
            "token_ids": output_token_ids,
            "cross_attentions": cross_attentions
        }
