# python inference_vllm.py --model deepseek --data val
# python inference_vllm.py --model codellama --data val --prompt prompts/prompt_v2.md --output inference_output/prompt_v2/codellama_v0
# python inference_vllm.py --model sqlcoder --data val

# python inference_vllm.py --model deepseek --data test
# python inference_vllm.py --model codellama --data test --prompt prompts/prompt_v2.md --output inference_output/prompt_v2/codellama_v0
# python inference_vllm.py --model sqlcoder --data test

# python inference_vllm.py --model deepseek --data train
# python inference_vllm.py --model codellama --data train --prompt prompts/prompt_v2.md --output inference_output/prompt_v2/codellama_v0
# python inference_vllm.py --model sqlcoder --data train


python inference_vllm.py --model codellama --data val --prompt prompts/prompt_v3.md --output inference_output/prompt_v3/codellama_v0
python inference_vllm.py --model codellama --data test --prompt prompts/prompt_v3.md --output inference_output/prompt_v3/codellama_v0
python inference_vllm.py --model codellama --data train --prompt prompts/prompt_v3.md --output inference_output/prompt_v3/codellama_v0
# python inference_vllm.py --model codellama --data eval_train --prompt prompts/prompt_v3.md --output inference_output/prompt_v3/codellama_v0
# python inference_vllm.py --model codellama --data eval_test --prompt prompts/prompt_v3.md --output inference_output/prompt_v3/codellama_v0

# python inference_vllm.py --model codellama --data val --prompt prompts/prompt_v2.md --output inference_output/prompt_v2/codellama_v1 --lora models/codellama-v1
# python inference_vllm.py --model codellama --data test --prompt prompts/prompt_v2.md --output inference_output/prompt_v2/codellama_v1 --lora models/codellama-v1
# python inference_vllm.py --model codellama --data train --prompt prompts/prompt_v2.md --output inference_output/prompt_v2/codellama_v1 --lora models/codellama-v1

python inference_vllm.py --model codellama --data val --prompt prompts/prompt_v3.md --output inference_output/prompt_v3/codellama_v4 --lora models/codellama-v4
python inference_vllm.py --model codellama --data test --prompt prompts/prompt_v3.md --output inference_output/prompt_v3/codellama_v4 --lora models/codellama-v4
python inference_vllm.py --model codellama --data train --prompt prompts/prompt_v3.md --output inference_output/prompt_v3/codellama_v4 --lora models/codellama-v4

python inference_vllm.py --model codellama --data val --prompt prompts/prompt_v3.md --output inference_output/prompt_v3/codellama_v5 --lora models/codellama-v5
python inference_vllm.py --model codellama --data test --prompt prompts/prompt_v3.md --output inference_output/prompt_v3/codellama_v5 --lora models/codellama-v5
python inference_vllm.py --model codellama --data train --prompt prompts/prompt_v3.md --output inference_output/prompt_v3/codellama_v5 --lora models/codellama-v5
python inference_vllm.py --model codellama --data eval_train --prompt prompts/prompt_v3.md --output inference_output/prompt_v3/codellama_v5 --lora models/codellama-v5
python inference_vllm.py --model codellama --data eval_test --prompt prompts/prompt_v3.md --output inference_output/prompt_v3/codellama_v5 --lora models/codellama-v5