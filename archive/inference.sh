python inference.py --model deepseek --data val --batch_size 8
python inference.py --model codellama --data val --batch_size 8
python inference.py --model sqlcoder --data val --batch_size 18

python inference.py --model deepseek --data test --batch_size 8
python inference.py --model codellama --data test --batch_size 8
python inference.py --model sqlcoder --data test --batch_size 18

python inference.py --model deepseek --data train --batch_size 8
python inference.py --model codellama --data train --batch_size 8
python inference.py --model sqlcoder --data train --batch_size 18