import itertools

MAX_CHAR_PER_LINE = 75

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


data = []
with open('testing.txt', 'r') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        data.append(line)

def print_diff(data1, data2):


    data1 = [data1[i:i+2] for i in range(0,len(data1),2)]     
    data2 = [data2[i:i+2] for i in range(0,len(data2),2)]     


    idx_diff = set()
    for i in range(len(data1)):
        if data1[i] != data2[i]:
            idx_diff.add(i)

    if len(idx_diff) == 0:
        return

    print("==" * MAX_CHAR_PER_LINE)

    for i in range(len(data1)):
        if i % MAX_CHAR_PER_LINE == 0:
            print()
        if i in idx_diff:
            print(f"{bcolors.WARNING}{data1[i]}{bcolors.ENDC}",end='')
        else:
            print(data1[i], end='')

    print()

    for i in range(len(data2)):
        if i % MAX_CHAR_PER_LINE == 0:
            print()
        if i in idx_diff:
            print(f"{bcolors.WARNING}{data2[i]}{bcolors.ENDC}",end='')
        else:
            print(data2[i], end='')

    print()
    print()
    print("==" * MAX_CHAR_PER_LINE)

 
for data1, data2 in list(itertools.combinations(list(set(data)), 2)):
    print_diff(data1, data2)
    
