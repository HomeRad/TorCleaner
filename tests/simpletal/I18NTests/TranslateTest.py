# -*- coding: iso-8859-1 -*-
"""unit test for parsing all supported i18n: constructs"""
import unittest, os
import StringIO
import logging, logging.config

from wc.webgui.simpletal import simpleTAL, simpleTALES

class Translator (object):
    """dummy Translations object - see the gettext module"""
    def __init__ (self, dict):
        self.dict = dict

    def gettext (self, msg):
        return self.dict.get(msg, msg)


class TranslateTests (unittest.TestCase):

    def setUp (self):
        self.context = simpleTALES.Context()
        self.context.addGlobal(u'hello', u'Hello')
        self.context.addGlobal(u'name', u'Basti')
        self.dict = {
            u'Hello': u'Ola, amigo',
            u'Hello, %(name)s!': u'Ola, %(name)s!',
            u'Uzgur': u'Gänsefleisch',
            u'Üzgür': u'Gansefleisch',
            u'Üzgürü': u'Gänsefleisch',
        }
        self.translator = Translator(self.dict)

    def _runTest_ (self, txt, result, errMsg="Error", encoding="ISO-8859-1"):
        result = result.encode(encoding)
        txt = txt.encode(encoding)
        template = simpleTAL.compileHTMLTemplate (txt)
        file = StringIO.StringIO ()
        template.expand(self.context, file, outputEncoding=encoding,
                        translator=self.translator)
        realResult = file.getvalue()
        res = (errMsg, txt, realResult, result, template)
        self.failUnless((realResult == result), "%s - \npassed in: %s \ngot back %s \nexpected %s\n\nTemplate: %s" % res)

    def testContentTranslate (self):
        """test content translation"""
        key = u'Hello'
        self._runTest_ ('<html i18n:translate="">%s</html>'%key,
                        '<html>%s</html>'%self.dict[key],
                        'Content translate failed.')

    def testStringTranslate (self):
        """test string translation"""
        key = u'Hello'
        self._runTest_ ('<html i18n:translate="string:%s">error</html>'%key,
                        '<html>%s</html>'%self.dict[key],
                        'String translate failed.')

    def testTalContentTranslate (self):
        """test translation of tal:content"""
        key = u'Hello'
        self._runTest_ ('<html i18n:translate="" tal:content="hello">error</html>',
                        '<html>%s</html>'%self.dict[key],
                        'Tal Content translate failed.')

    def testTalReplaceTranslate (self):
        """test translation of tal:replace"""
        key = u'Hello'
        self._runTest_ ('<html i18n:translate="" tal:replace="hello">error</html>',
                        self.dict[key],
                        'Tal Replace translate failed.')

    def testKeywordExpansion (self):
        """test %() keyword expansion"""
        key = u"Hello, %(name)s!"
        val = self.dict[key] % self.context.getVariableMap()
        self._runTest_ ('<html i18n:translate="">%s</html>'%key,
                        '<html>%s</html>'%val,
                        'Keyword expansion failed.')

    def testAttributeStringTranslate (self):
        """test translation of an attribute string"""
        key = u'Hello'
        self._runTest_ ('<html i18n:attributes="alt string:%s">.</html>'%key,
                        '<html alt="%s">.</html>'%self.dict[key],
                        'Attribute String translate failed.')

    def testAttributeContentTranslate (self):
        """test translation of an attribute var"""
        key = u'Hello'
        self._runTest_ ('<html i18n:attributes="value hello" value="error">.</html>',
                        '<html value="%s">.</html>'%self.dict[key],
                        'Attribute Content translate failed.')

    def testAttributeTranslate (self):
        """test translation of all attributes"""
        key = u'Hello'
        self._runTest_ ('<html alt="%s" title="%s" i18n:attributes="">.</html>'%(key, key),
                        '<html alt="%s" title="%s">.</html>'%(self.dict[key],self.dict[key]),
                        'All attribute translate failed.')

    def testDictValEncoding (self):
        """test non-Ascii char in dict value"""
        key = u'Uzgur'
        self._runTest_ ('<html i18n:translate="">%s</html>'%key,
                        '<html>%s</html>'%self.dict[key],
                        'Non-Ascii character in dict value failed.')

    def testDictKeyEncoding (self):
        """test non-Ascii char in dict key"""
        key = u'Üzgür'
        self._runTest_ ('<html i18n:translate="">%s</html>'%key,
                        '<html>%s</html>'%self.dict[key],
                        'Non-Ascii character in dict key failed.')

    def testDictKeyValEncoding (self):
        """test non-Ascii char in dict key and value"""
        key = u'Üzgürü'
        self._runTest_ ('<html i18n:translate="">%s</html>'%key,
                        '<html>%s</html>'%self.dict[key],
                        'Non-Ascii character in dict key and value failed.')

if __name__ == '__main__':
    unittest.main()

