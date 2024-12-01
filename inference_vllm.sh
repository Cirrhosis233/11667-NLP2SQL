# python inference_vllm.py --model codellama --data val --prompt prompts/prompt_v4.md --output inference_output/prompt_v4/codellama_v0
# python inference_vllm.py --model codellama --data test --prompt prompts/prompt_v4.md --output inference_output/prompt_v4/codellama_v0

# python inference_vllm.py --model sqlcoder --data val --prompt prompts/prompt_v4.md --output inference_output/prompt_v4/sqlcoder_v0
# python inference_vllm.py --model sqlcoder --data test --prompt prompts/prompt_v4.md --output inference_output/prompt_v4/sqlcoder_v0

# python inference_vllm.py --model deepseek --data val --prompt prompts/prompt_v4.md --output inference_output/prompt_v4/deepseek_v0
# python inference_vllm.py --model deepseek --data test --prompt prompts/prompt_v4.md --output inference_output/prompt_v4/deepseek_v0

# python inference_vllm.py --model codellama --data eval_train --prompt prompts/prompt_v4_postgres.md --output inference_output/prompt_v4/codellama_v0
# python inference_vllm.py --model codellama --data eval_test --prompt prompts/prompt_v4_postgres.md --output inference_output/prompt_v4/codellama_v0

# python inference_vllm.py --model sqlcoder --data eval_train --prompt prompts/prompt_v4_postgres.md --output inference_output/prompt_v4/sqlcoder_v0
# python inference_vllm.py --model sqlcoder --data eval_test --prompt prompts/prompt_v4_postgres.md --output inference_output/prompt_v4/sqlcoder_v0

# python inference_vllm.py --model deepseek --data eval_train --prompt prompts/prompt_v4_postgres.md --output inference_output/prompt_v4/deepseek_v0
# python inference_vllm.py --model deepseek --data eval_test --prompt prompts/prompt_v4_postgres.md --output inference_output/prompt_v4/deepseek_v0

python inference_vllm.py --model codellama --data val --prompt prompts/prompt_v4.md --output inference_output/prompt_v4/codellama_v8 --lora models/codellama-v8
python inference_vllm.py --model codellama --data val --prompt prompts/prompt_v4.md --output inference_output/prompt_v4/codellama_v8.1 --lora models/codellama-v8.1
python inference_vllm.py --model codellama --data val --prompt prompts/prompt_v4.md --output inference_output/prompt_v4/codellama_v8.2 --lora models/codellama-v8.2

python inference_vllm.py --model codellama --data test --prompt prompts/prompt_v4.md --output inference_output/prompt_v4/codellama_v8 --lora models/codellama-v8
python inference_vllm.py --model codellama --data test --prompt prompts/prompt_v4.md --output inference_output/prompt_v4/codellama_v8.1 --lora models/codellama-v8.1
python inference_vllm.py --model codellama --data test --prompt prompts/prompt_v4.md --output inference_output/prompt_v4/codellama_v8.2 --lora models/codellama-v8.2

python inference_vllm.py --model codellama --data eval_train --prompt prompts/prompt_v4_postgres.md --output inference_output/prompt_v4/codellama_v8 --lora models/codellama-v8
python inference_vllm.py --model codellama --data eval_train --prompt prompts/prompt_v4_postgres.md --output inference_output/prompt_v4/codellama_v8.1 --lora models/codellama-v8.1
python inference_vllm.py --model codellama --data eval_train --prompt prompts/prompt_v4_postgres.md --output inference_output/prompt_v4/codellama_v8.2 --lora models/codellama-v8.2

python inference_vllm.py --model codellama --data eval_test --prompt prompts/prompt_v4_postgres.md --output inference_output/prompt_v4/codellama_v8 --lora models/codellama-v8
python inference_vllm.py --model codellama --data eval_test --prompt prompts/prompt_v4_postgres.md --output inference_output/prompt_v4/codellama_v8.1 --lora models/codellama-v8.1
python inference_vllm.py --model codellama --data eval_test --prompt prompts/prompt_v4_postgres.md --output inference_output/prompt_v4/codellama_v8.2 --lora models/codellama-v8.2

python inference_vllm.py --model deepseek --data val --prompt prompts/prompt_v4.md --output inference_output/prompt_v4/deepseek_v1 --lora models/deepseek-v1
python inference_vllm.py --model deepseek --data test --prompt prompts/prompt_v4.md --output inference_output/prompt_v4/deepseek_v1 --lora models/deepseek-v1

python inference_vllm.py --model deepseek --data eval_train --prompt prompts/prompt_v4_postgres.md --output inference_output/prompt_v4/deepseek_v1 --lora models/deepseek-v1
python inference_vllm.py --model deepseek --data eval_test --prompt prompts/prompt_v4_postgres.md --output inference_output/prompt_v4/deepseek_v1 --lora models/deepseek-v1

python inference_vllm.py --model sqlcoder --data val --prompt prompts/prompt_v4.md --output inference_output/prompt_v4/sqlcoder_v1 --lora models/sqlcoder-v1
python inference_vllm.py --model sqlcoder --data test --prompt prompts/prompt_v4.md --output inference_output/prompt_v4/sqlcoder_v1 --lora models/sqlcoder-v1

python inference_vllm.py --model sqlcoder --data eval_train --prompt prompts/prompt_v4_postgres.md --output inference_output/prompt_v4/sqlcoder_v1 --lora models/sqlcoder-v1
python inference_vllm.py --model sqlcoder --data eval_test --prompt prompts/prompt_v4_postgres.md --output inference_output/prompt_v4/sqlcoder_v1 --lora models/sqlcoder-v1
