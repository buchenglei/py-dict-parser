# -*- coding: utf-8 -*-
import sys
import dict_ldoce, source_reader

def main():
    if len(sys.argv) != 2:
        raise Exception("必须要指定需要解析的单词列表文件")
    
    filepath = sys.argv[1]
    # 加载需要处理的单词列表
    ldoce = dict_ldoce.DictLdoce(source_reader.HTTPReader)
    result = []
    no = 1
    with open(filepath, 'r', encoding='utf-8') as f:
        for word in f:
            word = word.strip('\n')
            result.append(ldoce.word(word))
            print("word.{} '{}' done!".format(no, word))
            no += 1

    with open("./output.txt", 'w', encoding='utf-8') as f:
        for item in result:
            f.write(item)



# 判断当前文件是否是主文件
if __name__ == "__main__":
    main()