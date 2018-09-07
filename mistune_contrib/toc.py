# coding: utf-8

"""
    mistune_contrib.toc
    ~~~~~~~~~~~~~~~~~~~

    Support TOC features for mistune.

    :copyright: (c) 2015 by Hsiaoming Yang.
"""


class TocMixin(object):
    """TOC mixin for Renderer, mix this with Renderer::

        class TocRenderer(TocMixin, Renderer):
            pass

        toc = TocRenderer()
        md = mistune.Markdown(renderer=toc)

        # required in this order
        toc.reset_toc()          # initial the status
        md.parse(text)           # parse for headers
        toc.render_toc(level=3)  # render TOC HTML
    """

    def reset_toc(self):
        self.toc_tree = []
        self.toc_count = 0

    def header(self, text, level, raw=None):
        rv = '<h%d id="toc-%d">%s</h%d>\n' % (
            level, self.toc_count, text, level
        )
        self.toc_tree.append((self.toc_count, text, level, raw))
        self.toc_count += 1
        return rv

    def render_toc(self, level=3):
        """Render TOC to HTML.

        :param level: render toc to the given level
        """
        return ''.join(self._iter_toc(level))

    def _iter_toc(self, level):
        first_level = 0
        last_level = 0
        # because we have everything in nested li's we need to put each _line_ in
        # its own div so that we can set the div border as a dotted line in css
        # since there is no leader() available
        link_template = """%s<div class="tocline"><a href="#toc-%d">%s</a> <a href="#toc-%d" class="tocpagenr">&nbsp;</a></div>"""

        yield '<ul id="table-of-content">\n'

        for toc in self.toc_tree:
            index, text, l, raw = toc

            if l > level:
                # ignore this level
                continue

            if first_level == 0 :
                # based on first level
                first_level = l
                last_level = l
                yield link_template % ('<li>', index, text, index)
            elif last_level == l:
                yield link_template % ('</li>\n<li>', index, text, index)
            elif last_level == l - 1:
                last_level = l
                yield link_template % ('<ul>\n<li>', index, text, index)
            elif last_level > l:
                # close indention
                yield '</li>'
                while last_level > l:
                    yield '</ul>\n</li>\n'
                    last_level -= 1
                yield link_template % ('<li>', index, text, index)

        # close tags
        yield '</li>\n'
        while last_level > first_level:
            yield '</ul>\n</li>\n'
            last_level -= 1

        yield '</ul>\n'
