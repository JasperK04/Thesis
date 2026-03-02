html = """
<!DOCTYPE html>

<html lang="en-us">
<head>
<meta charset="utf-8"/>
<title>Day 1 - Advent of Code 2015</title>
<link href="/static/style.css?32" rel="stylesheet" type="text/css"/>
<link href="/static/highcontrast.css?2" rel="stylesheet alternate" title="High Contrast" type="text/css"/>
<link href="/favicon.png" rel="shortcut icon"/>
<script>window.addEventListener('click', function(e,s,r){if(e.target.nodeName==='CODE'&&e.detail===3){s=window.getSelection();s.removeAllRanges();r=document.createRange();r.selectNodeContents(e.target);s.addRange(r);}});</script>
</head><!--




Oh, hello!  Funny seeing you here.

I appreciate your enthusiasm, but you aren't going to find much down here.
There certainly aren't clues to any of the puzzles.  The best surprises don't
even appear in the source until you unlock them for real.

Please be careful with automated requests; I'm not a massive company, and I can
only take so much traffic.  Please be considerate so that everyone gets to play.

If you're curious about how Advent of Code works, it's running on some custom
Perl code. Other than a few integrations (auth, analytics, social media), I
built the whole thing myself, including the design, animations, prose, and all
of the puzzles.

The puzzles are most of the work; preparing a new calendar and a new set of
puzzles takes all of my free time for months every year. A lot of effort went
into building this thing - I hope you're enjoying playing it as much as I
enjoyed making it for you!

If you'd like to hang out, I'm @was.tl on Bluesky and @ericwastl@hachyderm.io
on Mastodon.

- Eric Wastl


















































-->
<body>
<header><div><h1 class="title-global"><a href="/">Advent of Code</a></h1><nav><ul><li><a href="/2015/about">[About]</a></li><li><a href="/2015/events">[Events]</a></li><li><a href="/2015/shop">[Shop]</a></li><li><a href="/2015/settings">[Settings]</a></li><li><a href="/2015/auth/logout">[Log Out]</a></li></ul></nav><div class="user">(anonymous user #5669892) <span class="star-count">50*</span></div></div><div><h1 class="title-event">      <span class="title-event-wrap">/*</span><a href="/2015">2015</a><span class="title-event-wrap">*/</span></h1><nav><ul><li><a href="/2015">[Calendar]</a></li><li><a href="/2015/support">[AoC++]</a></li><li><a href="/2015/sponsors">[Sponsors]</a></li><li><a href="/2015/leaderboard">[Leaderboards]</a></li><li><a href="/2015/stats">[Stats]</a></li></ul></nav></div></header>
<div id="sidebar">
</div><!--/sidebar-->
<main>
<style>article *[title]{border-bottom:1px dotted #ffff66;}</style><article class="day-desc"><h2>--- Day 1: Not Quite Lisp ---</h2><p>Santa was hoping for a white Christmas, but his weather machine's "snow" function is powered by stars, and he's fresh out!  To save Christmas, he needs you to collect <em class="star">fifty stars</em> by December 25th.</p>
<p>Collect stars by helping Santa solve puzzles.  Two puzzles will be made available on each day in the Advent calendar; the second puzzle is unlocked when you complete the first.  Each puzzle grants <em class="star">one star</em>. <span title="Also, some puzzles contain Easter eggs like this one. Yes, I know it's not traditional to do Advent calendars for Easter.">Good luck!</span></p>
<p>Here's an easy puzzle to warm you up.</p>
<p>Santa is trying to deliver presents in a large apartment building, but he can't find the right floor - the directions he got are a little confusing. He starts on the ground floor (floor <code>0</code>) and then follows the instructions one character at a time.</p>
<p>An opening parenthesis, <code>(</code>, means he should go up one floor, and a closing parenthesis, <code>)</code>, means he should go down one floor.</p>
<p>The apartment building is very tall, and the basement is very deep; he will never find the top or bottom floors.</p>
<p>For example:</p>
<ul>
<li><code>(())</code> and <code>()()</code> both result in floor <code>0</code>.</li>
<li><code>(((</code> and <code>(()(()(</code> both result in floor <code>3</code>.</li>
<li><code>))(((((</code> also results in floor <code>3</code>.</li>
<li><code>())</code> and <code>))(</code> both result in floor <code>-1</code> (the first basement level).</li>
<li><code>)))</code> and <code>)())())</code> both result in floor <code>-3</code>.</li>
</ul>
<p>To <em>what floor</em> do the instructions take Santa?</p>
</article>
<p>Your puzzle answer was .</p><article class="day-desc"><h2 id="part2">--- Part Two ---</h2><p>Now, given the same instructions, find the <em>position</em> of the first character that causes him to enter the basement (floor <code>-1</code>).  The first character in the instructions has position <code>1</code>, the second character has position <code>2</code>, and so on.</p>
<p>For example:</p>
<ul>
<li><code>)</code> causes him to enter the basement at character position <code>1</code>.</li>
<li><code>()())</code> causes him to enter the basement at character position <code>5</code>.</li>
</ul>
<p>What is the <em>position</em> of the character that causes Santa to first enter the basement?</p>
</article>
<p>Your puzzle answer was .</p><p class="day-success">Both parts of this puzzle are complete! They provide two gold stars: **</p>
<p>At this point, all that is left is for you to <a href="/2015">admire your Advent calendar</a>.</p>
<p>If you still want to see it, you can <a href="1/input" target="_blank">get your puzzle input</a>.</p>
<p>You can also <span class="share">[Share<span class="share-content">on
  <a href="https://bsky.app/intent/compose?text=I%27ve+completed+%22Not+Quite+Lisp%22+%2D+Day+1+%2D+Advent+of+Code+2015+%23AdventOfCode+https%3A%2F%2Fadventofcode%2Ecom%2F2015%2Fday%2F1" target="_blank">Bluesky</a>
<a href="https://twitter.com/intent/tweet?text=I%27ve+completed+%22Not+Quite+Lisp%22+%2D+Day+1+%2D+Advent+of+Code+2015&amp;url=https%3A%2F%2Fadventofcode%2Ecom%2F2015%2Fday%2F1&amp;related=ericwastl&amp;hashtags=AdventOfCode" target="_blank">Twitter</a>
<a href="javascript:void(0);" onclick="var ms; try{ms=localStorage.getItem('mastodon.server')}finally{} if(typeof ms!=='string')ms=''; ms=prompt('Mastodon Server?',ms); if(typeof ms==='string' &amp;&amp; ms.length){this.href='https://'+ms+'/share?text=I%27ve+completed+%22Not+Quite+Lisp%22+%2D+Day+1+%2D+Advent+of+Code+2015+%23AdventOfCode+https%3A%2F%2Fadventofcode%2Ecom%2F2015%2Fday%2F1';try{localStorage.setItem('mastodon.server',ms);}finally{}}else{return false;}" target="_blank">Mastodon</a></span>]</span> this puzzle.</p>
</main>
<!-- ga -->
<script>
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','//www.google-analytics.com/analytics.js','ga');
ga('create', 'UA-69522494-1', 'auto');
ga('set', 'anonymizeIp', true);
ga('send', 'pageview');
</script>
<!-- /ga -->
</body>
</html>
"""

import textwrap

from bs4 import BeautifulSoup, NavigableString, Tag

soup = BeautifulSoup(html, "html.parser")

main_tag = soup.find("main")
if not main_tag:
    exit(1)
main_tag.extract()
body = soup.body
if body is not None:
    body.clear()
    body.append(main_tag)
else:
    soup.clear()
    soup.append(main_tag)
for paragraph in main_tag.find_all("p", recursive=False):
    for code_tag in paragraph.find_all("code"):
        code_tag.decompose()

for tag in main_tag.find_all(True):
    tag.attrs.pop("onclick", None)

WRAP_WIDTH = 120
INDENT = "  "
BLOCK_TAGS = {
    "main",
    "article",
    "section",
    "p",
    "ul",
    "ol",
    "li",
    "pre",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "style",
}
INLINE_TAGS = {
    "a",
    "code",
    "em",
    "span",
    "strong",
}


def _format_attrs(tag: Tag) -> str:
    parts: list[str] = []
    for key, value in tag.attrs.items():
        if isinstance(value, list):
            value = " ".join(value)
        parts.append(f'{key}="{str(value)}"')
    return "" if not parts else " " + " ".join(parts)


def _format_text(text: str, indent: str) -> str:
    cleaned = " ".join(text.split())
    if not cleaned:
        return ""
    return textwrap.fill(
        cleaned,
        width=WRAP_WIDTH,
        initial_indent=indent,
        subsequent_indent=indent,
    )


def _format_inline(node: Tag | NavigableString) -> str:
    if isinstance(node, NavigableString):
        return " ".join(str(node).split())
    attrs = _format_attrs(node)
    inner = "".join(_format_inline(child) for child in node.contents)
    return f"<{node.name}{attrs}>{inner}</{node.name}>"


def _format_node(node: Tag | NavigableString, depth: int) -> str:
    indent = INDENT * depth
    if isinstance(node, NavigableString):
        return _format_text(str(node), indent)

    attrs = _format_attrs(node)
    if node.name == "pre":
        pre_text = node.get_text()
        return f"{indent}<{node.name}{attrs}>\n{pre_text}\n{indent}</{node.name}>"

    is_block = node.name in BLOCK_TAGS
    if not node.contents:
        return f"{indent}<{node.name}{attrs}></{node.name}>"

    if is_block:
        inline_only = all(
            isinstance(child, NavigableString)
            or (isinstance(child, Tag) and child.name in INLINE_TAGS)
            for child in node.contents
        )
        if inline_only:
            inner = " ".join(
                filter(None, (_format_inline(child) for child in node.contents))
            )
            inner = " ".join(inner.split())
            return f"{indent}<{node.name}{attrs}>{inner}</{node.name}>"

        lines: list[str] = [f"{indent}<{node.name}{attrs}>"]
        for child in node.contents:
            rendered = _format_node(child, depth + 1)
            if rendered:
                lines.append(rendered)
        lines.append(f"{indent}</{node.name}>")
        return "\n".join(lines)

    inner = "".join(_format_node(child, 0).strip() for child in node.contents)
    return f"{indent}<{node.name}{attrs}>{inner}</{node.name}>"


with open("test.html", "w") as f:
    f.write(_format_node(main_tag, 0))
