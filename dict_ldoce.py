# -*- coding: utf-8 -*-

from pyquery import PyQuery as pq

"""
定义Ldoce统一的输出格式

result = {
    word_family: [(), ()],
    dicts: [
        {
            word_base: (词性, 音标, 词频),
            explains: [
                {
                    definition:(单词分类, 动词类型, 英文解释),
                    examples: [
                        "",
                        "", // 最多两个
                    ],
                    usage: [
                        (短语/搭配, 例句),
                        (),
                    ]
                }
            ]
        }
    ]
}

"""

class LdoceTextFomater:
    """
    将上面定义好的返回输出成字符串
    """
    def __init__(self, result):
        self.result = result
        self.indent = '  '
        self.newline = '\n'
        self.twonewline = self.newline * 2
        self.spliter = '\n-----\n'
        self.wordspliter = '\n=====\n'

    def output(self):
        text = ""
        word_fmaily = self.result.get('word_family')
        if len(word_fmaily) > 0 :
            text += "[Word Family]" + self.newline + self.indent
            for word in word_fmaily:
                if len(word) == 2 and word[0] != "" and word[1] != "":
                    text += ':'.join(word) + ';'

        text += self.twonewline
        dicts = self.result.get('dicts')
        if len(dicts) <= 0:
            return text
        
        # 以下是dicts不为空时需要处理的逻辑
        for dict in dicts:
            # 解析word base
            word_base = dict.get('word_base')
            # 过滤掉定义元组中为空的部分
            items = [item for item in word_base if item != ""]
            if len(items) is not 0:
                text += ("[{}]" + self.newline).format(' | '.join(items))
            
            # 解析explains
            explains = dict.get('explains')
            if len(explains) <= 0:
                continue
            for explain in explains:
                if explain is None:
                    continue
                definiton = explain.get('definiton')
                # 过滤掉定义元组中为空的部分
                items = [item for item in definiton if item != ""]
                if len(items) is not 0:
                    text += ("<{}>" + self.twonewline).format(' | '.join(items))

                # 解析例句
                examples = explain.get('examples')
                if len(examples) > 0 :
                    text += self.newline.join(["* {}".format(item) for item in examples if item != ""])
                    text += self.newline

                # 解析用法
                usages = explain.get('usage')
                if len(usages) > 0 :
                    for usage in usages:
                        if usage[0] != "":
                            text += "#" + usage[0] + "#" + self.newline
                        else:
                            continue
                        if usage[1] != "":
                            text += self.indent + '-' + usage[1] + self.newline

                text += self.twonewline

        

        return text


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
        self.result = {}

    def __read_source_text(self, url):
        reader = self.readerClass(url)
        self.source_text = reader.get_page_source()
        self.domobj = pq(self.source_text)

    def word(self, word):
        # 解析网页源码
        self.__read_source_text(self.ldoce_url_base.format(word))

        # 解析词族
        word_family = self.__find_word_family()
        if len(word_family) is not 0:
            self.result['word_family'] = word_family

        # 加载单词解释
        dicts = self.domobj("span.dictentry")
        self.result['dicts'] = []
        for dict in dicts.items():
            inner_dict = {}
            if dict is None:
                continue
            if dict.find('span.dictionary_intro').text() == 'From Longman Business Dictionary':
                continue
            inner_dict['word_base'] = self.__parse_dict_word_base(dict)
            inner_dict['explains'] = self.__parse_dict_word_explains(dict)
            self.result['dicts'].append(inner_dict)

        return LdoceTextFomater(self.result).output()

    def __find_word_family(self):
        family=self.domobj('.wordfams')
        if family is None:
            return ""

        return LdoceWordFamilyHandler(family).format()

    def __parse_dict_word_base(self, dict_dom):
        return LdoceWordBaseHandler(dict_dom).format()

    def __parse_dict_word_explains(self, dict_dom):
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
        for child_dom in self.__family_dom.children().items():
            if child_dom.hasClass('pos'):
                current_pos=child_dom.text().strip()
                self.word_list[current_pos]=[]
            if child_dom.hasClass('crossRef'):
                self.word_list[current_pos].append(child_dom.text())

    def format(self):
        """
        将词族解析成这种格式:
        [('(noun)', 'servant,serve,server,service,disservice,serving,servery,servicing,servility,servitude'), ('(adjective)', 'serviceable,servile,serving'), ('(verb)', 'service')]
        """
        self.__parse()
        result = []
        # 将解析到的dict格式化成字符串
        for k, v in self.word_list.items():
            if k == '' or len(v) == 0:
                continue
            result.append((k,','.join(v)))

        return result


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

        result = (self.word_pos, self.proncode, self.word_frequency)

        return result
   

class LdoceWordExplainHandler:
    """
    用来解析单词的每一条英文意义, 例句, 词组搭配以及词组的例句
    """
    def __init__(self, dom):
        self.__root_dom=dom
        self.explains = []

    def format(self):
        self.__parse()

        return self.explains

    def __parse(self):
        # 每一个Sense都是一种词性的详解
        sense_doms=self.__root_dom.find('span.Sense')

        for sense_dom in sense_doms.items():
            self.explains.append(self.__parse_sense_dom(sense_dom))
            

    def __parse_sense_dom(self, sense_dom):
        explain = {}
        explain['definiton'] = self.__read_sense_definition(sense_dom)

        explain['examples'] = []
        explain['usage'] = []
        for sense_item in sense_dom.children().items():
            if sense_item.hasClass('EXAMPLE'):
                # 最多取两条例句
                if len(explain['examples']) > 2:
                    continue
                explain['examples'].append(self.__read_sense_example(sense_item))
            if sense_item.hasClass('GramExa'):
                explain['usage'].append(self.__parse_sense_gramexa(sense_item))
            if sense_item.hasClass('ColloExa'):
                 explain['usage'].append(self.__parse_sense_colloexa(sense_item))

        self.explains.append(explain)
                
    def __read_sense_definition(self, sense_dom):
        return (
            # 单词分类
            sense_dom.find('span.SIGNPOST').text(),
            # 单词语法, 比如动词是及物动词还是不及物动词
            sense_dom.find('span.GRAM').text(),
            # 这个单词的详细的英文解释
            sense_dom.find('span.DEF').text()
        )

    def __read_sense_example(self, example_dom):
        return example_dom.text()

    def __parse_sense_gramexa(self, gramexa_dom):
        propform = gramexa_dom.find('span.PROPFORM').text()
        if propform == '':
            propform = gramexa_dom.find('span.PROPFORMPREP').text()
        example = gramexa_dom.find('span.EXAMPLE').text()
        return (propform, example)

    def __parse_sense_colloexa(self, colloexa_dom):
        collo = colloexa_dom.find('span.COLLO').text()
        example = colloexa_dom.find('span.EXAMPLE').text()
        return (collo, example)