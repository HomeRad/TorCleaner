from wc.parser.htmllib import HtmlPrinter
import sys

def main():
    file = sys.argv[1]
    data = open(file).read()
    p = HtmlPrinter()
    p.feed(data)


if __name__=='__main__':
    main()
