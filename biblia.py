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


def _run(args, stdin=None):
    """Runs biblia and returns (stdout, stderr, returncode)."""
    exe = _executable()
    versoes = _settings().get("versoes", "")
    cmd = [exe] + args
    if versoes:
        cmd += ["-v", versoes]
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


class BibliaConsultarCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        out, err, _ = _run(["-f", "texto", _selected_refs(self.view)])
        _show(self.view, out, err)


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
    def run(self, edit):
        fmt = _format_args(self.view)
        # Bottom-up, so earlier replacements do not shift later regions.
        for region in reversed(_reference_regions(self.view)):
            text = self.view.substr(region)
            out, err, _ = _run(["filtro"] + fmt, stdin=text)
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
