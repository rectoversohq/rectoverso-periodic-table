#!/usr/bin/env python3
"""Render every exported front/back with Anki's bundled reviewer and Qt WebEngine."""

import argparse
import json
import time
from pathlib import Path
from PyQt6.QtCore import QTimer, QUrl
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWebEngineCore import (
    QWebEnginePage,
    QWebEngineProfile,
    QWebEngineUrlRequestInterceptor,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView

ROOT = Path(__file__).resolve().parents[2]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--evidence", type=Path, required=True)
p.add_argument("--web", type=Path, required=True)
p.add_argument("--out", type=Path, required=True)
p.add_argument("--sample", action="store_true")
p.add_argument(
    "--document-delay-ms",
    type=int,
    default=0,
    help="Exercise asynchronous navigation with a delayed document load",
)
p.add_argument(
    "--parser-delay-ms",
    type=int,
    default=0,
    help="Pause answer parsing after its caption script to test initialization order",
)
a = p.parse_args()
if not 0 <= a.document_delay_ms <= 2000:
    p.error("--document-delay-ms must be between 0 and 2000")
if not 0 <= a.parser_delay_ms <= 2000:
    p.error("--parser-delay-ms must be between 0 and 2000")
a.out.mkdir(parents=True, exist_ok=False)
app = QApplication(["periodic-table-native-review"])
profile = QWebEngineProfile()
profile.setCachePath(str(a.out / "qt-cache"))
profile.setPersistentStoragePath(str(a.out / "qt-storage"))
# A blocking resource makes the parser yield after Back Extra's caption script.
# It exercises real browser ordering without changing the script or its assertions.
if a.parser_delay_ms:
    parser_gate = a.out / "parser-gate.js"
    parser_gate.write_text("// Deliberate parser-order regression fixture.\n")

    class ParserDelay(QWebEngineUrlRequestInterceptor):
        def interceptRequest(self, info):
            if info.requestUrl().fileName() == "parser-gate.js":
                time.sleep(a.parser_delay_ms / 1000)

    parser_delay = ParserDelay()
    profile.setUrlRequestInterceptor(parser_delay)
errors = []


class Page(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, line, source):
        errors.append({"level": str(level), "message": message})


view = QWebEngineView()
page = Page(profile, view)
view.setPage(page)
view.resize(1200, 900)
view.show()
names = {
    lang: json.loads((ROOT / f"source/translations/{lang}.json").read_text())
    for lang in ("en", "fr")
}
selected = {1, 8, 26, 57, 71, 103, 117, 118}
items = []
for lang in names:
    for theme in ("light", "dark"):
        for z in range(1, 119):
            if a.sample and z not in selected:
                continue
            for side in ("question", "answer"):
                items.append((lang, theme, z, side))
results = []
current = None
started = 0
finished = False


def finish(error=None):
    global finished
    if finished:
        return
    finished = True
    report = {
        "pages": len(results),
        "expected": 64 if a.sample else 944,
        "passed": sum(x["passed"] for x in results),
        "failures": [x for x in results if not x["passed"]],
        "results": results,
        "fatal": error,
    }
    (a.out / "render-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    )
    print(
        json.dumps(
            {k: v for k, v in report.items() if k not in ("results", "failures")}
            | {"failureCount": len(report["failures"])}
        )
    )
    app.quit()


def start():
    global current, started
    if not items:
        finish()
        return
    current = items.pop(0)
    lang, theme, z, side = current
    errors.clear()
    started = time.monotonic()
    body = (a.evidence / lang / f"{z:03d}-{side}.html").read_text()
    if side == "answer" and a.parser_delay_ms:
        body = body.replace(
            "</script>",
            f'</script><script src="{parser_gate.as_uri()}?{lang}-{theme}-{z}"></script>',
            1,
        )
    cls = "card nightMode" if theme == "dark" else "card"
    document = '<!doctype html><html><head><meta charset="utf-8"><script>window.pycmd=()=>{};</script>'
    document += f'<link rel="stylesheet" href="{(a.web / "css/reviewer.css").as_uri()}"><script src="{(a.web / "js/reviewer.js").as_uri()}"></script>'
    # Observe Anki's own completed draw; never replace its shapes or rendering.
    document += """<script>
const originalSetup = anki.imageOcclusion.setup;
anki.imageOcclusion.setup = function(options = {}) {
  return originalSetup.call(this, {...options, onDidDrawShapes: (...args) => {
    options.onDidDrawShapes?.(...args);
    window.rvReviewDrawn = true;
  }});
};
</script>"""
    case = "-".join(map(str, current))
    document += (
        f'</head><body class="{cls}" data-rv-review-case="{case}">{body}</body></html>'
    )

    def load_document():
        view.setHtml(
            document, QUrl.fromLocalFile(str(a.evidence / lang / "source.media") + "/")
        )

    QTimer.singleShot(a.document_delay_ms, load_document)
    QTimer.singleShot(0, poll)


def poll():
    lang, theme, z, side = current
    case = json.dumps("-".join(map(str, current)))
    script = """(() => {if(document.body?.dataset.rvReviewCase !== CASE || document.readyState !== "complete" || !window.rvReviewDrawn)return null;const c=document.querySelector('canvas'),img=document.querySelector('#image-occlusion-container img');if(!c||!c.width||!img?.complete)return null;
 const target=document.querySelector('.cloze,.cloze-highlight');let alpha=null,pixelError=null;
 try{const d=target.dataset;alpha=c.getContext('2d').getImageData((+d.left + +d.width/2)*c.width,(+d.top + +d.height/2)*c.height,1,1).data[3];}catch(e){pixelError=String(e)}
 return JSON.stringify({api:!!window.anki?.imageOcclusion,canvas:[c.width,c.height],image:img.getAttribute('src'),ordinal:+target?.dataset.ordinal,targetClass:target?.className,alpha,pixelError,names:[...document.querySelectorAll('.rv-fact:not([hidden]) .rv-name')].map(e=>e.textContent),detail:[...document.querySelectorAll('.rv-fact:not([hidden]) .rv-detail')].map(e=>e.textContent),error:document.getElementById('err')?.textContent,metadata:document.body.innerText.includes('RV-OCCLUSION-1:')});})()""".replace(
        "CASE", case
    )

    def ready(value):
        if not value:
            if time.monotonic() - started > 8:
                finish(f"Timeout: {current}")
            else:
                QTimer.singleShot(80, poll)
            return
        data = json.loads(value)
        data.update(language=lang, theme=theme, ordinalExpected=z, side=side)
        expected_names = [] if side == "question" else [names[lang][str(z)]]
        data["passed"] = (
            data["api"]
            and not data["error"]
            and not data["metadata"]
            and data["ordinal"] == z
            and data["names"] == expected_names
            and data["alpha"] == (255 if side == "question" else 0)
            and data["image"] == f"rv-periodic-{theme}-v2.png"
        )
        if errors:
            data["console"] = list(errors)
        results.append(data)
        if z in selected:
            view.grab().save(str(a.out / f"{lang}-{theme}-{z:03d}-{side}.png"))
        QTimer.singleShot(0, start)

    page.runJavaScript(script, ready)


QTimer.singleShot(0, start)
QTimer.singleShot(900000, lambda: finish("Watchdog"))
app.exec()
if not finished:
    raise SystemExit("Window closed before completion")
report = json.loads((a.out / "render-report.json").read_text())
raise SystemExit(
    0
    if report["pages"] == report["expected"]
    and not report["failures"]
    and not report["fatal"]
    else 1
)
