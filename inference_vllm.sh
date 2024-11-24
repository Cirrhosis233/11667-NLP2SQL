python inference_vllm.py --model deepseek --data val
python inference_vllm.py --model codellama --data val
python inference_vllm.py --model sqlcoder --data val

python inference_vllm.py --model deepseek --data test
python inference_vllm.py --model codellama --data test
python inference_vllm.py --model sqlcoder --data test

python inference_vllm.py --model deepseek --data train
python inference_vllm.py --model codellama --data train
python inference_vllm.py --model sqlcoder --data train