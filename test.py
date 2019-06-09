# -*- coding: utf-8 -*-

import dict_ldoce
import source_reader

ldoce = dict_ldoce.DictLdoce(source_reader.HTTPReader)
print(ldoce.word('wrap'))

