
folder=aws_oregon_t3

for i in {1..2}
do
	python -u thug.py --config configs/${folder}/cpu${i}.json &> logs/${folder}/cpu${i}.txt &
	sleep 3
done

