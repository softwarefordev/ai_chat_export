import unittest

from ai_chat_export.render_html import render_assistant, render_html
from ai_chat_export.render_md import render_markdown
from ai_chat_export.transcript import Block, Transcript, build_transcript
from tests.support import sample_messages


class AssistantSubsetTests(unittest.TestCase):
    def test_fenced_code(self):
        html = render_assistant("```\nprint(1)\n```")
        self.assertIn("<pre><code>print(1)</code></pre>", html)

    def test_list(self):
        html = render_assistant("- alpha\n- beta")
        self.assertIn("<li>alpha</li>", html)
        self.assertIn("<li>beta</li>", html)

    def test_paragraph(self):
        html = render_assistant("Hello there")
        self.assertIn("<p>Hello there</p>", html)

    def test_inline_code(self):
        html = render_assistant("use `x` here")
        self.assertIn("<code>x</code>", html)
        self.assertIn("use ", html)


class DocumentTests(unittest.TestCase):
    def setUp(self):
        messages, prompts = sample_messages()
        self.transcript = build_transcript(messages, prompts)
        self.meta = {
            "title": "Fantasy Map Maker",
            "workspace": "SoggyMapMaker",
            "timestamp": "Aug 15, 2026 04:42 PM",
        }

    def test_dark_is_default_and_light_is_separate(self):
        dark = render_html(self.transcript, theme="dark", **self.meta)
        light = render_html(self.transcript, theme="light", **self.meta)
        self.assertIn("#161616", dark)
        self.assertNotIn("#f7f7f4", dark)
        self.assertIn("#f7f7f4", light)
        self.assertNotIn("#161616", light)
        for page in (dark, light):
            self.assertNotIn("<script", page.lower())
            self.assertNotIn("http", page.lower())
            self.assertIn("Please add a river tool.", page)
            self.assertIn("The river tool lives in tools/river.py.", page)

    def test_markdown_matches_visible_turns_without_color(self):
        messages, prompts = sample_messages()
        shown = build_transcript(messages, prompts, show_tools=True)
        page = render_html(shown, **self.meta)
        markdown = render_markdown(shown, **self.meta)
        for text in (
            "Please add a river tool.",
            "The river tool lives in tools/river.py.",
            "Read tools/river.py",
            "Glob *.py",
            "Ran List map tool modules",
        ):
            self.assertIn(text, page)
            self.assertIn(text, markdown)
        self.assertNotIn("#161616", markdown)
        self.assertNotIn("#f7f7f4", markdown)
        self.assertNotIn("SECRET_COMMAND_XYZ", markdown)
        self.assertEqual(page.count("<h2>Agent</h2>"), 1)
        self.assertEqual(markdown.count("## Agent"), 1)

    def test_one_agent_heading_until_the_next_prompt(self):
        messages = [
            {"role": "user", "content": "First prompt"},
            {"role": "assistant", "content": [{"type": "text", "text": "First answer"}]},
            {"role": "assistant", "content": [{"type": "text", "text": "Second answer"}]},
            {"role": "user", "content": "Second prompt"},
            {"role": "assistant", "content": [{"type": "text", "text": "Third answer"}]},
        ]
        prompts = ["First prompt", "Second prompt"]
        transcript = build_transcript(messages, prompts)
        page = render_html(transcript, **self.meta)
        markdown = render_markdown(transcript, **self.meta)
        self.assertEqual(page.count("<h2>Agent</h2>"), 2)
        self.assertEqual(markdown.count("## Agent"), 2)
        first_agent = markdown.split("## User")[1]
        self.assertIn("First answer", first_agent)
        self.assertIn("Second answer", first_agent)
        self.assertNotIn("Third answer", first_agent)

    def test_tools_only_stretch_has_no_heading_by_default(self):
        messages = [
            {"role": "user", "content": "Go"},
            {
                "role": "assistant",
                "content": [
                    {"type": "tool-call", "toolName": "Read", "args": {"path": "a.py"}}
                ],
            },
            {
                "role": "tool",
                "content": [{"type": "tool-result", "toolName": "Read", "result": "file body"}],
            },
        ]
        transcript = build_transcript(messages, ["Go"])
        page = render_html(transcript, **self.meta)
        markdown = render_markdown(transcript, **self.meta)
        self.assertNotIn("<h2>Agent</h2>", page)
        self.assertNotIn("## Agent", markdown)
        self.assertNotIn("Read a.py", page)
        self.assertNotIn("file body", page)

    def test_turn_time_renders_on_you_and_agent_and_header_stays(self):
        query = "Please add a river tool."
        messages = [
            {
                "role": "user",
                "content": "<timestamp>Friday, Oct 23, 2026, 11:13 AM (UTC-7)</timestamp>\n"
                f"<user_query>{query}</user_query>",
            },
            {"role": "assistant", "content": "Done."},
        ]
        transcript = build_transcript(messages, [query])
        page = render_html(transcript, **self.meta)
        markdown = render_markdown(transcript, **self.meta)
        turn = "Oct 23, 2026 11:13 AM"
        header = self.meta["timestamp"]
        self.assertIn(f'<h2>User <span class="time">{turn}</span></h2>', page)
        self.assertIn(f'<h2>Agent <span class="time">{turn}</span></h2>', page)
        self.assertIn(f'<span class="time">{header}</span>', page)
        self.assertIn(f"## User · {turn}", markdown)
        self.assertIn(f"## Agent · {turn}", markdown)
        self.assertIn(header, markdown)
        bare = build_transcript(*sample_messages())
        bare_page = render_html(bare, **self.meta)
        bare_markdown = render_markdown(bare, **self.meta)
        self.assertIn("<h2>User</h2>", bare_page)
        self.assertIn("<h2>Agent</h2>", bare_page)
        self.assertIn(f'<span class="time">{header}</span>', bare_page)
        self.assertIn("## User\n", bare_markdown)
        self.assertNotIn("## User ·", bare_markdown)

    def test_user_and_agent_panels_differ_in_both_themes(self):
        transcript = Transcript(
            blocks=[
                Block("you", text="Prompt"),
                Block("agent", text="Reply"),
                Block("system", text="Note"),
            ]
        )
        dark = render_html(transcript, theme="dark", **self.meta)
        light = render_html(transcript, theme="light", **self.meta)
        self.assertIn("--user: #2c261c;", dark)
        self.assertIn("--agent: #1e2428;", dark)
        self.assertIn("--panel: #222222;", dark)
        self.assertIn("#161616", dark)
        self.assertNotIn("#f7f7f4", dark)
        self.assertIn("--user: #f6efe4;", light)
        self.assertIn("--agent: #f3f5f7;", light)
        self.assertIn("--panel: #ffffff;", light)
        self.assertIn("#f7f7f4", light)
        self.assertNotIn("#161616", light)
        for page in (dark, light):
            self.assertIn(
                "section.you { background: var(--user); border-left: 3px solid var(--mark); scroll-margin-top: 5rem; }",
                page,
            )
            self.assertIn("section.agent { background: var(--agent); }", page)
            self.assertIn("section.system, section.context { background: var(--panel); }", page)
            self.assertIn('<section class="you"', page)
            self.assertIn('<section class="agent" data-turn="1">', page)
            self.assertIn('<section class="system">', page)

    def test_navigator_links_user_turns_and_clips_the_first_line(self):
        transcript = Transcript(
            blocks=[
                Block("you", text="First line\nLater line", timestamp="Oct 23, 2026 11:13 AM"),
                Block("agent", text="Agent only reply"),
                Block("context", text="Hidden context"),
                Block("you", text="Second prompt"),
                Block("you", text="", images=[("image/png", "BBBB")]),
                Block("you", text=""),
            ]
        )
        page = render_html(transcript, **self.meta)
        nav = page.split("<article>", 1)[0]
        self.assertIn('<a href="#user-1">', nav)
        self.assertIn('<a href="#user-2">', nav)
        self.assertIn('<a href="#user-3">', nav)
        self.assertIn('<a href="#user-4">', nav)
        self.assertIn('id="user-1"', page)
        self.assertIn('id="user-4"', page)
        self.assertIn("26-10-23 11:13", nav)
        self.assertNotIn("Oct 23, 2026 11:13 AM", nav)
        self.assertIn(
            '<h2>User <span class="time">Oct 23, 2026 11:13 AM</span></h2>',
            page,
        )
        self.assertIn('<span class="label">First line</span>', nav)
        self.assertIn('<span class="label">Second prompt</span>', nav)
        self.assertIn('<span class="label">Image</span>', nav)
        self.assertIn('<span class="label">User</span>', nav)
        self.assertNotIn("Later line", nav)
        self.assertNotIn("Agent only reply", nav)
        self.assertNotIn("Hidden context", nav)
        self.assertNotIn('href="#user-5"', page)
        self.assertIn("position: sticky", page)
        self.assertIn("text-overflow: ellipsis", page)
        self.assertIn("section.you:target { outline: 2px solid var(--mark); }", page)
        self.assertNotIn("<script", page.lower())
        self.assertNotIn("http", page.lower())

        empty = render_html(
            Transcript(blocks=[Block("agent", text="Only reply")]),
            title="T",
            workspace="W",
            timestamp="t",
        )
        empty_nav = empty.split("<article>", 1)[0]
        self.assertIn("<nav>", empty_nav)
        self.assertNotIn("<li>", empty_nav)
        self.assertNotIn("Only reply", empty_nav)

    def test_navigator_compacts_parsed_times_and_keeps_headings(self):
        cases = (
            ("Oct 23, 2026 01:08 PM", "26-10-23 13:08"),
            ("Oct 23, 2026 11:13 AM", "26-10-23 11:13"),
            ("Sep 1, 2026 09:05 AM", "26-09-01 09:05"),
            ("Oct 23, 2026 12:00 AM", "26-10-23 00:00"),
            ("Oct 23, 2026 12:00 PM", "26-10-23 12:00"),
            ("sometime next week", "sometime next week"),
        )
        blocks = [
            Block("you", text=f"Query {index}", timestamp=stamp)
            for index, (stamp, _compact) in enumerate(cases)
        ]
        blocks.append(Block("agent", text="Reply", timestamp="Oct 23, 2026 01:08 PM"))
        page = render_html(Transcript(blocks=blocks), **self.meta)
        nav, article = page.split("<article>", 1)
        for stamp, compact in cases:
            self.assertIn(f'<span class="time">{compact}</span>', nav)
            self.assertIn(f'<h2>User <span class="time">{stamp}</span></h2>', article)
            if stamp != compact:
                self.assertNotIn(stamp, nav)
        self.assertIn(
            '<h2>Agent <span class="time">Oct 23, 2026 01:08 PM</span></h2>',
            article,
        )

    def test_navigator_time_uses_a_smaller_font(self):
        transcript = Transcript(
            blocks=[
                Block("you", text="Parsed query", timestamp="Oct 23, 2026 11:13 AM"),
                Block("you", text="Stored query", timestamp="sometime next week"),
            ]
        )
        page = render_html(transcript, **self.meta)
        nav = page.split("<article>", 1)[0]
        self.assertIn("nav .time { font-size: 10px; white-space: nowrap; }", page)
        self.assertIn("nav a { display: flex; flex-direction: column;", page)
        self.assertIn('font-family: "Segoe UI", system-ui, sans-serif;', page)
        self.assertNotIn("0.75rem", page)
        link = nav.split("<a ", 1)[1]
        self.assertLess(link.index('<span class="time">'), link.index('<span class="label">'))
        self.assertIn('<span class="time">26-10-23 11:13</span>', nav)
        self.assertIn('<span class="time">sometime next week</span>', nav)
        self.assertIn(
            'font: 18px/1.5 Georgia, "Iowan Old Style", Palatino, serif;',
            page,
        )
        self.assertNotIn("nav .label { font-size", page)

    def test_navigator_column_is_30rem_from_70rem(self):
        page = render_html(self.transcript, **self.meta)
        self.assertIn("@media (min-width: 70rem) {", page)
        self.assertIn("grid-template-columns: 30rem minmax(0, 1fr);", page)
        self.assertNotIn("16rem", page)
        self.assertNotIn("52rem", page)

    def test_turn_mark_groups_the_user_and_following_agent(self):
        transcript = Transcript(
            blocks=[
                Block("system", text="Preamble"),
                Block("you", text="First"),
                Block("agent", text="Reply one"),
                Block("context", text="Injected"),
                Block("agent", text="Reply two"),
                Block("you", text="Second"),
                Block("you", text="Third"),
                Block("agent", text="Reply three"),
            ]
        )
        page = render_html(transcript, **self.meta)
        article = page.split("<article>", 1)[1]
        self.assertIn('<section class="you" id="user-1" data-turn="1">', article)
        self.assertEqual(article.count('data-turn="1"'), 3)
        self.assertIn('<section class="you" id="user-2" data-turn="2">', article)
        self.assertEqual(article.count('data-turn="2"'), 1)
        self.assertIn('<section class="you" id="user-3" data-turn="3">', article)
        self.assertIn('<section class="agent" data-turn="3">', article)
        self.assertEqual(article.count('data-turn="3"'), 2)
        self.assertIn('<section class="system">', article)
        self.assertIn('<section class="context">', article)
        self.assertNotIn('class="system" data-turn', article)
        self.assertNotIn('class="context" data-turn', article)

    def test_checkbox_sits_beside_an_unchecked_link(self):
        transcript = Transcript(
            blocks=[
                Block("you", text="First line\nLater line"),
                Block("agent", text="Reply"),
            ]
        )
        page = render_html(transcript, **self.meta)
        nav = page.split("<nav>", 1)[1].split("</nav>", 1)[0]
        item = nav.split("<li>", 1)[1].split("</li>", 1)[0]
        self.assertLess(item.index('type="checkbox"'), item.index("<a "))
        self.assertIn('id="keep-1"', item)
        self.assertIn('href="#user-1"', item)
        self.assertNotIn("<input", item.split("<a ", 1)[1])
        self.assertNotRegex(page, r"<input[^>]*\bchecked\b")
        self.assertIn('<a href="#user-1">', nav)
        self.assertNotIn("<script", page.lower())
        self.assertNotIn("http", page.lower())

    def test_filter_rules_keep_the_title_and_footer(self):
        transcript = Transcript(
            blocks=[
                Block("you", text="First"),
                Block("agent", text="Reply"),
                Block("you", text="Second"),
                Block("you", text="Third"),
            ],
            footer=["Kept note"],
        )
        page = render_html(transcript, **self.meta)
        hide = "body:has(nav input:checked) article section { display: none; }"
        self.assertIn(hide, page)
        self.assertNotIn("header", hide)
        self.assertNotIn("footer", hide)
        for number in (1, 2, 3):
            self.assertIn(
                "body:has(#keep-"
                f'{number}:checked) article [data-turn="{number}"] {{ display: block; }}',
                page,
            )
        self.assertIn("<header>", page)
        self.assertIn("<h1>Fantasy Map Maker</h1>", page)
        self.assertIn("<footer>", page)
        self.assertIn("Kept note", page)

    def test_clear_filter_sits_at_both_ends(self):
        transcript = Transcript(blocks=[Block("you", text="First"), Block("you", text="Second")])
        page = render_html(transcript, **self.meta)
        nav = page.split("<nav>", 1)[1].split("</nav>", 1)[0]
        button = '<button type="reset">Clear filter</button>'
        self.assertEqual(nav.count(button), 2)
        self.assertLess(nav.index(button), nav.index("<ol>"))
        self.assertGreater(nav.rindex(button), nav.index("</ol>"))
        self.assertIn(
            "nav button { display: none; font: inherit; color: var(--text); background: var(--bg); border: 1px solid var(--rule); }",
            page,
        )
        self.assertIn("body:has(nav input:checked) nav button { display: block; }", page)
        self.assertIn("nav form > button:first-child { position: sticky; top: 0; z-index: 1; }", page)

    def test_markdown_has_no_turn_filter(self):
        transcript = Transcript(
            blocks=[Block("you", text="Prompt"), Block("agent", text="Reply")]
        )
        markdown = render_markdown(transcript, **self.meta)
        self.assertNotIn("checkbox", markdown)
        self.assertNotIn("Clear filter", markdown)
        self.assertIn("## User", markdown)

    def test_linked_image_is_embedded(self):
        transcript = Transcript(
            blocks=[Block("you", text="See this", images=[("image/png", "AAAA")])]
        )
        page = render_html(transcript, title="T", workspace="W", timestamp="t")
        self.assertIn("data:image/png;base64,AAAA", page)


if __name__ == "__main__":
    unittest.main()
