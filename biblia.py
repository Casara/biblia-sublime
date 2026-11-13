"""Sublime Text integration for the `biblia` command-line tool.

Commands (see Default.sublime-commands and Default.sublime-keymap):

- biblia_consultar: shows the text of the selected reference (or of the
  reference on the cursor line) in a popup, without touching the file.
- biblia_inserir:   replaces each selected reference with its text.
- biblia_perguntar: asks for a reference in the input panel and shows it.
- biblia_paralelos: shows the selected reference with the list of its
  parallel passages.
- biblia_inserir_paralelos: keeps each selected reference and inserts the
  text of its parallel passages on the lines after it.
- biblia_original: shows the selected reference with the original
  Hebrew/Greek words (-s) in a read-only "Bíblia" tab.
- biblia_strong: lexicon entry of the Strong number under the cursor (in
  that tab too), or a search by transliteration or gloss.
- biblia_consultar_versoes / biblia_inserir_versoes: ask for the
  translations of this run, then work like biblia_consultar /
  biblia_inserir.

The interlinear and the lexicon go to a tab, not to the popup: they are
aligned in columns, which the popup's proportional font would break, and
the cursor can stand on a Strong number there.

Settings (Preferences > Package Settings, or biblia.sublime-settings):
  "executavel": path to the binary (default "biblia", from PATH)
  "versoes":    e.g. "ara,naa" (empty = the tool's own config)
  "formato":    format of the insert commands; "auto" (default) picks it
                from the file: "formatos_por_extensao", then the syntax
                (Markdown, Typst); any other file gets the tool's own
                "formato_filtro"
"""

import html
import os
import re
import shutil
import subprocess

import sublime
import sublime_plugin

SETTINGS = "biblia.sublime-settings"


def _settings():
    return sublime.load_settings(SETTINGS)


# Where "make install" and "go install" put the binary. Sublime started
# from the desktop does not read the shell profile, so these folders are
# often missing from its PATH even when the terminal finds "biblia".
_FALLBACK_DIRS = ("~/.local/bin", "~/go/bin")

_WINDOWS = sublime.platform() == "windows"


def _executable():
    """The configured binary, looked up in PATH and then in the usual
    install folders when only a bare name is configured."""
    exe = _settings().get("executavel", "biblia")
    if os.path.dirname(exe) or shutil.which(exe):
        return exe
    names = [exe + ".exe", exe] if _WINDOWS else [exe]
    for folder in _FALLBACK_DIRS:
        for name in names:
            candidate = os.path.join(os.path.expanduser(folder), name)
            if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
                return candidate
    return exe


def _startupinfo():
    """On Windows, keeps a console window from flashing at each call."""
    if not _WINDOWS:
        return None
    info = subprocess.STARTUPINFO()
    info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    return info


# _CONFIG makes _run take the translations from the settings.
_CONFIG = object()


def _run(args, stdin=None, versions=_CONFIG):
    """Runs biblia and returns (stdout, stderr, returncode).

    versions picks the "-v" argument: _CONFIG takes "versoes" from the
    settings, a string overrides it for this run, and None sends none
    ("strong" and "versoes" have no -v flag and would refuse it).
    """
    exe = _executable()
    if versions is _CONFIG:
        versions = _settings().get("versoes", "")
    cmd = [exe] + args
    if versions:
        cmd += ["-v", versions]
    try:
        proc = subprocess.run(
            cmd,
            input=stdin,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
            startupinfo=_startupinfo(),
        )
    except FileNotFoundError:
        return "", "biblia: executável não encontrado ({})".format(exe), 127
    except subprocess.TimeoutExpired:
        return "", "biblia: tempo esgotado", 124
    return proc.stdout, proc.stderr, proc.returncode


# Syntax scopes of files without an extension in formatos_por_extensao.
_FORMAT_BY_SCOPE = (("markdown", "md"), ("typst", "typ"))


def _format_args(view):
    """The "-f" arguments for a view, or none to use the tool's default."""
    chosen = _settings().get("formato", "auto")
    if chosen != "auto":
        return ["-f", chosen]

    by_ext = _settings().get("formatos_por_extensao", {})
    ext = os.path.splitext(view.file_name() or "")[1].lower()
    if ext in by_ext:
        return ["-f", by_ext[ext]]

    scope = view.scope_name(0)
    for name, fmt in _FORMAT_BY_SCOPE:
        if name in scope:
            return ["-f", fmt]

    return []


def _selected_refs(view):
    return "; ".join(view.substr(r).strip() for r in _reference_regions(view))


def _reference_regions(view):
    """Non-empty selections, or the cursor line when nothing is selected."""
    out = []
    for region in view.sel():
        if region.empty():
            region = view.line(region)
        out.append(region)
    return out


def _show(view, text, error):
    body = html.escape(text.strip() or error.strip()).replace("\n", "<br>")
    view.show_popup(
        "<div style='padding: 6px; max-width: 70em'>{}</div>".format(body),
        max_width=900,
        max_height=600,
    )


def _show_page(window, kind, name, text, error):
    """Shows text in the window's read-only "Bíblia" tab of that kind
    ("original" or "strong"), created on first use, or the error in the
    status bar when there is no text. One tab per kind, so looking up a
    Strong number from the interlinear leaves the interlinear in place."""
    if not text.strip():
        sublime.status_message(error.strip() or "Bíblia: nada encontrado.")
        return
    page = next((v for v in window.views() if v.settings().get("biblia_page") == kind), None)
    if page is None:
        page = window.new_file()
        page.set_scratch(True)
        page.settings().set("biblia_page", kind)
        page.settings().set("word_wrap", False)
    page.set_name("Bíblia: " + name)
    page.set_read_only(False)
    page.run_command("biblia_replace_page", {"text": text})
    page.set_read_only(True)
    window.focus_view(page)
    if error.strip():
        sublime.status_message(error.strip().splitlines()[-1])


class BibliaReplacePageCommand(sublime_plugin.TextCommand):
    """Internal: replaces the whole text of the "Bíblia" tab."""

    def run(self, edit, text):
        self.view.replace(edit, sublime.Region(0, self.view.size()), text)
        self.view.sel().clear()
        self.view.sel().add(sublime.Region(0))
        self.view.show(0)


class BibliaConsultarCommand(sublime_plugin.TextCommand):
    def run(self, edit, versoes=None):
        args = ["-f", "texto", _selected_refs(self.view)]
        out, err, _ = _run(args, versions=versoes or _CONFIG)
        _show(self.view, out, err)


class BibliaOriginalCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        refs = _selected_refs(self.view)
        if not refs.strip():
            return
        out, err, _ = _run(["-f", "texto", "-s", refs])
        _show_page(self.view.window(), "original", refs + " (original)", out, err)


# A Strong number as the tool takes it: G25, g0025, H7451b, H2603A.
_STRONG = re.compile(r"\b[HGhg]\d{1,4}[A-Za-z]?\b")


def _strong_under_cursor(view):
    """The selected text, or the Strong number the cursor stands on (a
    whole interlinear line would carry the word and the gloss too)."""
    sel = view.sel()
    if not sel:
        return ""
    region = sel[0]
    if not region.empty():
        return view.substr(region).strip()
    line = view.line(region.b)
    col = region.b - line.a
    for m in _STRONG.finditer(view.substr(line)):
        if m.start() <= col <= m.end():
            return m.group(0)
    return ""


class BibliaStrongCommand(sublime_plugin.TextCommand):
    def run(self, edit, query=None):
        window = self.view.window()
        query = query or _strong_under_cursor(self.view)
        if _STRONG.fullmatch(query):
            self._number(window, query)
            return
        window.show_input_panel(
            "Strong (H2617, G25), transliteração ou glosa (grego: em espanhol):",
            query.split("\n")[0],
            lambda text: self._ask(window, text.strip()),
            None,
            None,
        )

    def _number(self, window, number):
        out, err, _ = _run(["strong", number, "-c"], versions=None)
        _show_page(window, "strong", number.upper(), out, err)

    def _ask(self, window, text):
        if not text:
            return
        if _STRONG.fullmatch(text):
            self._number(window, text)
            return
        choices = [("Transliteração", "-tr"), ("Glosa", "-glosa")]

        def on_done(i):
            if i < 0:
                return
            label, flag = choices[i]
            out, err, _ = _run(["strong", flag, text], versions=None)
            _show_page(window, "strong", "{}: {}".format(label, text), out, err)

        window.show_quick_panel(
            ["{}: strong {} {}".format(label, flag, text) for label, flag in choices],
            on_done,
        )


# The last translations asked for, offered again at the next run.
_last_versions = ""


def _ask_versions(view, command):
    """Asks for the translations of one run, then runs command on view with
    them."""

    def on_done(text):
        global _last_versions
        text = ",".join(v.strip() for v in text.split(",") if v.strip())
        if not text:
            return
        _last_versions = text
        view.run_command(command, {"versoes": text})

    view.window().show_input_panel(
        "Traduções (ex.: ara,naa,nvi; lista: biblia versoes):",
        _last_versions or _settings().get("versoes", ""),
        on_done,
        None,
        None,
    )


class BibliaConsultarVersoesCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        _ask_versions(self.view, "biblia_consultar")


class BibliaInserirVersoesCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        _ask_versions(self.view, "biblia_inserir")


class BibliaParalelosCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        out, err, _ = _run(["-f", "texto", "-p", _selected_refs(self.view)])
        _show(self.view, out, err)


class BibliaInserirParalelosCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        fmt = _format_args(self.view)
        inserted = False
        # Bottom-up, so earlier insertions do not shift later regions.
        for region in reversed(_reference_regions(self.view)):
            text = self.view.substr(region)
            out, err, _ = _run(["filtro", "-p"] + fmt, stdin=text)
            if err:
                sublime.status_message(err.strip().splitlines()[-1])
            out = out.rstrip("\n")
            if out:
                self.view.insert(edit, region.end(), "\n" + out)
                inserted = True
        if not inserted:
            sublime.status_message("Bíblia: nenhuma passagem paralela no banco da UBS.")


class BibliaInserirCommand(sublime_plugin.TextCommand):
    def run(self, edit, versoes=None):
        fmt = _format_args(self.view)
        # Bottom-up, so earlier replacements do not shift later regions.
        for region in reversed(_reference_regions(self.view)):
            text = self.view.substr(region)
            out, err, _ = _run(["filtro"] + fmt, stdin=text, versions=versoes or _CONFIG)
            if err:
                sublime.status_message(err.strip().splitlines()[-1])
            if out:
                self.view.replace(edit, region, out.rstrip("\n"))


class BibliaPerguntarCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.show_input_panel("Referência:", "", self.on_done, None, None)

    def on_done(self, ref):
        view = self.window.active_view()
        if not ref.strip() or view is None:
            return
        out, err, _ = _run(["-f", "texto", ref])
        _show(view, out, err)
