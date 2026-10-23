import unittest

from session_export.render_html import render_assistant, render_html
from session_export.render_md import render_markdown
from session_export.transcript import Block, Transcript, build_transcript
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

    def test_linked_image_is_embedded(self):
        transcript = Transcript(
            blocks=[Block("you", text="See this", images=[("image/png", "AAAA")])]
        )
        page = render_html(transcript, title="T", workspace="W", timestamp="t")
        self.assertIn("data:image/png;base64,AAAA", page)


if __name__ == "__main__":
    unittest.main()
