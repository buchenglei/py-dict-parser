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

        """
        解析整个词典
        """
        # 加载单词解释
        dicts = self.domobj("span.dictentry")
        for dict in dicts.items():
            if dict is None:
                continue
            self.__parse_dict_word_base(dict))
            # self.__parse_dict_word_explain(dict)
        
    def __find_word_family(self):
        family = self.domobj('.wordfams')
        if family is None:
            return ""

        return HandleLdoceWordFamily(family).format()

    def __parse_dict_word_base(self, dict_root_dom):
        return HandleLdoceWordBase(dict_root_dom).format()


# 下面的class用于处理词典的每一部分
# 需要使用pyquery的dom对象来初始化
# 把对词典解释的每一部分拆解到不同的class中去
# 通过组合的方式来拼装词典每一部分的数据清洗
# 每个方法统一使用format方法对外, 该方法返回一个渲染好的字符串

class HandleLdoceWordFamily:
    """
    解析该单词的词族信息
    """
    def __init__(self, dom):
        self.word_list = {}
        self.__family_dom = dom

    def __parse(self):
        current_pos = ""
        # 解析wordfamily的dom
        for child in self.__family_dom.children():
            child_classes = child.attrib.get("class")
            if 'pos' in child_classes:
                current_pos = child.text.strip()
                self.word_list[current_pos] = []
            if 'crossRef' in child_classes:
                self.word_list[current_pos].append(child.text)

    def format(self):
        self.__parse()
        # 将解析到的dict格式化成字符串
        template = "Word Family\n"
        for k, v in self.word_list.items():
            template += "{}: {}\n".format(k, ','.join(v))

        return template
        
    
class HandleLdoceWordBase:
    """
    解析该单词的基本信息, 包含该单词关联的topic, 音标,词频和词性
    """
    def __init__(self, dom):
        self.__root_dom = dom

    def __parse(self):
        # 解析音标
        self.proncode = self.__root_dom.find('span.PronCodes').children().text()
        # 解析词频
        self.word_frequency = self.__root_dom.find('span.tooltip').text()
        # 解析词性
        self.word_pos = self.__root_dom.find('span.POS').text()

    def format(self):
        self.__parse()
        # 优化音标的空格
        self.proncode = self.proncode.replace(' ', '')

        return "{} {} {}".format(self.word_pos, self.proncode, self.word_frequency)


class HandleLdoceWordExplain:
    """
    用来解析单词的每一条英文意义, 例句, 词组搭配以及词组的例句
    """
    def __init__(self, dom):
        self.__root_dom = dom

    def format(self):
        pass

    def __parse(self, dict_root_dom):
        explain_doms = dict_root_dom.find('span.Sense')

        explains = []
        for explain_dom in explain_doms.items():

            for explain_item in explain_dom.children().items():
                print(explain_dom.text())

    def __read_explain_sign(self, explain_dom):
        return explain_dom.find('span.SIGNPOST').text()

    def __read_explain_gram(self, explain_dom):
        return explain_dom.find('span.GRAM').text()

    def __read_explain_definition(self, explain_dom):
        return explain_dom.find('span.DEF').text()

    def _read_explain_example(self, example_dom):
        # 处理一级example
        if example_dom.hasClass('EXAMPLE'):
            return example_dom.text()
        
        # 处理短语和例句的组合
        # TODO 暂时不支持
        # parse_examples = []
        # phrase = example_dom.text()
        # phrase_example_dom = example_dom.children().items()
        # if phrase_example_dom is None:
        #     return phrase
        # for parse_example in phrase_example_dom:
        #     parse_examples.append(parse_example.text())

        # return "{}\n\t{}".format(phrase, '\n\t'.join(parse_examples))