from html.parser import HTMLParser

VOID_ELEMENTS = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}

class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID_ELEMENTS:
            self.tags.append((tag, self.getpos()))

    def handle_endtag(self, tag):
        if tag in VOID_ELEMENTS:
            return # skip void elements

        if not self.tags:
            self.errors.append(f"Unexpected closing tag </{tag}> at line {self.getpos()[0]}")
            return
            
        start_tag, pos = self.tags.pop()
        if start_tag != tag:
            self.errors.append(f"Mismatched tag: expected </{start_tag}> (from line {pos[0]}), found </{tag}> at line {self.getpos()[0]}")

def check_html_file():
    parser = MyHTMLParser()
    with open("backend/static/index.html", "r", encoding="utf-8") as f:
        html = f.read()
    
    try:
        parser.feed(html)
        print("Parsing completed.")
        if parser.errors:
            print(f"Found {len(parser.errors)} errors:")
            for err in parser.errors[:20]:
                print(" -", err)
        else:
            print("No HTML tag mismatches found!")
    except Exception as e:
        print("HTML Parsing crashed:", e)

if __name__ == "__main__":
    check_html_file()
