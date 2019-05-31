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

    def __read_source_text(self, url):
        reader = self.readerClass(url)
        self.source_text = reader.get_page_source()
        self.domobj = pq(self.source_text)

    def word(self, word):
        # 解析网页源码
        self.__read_source_text(self.ldoce_url_base.format(word))

        # 解析词族
        self.__find_word_family()

        # 加载单词解释
        dicts = self.domobj("span.dictentry")
        for dict in dicts.items():
            if dict is None:
                continue
            if dict.find('span.dictionary_intro').text() == 'From Longman Business Dictionary':
                continue
            self.__parse_dict_word_base(dict)
            self.__parse_dict_word_explain(dict)

    def __find_word_family(self):
        family=self.domobj('.wordfams')
        if family is None:
            return ""

        return LdoceWordFamilyHandler(family).format()

    def __parse_dict_word_base(self, dict_dom):
        return LdoceWordBaseHandler(dict_dom).format()

    def __parse_dict_word_explain(self, dict_dom):
        return LdoceWordExplainHandler(dict_dom).format()


# 下面的class用于处理词典的每一部分
# 需要使用pyquery的dom对象来初始化
# 把对词典解释的每一部分拆解到不同的class中去
# 通过组合的方式来拼装词典每一部分的数据清洗
# 每个方法统一使用format方法对外, 该方法返回一个渲染好的字符串

class LdoceWordFamilyHandler:
    """
    解析该单词的词族信息
    """
    def __init__(self, dom):
        self.word_list={}
        self.__family_dom=dom

    def __parse(self):
        current_pos=""
        # 解析wordfamily的dom
        for child in self.__family_dom.children():
            child_classes=child.attrib.get("class")
            if 'pos' in child_classes:
                current_pos=child.text.strip()
                self.word_list[current_pos]=[]
            if 'crossRef' in child_classes:
                self.word_list[current_pos].append(child.text)

    def format(self):
        self.__parse()
        # 将解析到的dict格式化成字符串
        template="Word Family\n"
        for k, v in self.word_list.items():
            template += "{}: {}\n".format(k, ','.join(v))

        return template


class LdoceWordBaseHandler:
    """
    解析该单词的基本信息, 包含该单词关联的topic, 音标,词频和词性
    """
    def __init__(self, dom):
        self.__root_dom=dom

    def __parse(self):
        # 解析音标
        self.proncode=self.__root_dom.find('span.PronCodes').children().text()
        # 解析词频
        self.word_frequency=self.__root_dom.find('span.tooltip').text()
        # 解析词性
        self.word_pos=self.__root_dom.find('span.POS').text()

    def format(self):
        self.__parse()
        # 优化音标的空格
        self.proncode=self.proncode.replace(' ', '')

        return "{} {} {}".format(self.word_pos, self.proncode, self.word_frequency)


class LdoceWordExplainHandler:
    """
    用来解析单词的每一条英文意义, 例句, 词组搭配以及词组的例句
    """
    def __init__(self, dom):
        self.__root_dom=dom
        self.dicts = []

    def format(self):
        self.__parse()

    def __parse(self):
        # 每一个Sense都是一种词性的详解
        sense_doms=self.__root_dom.find('span.Sense')

        for sense_dom in sense_doms.items():
            self.__parse_sense_dom(sense_dom)
            

    def __parse_sense_dom(self, sense_dom):
        print(self.__read_sense_definition(sense_dom))
        for sense_item in sense_dom.children().items():
            if sense_item.hasClass('EXAMPLE'):
                self.__read_sense_example(sense_item)
            if sense_item.hasClass('GramExa'):
                self.__parse_sense_gramexa(sense_item)
            if sense_item.hasClass('ColloExa'):
                self.__parse_sense_colloexa(sense_item)
            
                
    def __read_sense_definition(self, sense_dom):
        return [
            sense_dom.find('span.SIGNPOST').text(),
            sense_dom.find('span.GRAM').text(),
            sense_dom.find('span.DEF').text()
        ]

    def __read_sense_example(self, example_dom):
        return example_dom.text()

    def __parse_sense_gramexa(self, gramexa_dom):
        propform = gramexa_dom.find('span.PROPFORM').text()
        if propform == '':
            propform = gramexa_dom.find('span.PROPFORMPREP').text()
        example = gramexa_dom.find('span.EXAMPLE').text()
        return [propform, example]

    def __parse_sense_colloexa(self, colloexa_dom):
        collo = colloexa_dom.find('span.COLLO').text()
        example = colloexa_dom.find('span.EXAMPLE').text()
        return [collo, example]