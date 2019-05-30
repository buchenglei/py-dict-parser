# -*- coding: utf-8 -*-

from pyquery import PyQuery as pq


class DictLdoce:
    """
    解析朗文词典页面
    """

    def __init__(self, readerClass):
        """
        初始化解析朗文词典页面的
        """
        self.readerClass = readerClass
        self.ldoce_url_base = "https://www.ldoceonline.com/dictionary/{}"
        self.source_text = ""
        self.template = {
            "word_title": {}
        }

    def parse_word(self, word):
        # 解析网页源码
        self.__read_source_text(self.ldoce_url_base.format(word))
        return self.__parse_dictionary()

    def __read_source_text(self, url):
        reader = self.readerClass(url)
        self.source_text = reader.get_page_source()
        self.domobj = pq(self.source_text)

    def __parse_dictionary(self):
        """
        解析整个词典
        """
        self.__find_word_family()
        # 加载单词解释
        dicts = self.domobj("span.dictentry")
        for dict in dicts.items():
            if dict is None:
                continue
            self.__parse_dict_word_base(dict.children())
            # print(dict_content)

    def __find_word_family(self):
        family = self.domobj('.wordfams')
        if family is None:
            return ""

        word_list = {}
        current_pos = ""
        # 解析wordfamily的dom
        for child in family.children():
            child_classes = child.attrib.get("class")
            if 'pos' in child_classes:
                current_pos = child.text.strip()
                word_list[current_pos] = []
            if 'crossRef' in child_classes:
                word_list[current_pos].append(child.text)

        # 将解析到的dict格式化成字符串
        template = "Word Family\n"
        for k, v in word_list.items():
            template += "{}: {}\n".format(k, ','.join(v))

        return template

    def __parse_dict_word_base(self, dom):
        """
        解析单词的基础部分,比如音标词性,词频
        """
        # 解析音标
        print(dom.contents())
        dom_proncodes = dom.filter('.PronCodes')
        print(dom_proncodes.contents())



    def __parse_dict_word_explain(slef):
        pass



