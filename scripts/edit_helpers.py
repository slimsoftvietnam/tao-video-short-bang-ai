# Studio-safe patching for a HyperFrames index.html.
#
# Opening a project in Studio re-serialises index.html every time: it injects
# `data-hf-id="…"` before `id` (507 of them in one pass), turns `<br />` into `<br>`,
# collapses multi-line attributes, and drops duplicate attributes. Any patch script
# that matches HTML by literal text breaks the first time the author previews — this
# happened on the first edit of two consecutive projects.
#
# Studio leaves the CSS and the <script> block alone. So:
#   HTML  -> address by id and walk tag depth   (replace_el, drop_el, retop)
#   CSS/JS -> literal text is fine               (sub)
#
# Usage from a project's revise script:
#
#     import sys; sys.path.insert(0, "scripts")
#     from edit_helpers import Doc
#     d = Doc("index.html")
#     d.replace_el("h-title", '<div class="pad" id="h-title" ...>...</div>')
#     d.retop("h-4", 980)
#     d.sub('show("#h-4", 3.60', 'show("#h-4", 3.85')
#     d.save()
#
# Every operation asserts. A patch that silently matches nothing is worse than one
# that crashes: you find out at render time, or the author finds out on playback.
#
# WRITE PATCH SCRIPTS WITH THE WRITE TOOL. A `\b` in a regex passed through a Bash
# heredoc or `python -c` becomes a literal backspace byte (0x08). The pattern then
# matches when tested on its own and fails inside the script. `cat -A` shows `^H`.
import io
import re


class Doc:
    def __init__(self, path="index.html"):
        self.path = path
        self.s = io.open(path, encoding="utf-8").read()

    def save(self):
        io.open(self.path, "w", encoding="utf-8").write(self.s)

    # ── HTML, by id ──────────────────────────────────────────────────────────
    def _open_tag(self, el_id):
        """The opening tag carrying id="el_id". The id must be a whole attribute,
        not the tail of data-hf-id="…", hence the lookbehind."""
        pat = r'<(\w+)(?=[^>]*(?<![-\w])id="%s")[^>]*>' % re.escape(el_id)
        m = re.search(pat, self.s)
        assert m, "element not found: #" + el_id
        return m

    def _extent(self, el_id):
        """(line_start, end) of the whole element, children included. Walks tag
        depth: a non-greedy scan for the next close stops at the first child."""
        m = self._open_tag(el_id)
        tag, i = m.group(1), m.end()
        if not m.group(0).endswith("/>"):
            depth = 1
            pat = re.compile(r"<(/?)%s\b[^>]*?(/?)>" % tag)
            while depth:
                mm = pat.search(self.s, i)
                assert mm, "unclosed <%s> for #%s" % (tag, el_id)
                i = mm.end()
                if mm.group(1):
                    depth -= 1
                elif not mm.group(2):
                    depth += 1
        return self.s.rfind("\n", 0, m.start()) + 1, i

    def replace_el(self, el_id, new_html):
        """Replace the element with new_html, from the start of its own line, so
        indentation comes from new_html."""
        a, b = self._extent(el_id)
        self.s = self.s[:a] + new_html + self.s[b:]

    def drop_el(self, el_id):
        a, b = self._extent(el_id)
        # swallow the now-empty line
        if self.s[b:b + 1] == "\n":
            b += 1
        self.s = self.s[:a] + self.s[b:]

    def retop(self, el_id, px):
        """Change one element's `top:` without touching anything else in the tag."""
        m = self._open_tag(el_id)
        tag = m.group(0)
        new, n = re.subn(r"top:\s*-?\d+px", "top:%dpx" % px, tag, count=1)
        assert n == 1, "no top: in #" + el_id
        self.s = self.s[:m.start()] + new + self.s[m.end():]

    def set_style(self, el_id, style):
        """Replace the element's style attribute wholesale. There must only ever be
        ONE style attribute per tag: the browser keeps the first and Studio drops
        the rest. Merging by hand once produced `style="…" class="" … style="…"`,
        which also lost `class="pad"` and with it `position:absolute`."""
        m = self._open_tag(el_id)
        tag = m.group(0)
        n_style = len(re.findall(r'\sstyle="', tag))
        if n_style:
            tag = re.sub(r'\sstyle="[^"]*"', "", tag)
        tag = tag[:-1] + ' style="%s">' % style if not tag.endswith("/>") \
            else tag[:-2] + ' style="%s" />' % style
        self.s = self.s[:m.start()] + tag + self.s[m.end():]

    def count_id(self, el_id):
        return len(re.findall(r'(?<![-\w])id="%s"' % re.escape(el_id), self.s))

    # ── CSS and JS, literal ──────────────────────────────────────────────────
    def sub(self, old, new, n=1):
        """Literal replace. Only for CSS and <script> text — never for tags."""
        c = self.s.count(old)
        assert c == n, "count %d (want %d): %r" % (c, n, old[:90])
        self.s = self.s.replace(old, new, n)
