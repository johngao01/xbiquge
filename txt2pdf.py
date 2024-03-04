import os
import typing
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Flowable, Paragraph
from reportlab.platypus import PageBreak
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('Microsoft-YaHei', 'chinese.msyh.ttf'))


# https://stackoverflow.com/questions/77680905/python-reportlab-table-of-contents-page-numbering-problem
def add_page_number(canvas, doc):
    """
    Add the page number
    """
    page_num = canvas.getPageNumber()
    text = "- %s -" % page_num
    canvas.drawRightString(4.5 * inch, 0.5 * inch, text)


stylesheet = {
    'default': ParagraphStyle(
        'default',
        fontName='Microsoft-YaHei',
        fontSize=12,
        leading=14,
        textColor=colors.black,
        firstLineIndent=27,
        spaceAfter=12,
    ),
    'bookmark': ParagraphStyle(
        'Heading1',
        fontName='Microsoft-YaHei',
        fontSize=15,
        textColor=colors.blue,
        spaceAfter=35,
    ),
}


# https://stackoverflow.com/questions/73373464/reportlab-smartest-way-to-position-page-with-bookmarkpage
class SmartParagraph(Paragraph):
    def __init__(self, text, *args, **kwds):
        """This paragraph remembers its position on the canvas"""
        super(SmartParagraph, self).__init__(text, *args, **kwds)
        self._pos: typing.Tuple[int, int] = None

    def draw(self):
        super(SmartParagraph, self).draw()
        self._pos = self.canv.absolutePosition(0, 0)

    def get_pos(self) -> typing.Tuple[int, int]:
        return self._pos


class CustomDocTemplate(SimpleDocTemplate):
    def __init__(self, filename, outline_levels: int = 4, **kwargs):
        super(CustomDocTemplate, self).__init__(filename, **kwargs)
        self._bookmark_keys = list()

        if not isinstance(outline_levels, int) and outline_levels < 1:
            raise ValueError("Outline levels must be integer and at least 1")
        self._outline_levels = {f'Heading{level + 1}': level for level in range(outline_levels)}
        # Map of kind:      Heading1 -> 0
        # Heading 1 is level 0, I dont make the rules

    def afterFlowable(self, flowable: Flowable):
        """Registers TOC entries."""
        if isinstance(flowable, Paragraph):
            flowable: Paragraph
            text = flowable.getPlainText()
            style = flowable.style.name

            if style in self._outline_levels:
                level = self._outline_levels[style]
            else:
                return

            if text not in self._bookmark_keys:
                key = text
                self._bookmark_keys.append(key)
            else:
                # There might headings with identical text, yet they need a different key
                # Keys are stored in a list and incremented if a duplicate is found
                cnt = 1
                while True:
                    key = text + str(cnt)
                    if key not in self._bookmark_keys:
                        self._bookmark_keys.append(key)
                        break
                    cnt += 1

            if isinstance(flowable, SmartParagraph):
                # Only smart paragraphs know their own position
                x, y = flowable.get_pos()
                y += flowable.style.fontSize + 15
                self.canv.bookmarkPage(key, fit="FitH", top=y)
            else:
                # Dumb paragraphs need to show the whole page
                self.canv.bookmarkPage(key)

            self.canv.addOutlineEntry(title=text, key=key, level=level)

    def _endBuild(self):
        """Override of parent function. Shows outline tree by default when opening PDF."""
        super(CustomDocTemplate, self)._endBuild()
        self.canv.showOutline()


story = []
txt_folder = '诡秘之主'
doc = CustomDocTemplate(f'{txt_folder}.pdf', pagesize=A4)

txt_files = sorted(
    [f for f in os.listdir(txt_folder) if f.endswith('.txt')],
    key=lambda f: os.path.getctime(os.path.join(txt_folder, f))
)
all_files = txt_files[12:]
all_files.extend(reversed(txt_files[0:12]))
# 循环迭代生成章节内容
for txt_file in all_files:
    chapter_title = os.path.splitext(txt_file)[0]
    with open(os.path.join(txt_folder, txt_file), 'r', encoding='utf-8') as txt:
        chapter_content = txt.read()

    # 添加章节标签
    story.append(SmartParagraph(chapter_title, stylesheet['bookmark']))

    paragraphs = chapter_content.split("\n")
    # 添加章节内容
    for paragraph in paragraphs:
        para = Paragraph("\t" + paragraph, stylesheet['default'])
        story.append(para)
    story.append(PageBreak())
    # 构建文档
doc.multiBuild(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
