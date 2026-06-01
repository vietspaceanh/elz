from __future__ import annotations

from pygments.lexers import Python3Lexer, get_lexer_by_name
from pygments.token import Comment, String, Name, Punctuation, Text

SUBLANG_PREFIXES = frozenset({"sql", "html", "md"})
FUNC_SUBLANG = {"sql": "sql", "plot": "sql", "el": "md"}
TRIPLE_DELIMS = frozenset({"'''", '"""'})


class ElfPythonLexer(Python3Lexer):
    name = "ElfPython"
    aliases = ["elf-python"]

    def __init__(self, **options):
        super().__init__(**options)
        self._cache: dict[str, object] = {}

    def _get_lexer(self, lang: str):
        if lang not in self._cache:
            try:
                self._cache[lang] = get_lexer_by_name(lang)
            except Exception:
                self._cache[lang] = None
        return self._cache[lang]

    def get_tokens_unprocessed(self, text):
        tokens = list(super().get_tokens_unprocessed(text))
        return self._process(tokens)

    def _is_string_type(self, ttype) -> bool:
        return ttype in String

    def _is_text_type(self, ttype) -> bool:
        return ttype in Text

    def _is_interpol_type(self, ttype) -> bool:
        return ttype in String.Interpol

    def _process(self, tokens):
        result = []
        i = 0
        n = len(tokens)
        while i < n:
            r, i = self._try_pattern(tokens, i)
            result.extend(r)
        return result

    def _try_pattern(self, tokens, i):
        r, ni = self._try_triple_with_prefix(tokens, i)
        if r is not None:
            return r, ni
        r, ni = self._try_func_call(tokens, i)
        if r is not None:
            return r, ni
        return [tokens[i]], i + 1

    def _detect_sublang(self, inner_text: str) -> tuple[str | None, str]:
        first = inner_text.lstrip()
        first_word = first.split(None, 1)[0] if first else ""
        if first_word in SUBLANG_PREFIXES:
            return first_word, first_word
        if first_word == "--sql":
            return "sql", first_word
        return None, first_word

    def _try_triple_with_prefix(self, tokens, i):
        n = len(tokens)
        if i >= n:
            return None, i

        affix = ""
        idx = i

        if self._is_string_type(tokens[idx][1]) and tokens[idx][2] in ("f", "F"):
            affix = tokens[idx][2]
            idx += 1
            if idx >= n:
                return None, i

        if not (self._is_string_type(tokens[idx][1]) and tokens[idx][2] in TRIPLE_DELIMS):
            return None, i
        open_delim = tokens[idx][2]
        delim_token = tokens[idx]
        idx += 1
        if idx >= n:
            return None, i

        content_tokens = []
        close_token = None
        while idx < n:
            t = tokens[idx]
            if t[2] == open_delim and self._is_string_type(t[1]):
                close_token = t
                idx += 1
                break
            content_tokens.append(t)
            idx += 1

        if close_token is None:
            return None, i

        inner_text = "".join(t[2] for t in content_tokens)

        lang, first_word = self._detect_sublang(inner_text)

        if lang is None:
            return None, i

        sub_lexer = self._get_lexer(lang)

        result = []
        if affix:
            result.append((tokens[i][0], String.Affix, affix))
        result.append((delim_token[0], String, open_delim))
        result.append((content_tokens[0][0], Comment, first_word))

        for seg_type, seg_tokens in self._split_segments(content_tokens[1:]):
            if seg_type == 'text':
                seg_text = "".join(t[2] for t in seg_tokens)
                if sub_lexer and seg_text:
                    base = seg_tokens[0][0]
                    for sp, st, sv in sub_lexer.get_tokens_unprocessed(seg_text):
                        result.append((base + sp, st, sv))
                elif seg_text:
                    result.append((seg_tokens[0][0], String, seg_text))
            else:
                for t in seg_tokens:
                    result.append(t)
        result.append((close_token[0], String, close_token[2]))
        return result, idx

    def _split_segments(self, tokens):
        segments = []
        text_buf = []
        i = 0
        while i < len(tokens):
            t = tokens[i]
            if self._is_interpol_type(t[1]):
                if text_buf:
                    segments.append(('text', text_buf))
                    text_buf = []
                group = [t]
                i += 1
                while i < len(tokens):
                    t2 = tokens[i]
                    group.append(t2)
                    i += 1
                    if self._is_interpol_type(t2[1]):
                        break
                segments.append(('interpol', group))
            else:
                text_buf.append(t)
                i += 1
        if text_buf:
            segments.append(('text', text_buf))
        return segments

    def _try_func_call(self, tokens, i):
        n = len(tokens)
        if i >= n:
            return None, i

        if tokens[i][1] not in Name or tokens[i][2] not in FUNC_SUBLANG:
            return None, i
        func_name = tokens[i][2]
        func_token = tokens[i]
        idx = i + 1

        while idx < n and self._is_text_type(tokens[idx][1]):
            idx += 1
        if idx >= n or tokens[idx][2] != "(":
            return None, i
        paren_token = tokens[idx]
        idx += 1

        while idx < n and self._is_text_type(tokens[idx][1]):
            idx += 1
        if idx >= n:
            return None, i

        affix = ""
        str_start = idx
        if self._is_string_type(tokens[idx][1]) and tokens[idx][2] in ("f", "F"):
            affix = tokens[idx][2]
            idx += 1
            if idx >= n:
                return None, i

        if not (self._is_string_type(tokens[idx][1])):
            return None, i
        open_delim = tokens[idx][2]
        open_delim_token = tokens[idx]
        idx += 1
        if idx >= n:
            return None, i

        content_tokens = []
        close_token = None
        while idx < n:
            t = tokens[idx]
            if t[2] == open_delim and self._is_string_type(t[1]):
                close_token = t
                idx += 1
                break
            content_tokens.append(t)
            idx += 1

        if close_token is None:
            return None, i

        lang = FUNC_SUBLANG[func_name]

        skip_sublang_inner = False
        if open_delim in TRIPLE_DELIMS:
            inner_text = "".join(t[2] for t in content_tokens)
            detected, first_word = self._detect_sublang(inner_text)
            if detected:
                lang = detected
                skip_sublang_inner = True

        sub_lexer = self._get_lexer(lang)

        result = []
        result.append((func_token[0], Name.Function, func_token[2]))
        result.append((paren_token[0], Punctuation, "("))
        if affix:
            result.append((tokens[str_start][0], String.Affix, affix))
        result.append((open_delim_token[0], String, open_delim))
        seg_start = 0
        if skip_sublang_inner:
            result.append((content_tokens[0][0], Comment, first_word))
            seg_start = 1
        for seg_type, seg_tokens in self._split_segments(content_tokens[seg_start:]):
            if seg_type == 'text':
                seg_text = "".join(t[2] for t in seg_tokens)
                if sub_lexer and seg_text:
                    base = seg_tokens[0][0]
                    for sp, st, sv in sub_lexer.get_tokens_unprocessed(seg_text):
                        result.append((base + sp, st, sv))
                elif seg_text:
                    result.append((seg_tokens[0][0], String, seg_text))
            else:
                for t in seg_tokens:
                    result.append(t)
        result.append((close_token[0], String, close_token[2]))
        return result, idx
