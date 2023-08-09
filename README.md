# attention-visualizer

### Link: https://attention-visualizer.azurewebsites.net/

## 1. What is this project?

This is a web app that allows the user to visualize the attention between the input and output of an LLM.

Below is a demonstration of how to visualize the attention (by selecting a part of the summary text):

<img width="776" alt="image" src="https://github.com/dimasikson/attention-visualizer/assets/47122797/b07fb447-65a5-41a1-bf36-ea71cfd62fc8">

## 2. How was it done?

### 2.1. Cross-attentions

The LLM is a pre-trained hugging face model, specifically fine-tuned on a summarization task ([pszemraj/long-t5-tglobal-base-16384-book-summary](https://huggingface.co/pszemraj/long-t5-tglobal-base-16384-book-summary)).

The cross-attentions returned by the model are of shape `(O, L, B, H, M, I)`, and we do averaging over dimensions `L`, `B`, `H` and `M` to get the attentions to shape `(O, I)`.

Here is an example of attentions of shape `(O, I)`:

![image](https://github.com/dimasikson/attention-visualizer/assets/47122797/f91b2823-6b74-4c73-a4e1-68e3ecd41278)

Cross-attention dimensions glossary:
  - `O` - the number of tokens in the output sequence
  - `L` - the number of layers in the model
  - `B` - the number of batches (always 1 in our case)
  - `H` - the number of heads in each layer
  - `M` - the number of beams in beam search (for now, always 1)
  - `I` - the number of tokens in the input sequence

### 2.2. API deployment

This model was deployed as a managed endpoint on Azure ML. Check `summarize/README.md` and `summarize/deploy.py` for details.

### 2.3. App deployment

The app was deployed with App Service on Azure. Stack is Flask + vanilla JS/CSS/HTML.
