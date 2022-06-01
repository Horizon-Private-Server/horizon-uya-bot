import itertools
import sys

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

def read_lines(file:str):
    data = []
    with open(file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data.append(line[39:])
    return data

file1 = read_lines('log1.txt')
file2 = read_lines('log2.txt')

file1_printlines = []
file2_printlines = []

for line_num in range(len(file1)):

    f1_line = file1[line_num]
    f2_line = file2[line_num]

    f1_print = ''
    f2_print = ''

    f1_split = f1_line.split()
    f2_split = f2_line.split()

    if len(f1_split) != len(f2_split):
        print(f"Line:\n{f1_line}\n\n does not match\n\n{f2_line}\n")
        sys.exit()

    for word_num in range(len(f1_split)):
        f1_word = f1_split[word_num]
        f2_word = f2_split[word_num]

        if len(f1_word) != len(f2_word):
            f1_print += f"{bcolors.WARNING}{f1_word}{bcolors.ENDC} "
            f2_print += f"{bcolors.WARNING}{f2_word}{bcolors.ENDC} "
        else:
            f1_word_buf = ''
            f2_word_buf = ''
            for letter_num in range(len(f1_word)):
                if f1_word[letter_num] == f2_word[letter_num]:
                    f1_word_buf += f1_word[letter_num]
                    f2_word_buf += f2_word[letter_num]
                else:
                    f1_word_buf += f"{bcolors.WARNING}{f1_word[letter_num]}{bcolors.ENDC}"
                    f2_word_buf += f"{bcolors.WARNING}{f2_word[letter_num]}{bcolors.ENDC}"

            f1_print += f1_word_buf + ' '
            f2_print += f2_word_buf + ' '

    if f1_print != '':
        file1_printlines.append(f1_print)
    if f2_print != '':
        file2_printlines.append(f2_print)

for l in file1_printlines:
    print(l)

print()
print("==========================")
print()

for l in file2_printlines:
    print(l)

# print("==" * MAX_CHAR_PER_LINE)
#
# for i in range(len(data1)):
#     if i % MAX_CHAR_PER_LINE == 0:
#         print()
#     if i in idx_diff:
#         print(f"{bcolors.WARNING}{data1[i]}{bcolors.ENDC}",end='')
#     else:
#         print(data1[i], end='')
#
# print()
