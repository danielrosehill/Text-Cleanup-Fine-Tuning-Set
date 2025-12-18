The objective of this undertaking is to generate a finetune of an audio multi-modal model (HF task: audio-text to text). 

The dataset contains:

- Audio file  
- ASR (verbatim) transcript 
- A non-fine-tuned but guided transcript from an audio multimodal model (untrained) following a general system prompt for transcript cleanup/redaction 
- A manually created guided transcript to model the desired degree, type and characteristics of the fine-tune