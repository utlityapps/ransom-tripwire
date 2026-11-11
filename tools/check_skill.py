#!/usr/bin/env python3
"""Independent re-implementation of the Uliya Skill static checks (uliya-skill-kit 0.7.3-en).

The official checker is `node uliya-skill-kit/scripts/check-skill.mjs <skill-dir>`. This script ports
its published rules to Python so the package can be checked where the official kit cannot run.
It is a cross-check, not a replacement: run the official checker before uploading.

Usage: python3 tools/check_skill.py skill/ransom-tripwire
Exit code: 0 = no errors, 1 = errors, 2 = bad usage.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SINGLE_FILE_MAX = 1024 * 1024
PACKAGE_MAX = 10 * 1024 * 1024
PACKAGE_MAX_FILES = 100
BODY_RECOMMENDED_LINES = 500
CLI_AGENTS = {
    "ug-music": "media-agent",
    "ug-video": "media-agent",
    "ug-surveillance": "security-monitor-agent",
    "ug-filesystem": "file-agent",
    "ug-filemgr": "file-agent",
    "file-workflow": "file-agent",
    "ug-document": "document-agent",
    "ug-knowledge": "knowledge-agent",
    "ug-photo": "photo-agent",
}
ALLOWED_AGENTS = set(CLI_AGENTS.values())
STATUS_TOKENS = ["completed", "failed", "cancelled", "waiting_user", "waiting_approval"]

PRIVATE_KEY = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")
CREDENTIAL = re.compile(r"\b(?:password|passwd|token|api[_-]?key|secret)\s*[:=]\s*[\"'][^\"'\n]+[\"']", re.I)
REMOTE_DOWNLOAD = re.compile(r"\b(?:curl|wget)\b|https?://\S+\s*\|\s*(?:sh|bash)\b", re.I)
RUNTIME_FENCE = re.compile(r"^```\s*(?:bash|sh|shell|python|py|javascript|js|node|typescript|ts)\b", re.I)
DIRECT_FILE_API = re.compile(r"\b(?:readFile|writeFile|unlink|pathlib|fs\.|open\s*\(|cp\s+|mv\s+|rm\s+|cat\s+)\b", re.I)
HTTP_CALL = re.compile(r"\b(?:fetch|axios|XMLHttpRequest|http\.request|https\.request)\s*\(", re.I)
NAS_PATH = re.compile(r"(?:^|[\s\"'])/(?:nas|mnt|volume\d*|shares?)(?:/|\b)", re.I)
BYPASS = re.compile(r"\b(?:bypass|skip|disable|ignore|绕过|跳过|关闭)\b[^\n]{0,40}\b(?:gateway|approval|permission|audit|审批|权限|审计)\b", re.I)
INTERNAL = re.compile(r"\b(?:ug-ai|HERMES(?:\s+action)?|Host CLI|expert[-_ ]?id|correlation[-_ ]?id|request[-_ ]?id)\b", re.I)
COMPACT = re.compile(r"\b(?:compact-main-agent|compact-unified-agent|compact profile)\b", re.I)
CLI_INVOKE = re.compile(r"\bcli\.invoke\b")
CLI_INVOKE_NEGATED = re.compile(
    r"(?:不|不要|不得|禁止|避免)[^\n]{0,24}(?:直接)?(?:执行|调用|使用)?\s*`?cli\.invoke\b|"
    r"(?:do not|don't|never|must not|without)[^\n]{0,24}\bcli\.invoke\b",
    re.I,
)
DESC_TRIGGER = re.compile(r"(?:当用户|用户(?:说|问|要|需要|希望|要求|提到)|适用于|使用于|用于|供[^，。;；]{1,40}使用|when\b|use when\b)", re.I)
DESC_SPLIT = re.compile(r"(?:当用户|用户(?:说|问|要|需要|希望|要求|提到)|when\b|use when\b)", re.I)
DESC_EXEC_DETAIL = re.compile(r"(?:先[^，。;；]{0,24}(?:再|然后)|保存到|存到|输出到|按[^，。;；]{0,20}(?:排序|分组|归档)|不要|不得|不删除|只报告)")
DESC_IMPERATIVE = re.compile(r"^\s*(?:生成|创建|整理出|产出|输出|汇总出|做一份|出一份)")
HOME_PATH = re.compile(r"/home/(?!<|\{|\$|某个?用户|用户名|user(?:name)?\b)[A-Za-z0-9._-]+(?:/|\b)", re.I)
DYNAMIC = re.compile(r"<[^>\n]{1,80}>|(?:该路径|该目录|上一步(?:的)?(?:路径|目录|结果|文件|文本|内容|ID|标识)|刚才(?:的)?(?:结果|路径|目录|内容))", re.I)
QUERY_INTENT = re.compile(r"(?:查询|查找|搜索|筛选|扫描|盘点|检索|列出|浏览|query|search|find|scan|filter|list|report)", re.I)
EMPTY_RESULT = re.compile(r"(?:空结果|空列表|空集合|无结果|无匹配(?:结果|项)?|没有匹配|没有找到|未找到|目录为空|返回为空|no results?|empty (?:result|list|set)|zero matches?)", re.I)
REAL_RESULT = re.compile(r"(真实|real)[^\n]{0,40}(结果|result)|上一步|upstream|下游|downstream", re.I)
PLACEHOLDER = re.compile(r"replace-with-|\bTODO\b|\bTBD\b|待定")
SECTIONS = [
    (re.compile(r"^# (?:目标|Goal)\s*$", re.M | re.I), "Goal"),
    (re.compile(r"^# (?:必需输入|Required input)\s*$", re.M | re.I), "Required input"),
    (re.compile(r"^# (?:专家编排|Workflow|Orchestration)\s*$", re.M | re.I), "Workflow"),
    (re.compile(r"^# (?:完成与失败|Failure handling|Completion and failure)\s*$", re.M | re.I), "Completion and failure"),
]
EVIDENCE_HEADING = re.compile(r"^# (?:生成期能力依据|Generation-time capability evidence)\s*$", re.M | re.I)
EVIDENCE_LINE = re.compile(r"^\s*-\s+`([a-z][a-z0-9-]*)`\s+→\s+`([a-z][a-z0-9-]*)`\s*$", re.M)
LINK = re.compile(r"\]\((references/[^)\s#]+\.md)\)")


class Report:
    def __init__(self) -> None:
        self.items: list[tuple[str, str, str, str]] = []

    def add(self, code: str, severity: str, where: str, message: str) -> None:
        self.items.append((severity, code, where, message))

    @property
    def errors(self) -> int:
        return sum(1 for s, *_ in self.items if s == "error")

    @property
    def warnings(self) -> int:
        return sum(1 for s, *_ in self.items if s == "warning")


def parse_frontmatter(source: str, r: Report) -> tuple[dict[str, str], str]:
    m = re.match(r"^---\r?\n([\s\S]*?)\r?\n---\r?\n?", source)
    if not m:
        r.add("SKILL_FRONTMATTER_INVALID", "error", "SKILL.md", "missing frontmatter")
        return {}, source
    values: dict[str, str] = {}
    for line in m.group(1).splitlines():
        kv = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not kv:
            r.add("SKILL_FRONTMATTER_INVALID", "error", "SKILL.md", f"not a simple key: value line: {line!r}")
            continue
        key, value = kv.group(1), kv.group(2).strip()
        if key not in ("name", "description") or key in values or not value:
            r.add("SKILL_FRONTMATTER_INVALID", "error", "SKILL.md", f"only non-empty, unique name and description allowed: {key}")
        values[key] = value
    for key in ("name", "description"):
        if key not in values:
            r.add("SKILL_FRONTMATTER_INVALID", "error", "SKILL.md", f"frontmatter missing {key}")
    return values, source[m.end():]


def check_markdown(source: str, r: Report) -> dict[str, str]:
    fm, body = parse_frontmatter(source, r)
    for pattern, label in SECTIONS:
        if not pattern.search(body):
            r.add("SKILL_REQUIRED_SECTION_MISSING", "error", "SKILL.md", f"missing section: {label}")
    for m in PLACEHOLDER.finditer(source):
        r.add("SKILL_PLACEHOLDER_REMAINS", "error", f"SKILL.md:{source.count(chr(10), 0, m.start()) + 1}", m.group(0))
    name = fm.get("name", "")
    if name and not 2 <= len(name) <= 64:
        r.add("SKILL_NAME_LENGTH_INVALID", "error", "SKILL.md:2", f"{len(name)} characters")
    desc = fm.get("description", "")
    if desc:
        if len(desc) > 1024:
            r.add("DESCRIPTION_LENGTH_EXCEEDED", "error", "SKILL.md:3", f"{len(desc)} characters")
        if not DESC_TRIGGER.search(desc):
            r.add("DESCRIPTION_TRIGGER_MISSING", "warning", "SKILL.md:3", "no user trigger phrase")
        head = DESC_SPLIT.split(desc)[0]
        if DESC_EXEC_DETAIL.search(head):
            r.add("DESCRIPTION_EXECUTION_DETAIL", "warning", "SKILL.md:3", "execution detail in description")
        if DESC_IMPERATIVE.search(head):
            r.add("DESCRIPTION_IMPERATIVE_STYLE", "warning", "SKILL.md:3", "imperative description")
    lines = len(body.splitlines())
    if lines > BODY_RECOMMENDED_LINES:
        r.add("SKILL_BODY_LINES_RECOMMENDATION_EXCEEDED", "warning", "SKILL.md", f"{lines} body lines")
    return fm


def delegate_command(line: str, start: int) -> str:
    if start > 0 and line[start - 1] == "`":
        end = line.find("`", start)
        if end != -1:
            return line[start:end]
    return line[start:].rstrip().rstrip("`").rstrip()


def check_delegates(source: str, r: Report) -> list[tuple[str, int]]:
    targets: list[tuple[str, int]] = []
    count = 0
    for i, line in enumerate(source.splitlines(), 1):
        start = line.find("delegate --")
        if start == -1:
            continue
        count += 1
        where = f"SKILL.md:{i}"
        cmd = delegate_command(line, start)
        if re.search(r"\$\(|`[^`]+`|\|\||&&|\s[|<>]\s", cmd):
            r.add("DELEGATE_FORMAT_INVALID", "error", where, "pipe, redirect, substitution or chaining")
            continue
        tgt = list(re.finditer(r"(?:^|\s)--target(?:\s+([^\s]+))?", cmd))
        ins = list(re.finditer(r"(?:^|\s)--instruction(?:\s+('(?:[^']|'\"'\"')*'|\"[^\"]*\"|[^\s]+))?", cmd))
        if len(tgt) != 1 or len(ins) != 1 or re.search(r"\s--(?!target\b|instruction\b)[a-z0-9-]+", cmd, re.I):
            r.add("DELEGATE_FORMAT_INVALID", "error", where, "exactly one --target and one --instruction")
            continue
        target = (tgt[0].group(1) or "").rstrip("`*_")
        raw = ins[0].group(1) or ""
        if not target:
            r.add("DELEGATE_FORMAT_INVALID", "error", where, "missing target")
        elif target not in ALLOWED_AGENTS:
            r.add("DELEGATE_TARGET_UNKNOWN", "error", where, target)
        else:
            targets.append((target, i))
        if raw in ("", "''", '""'):
            r.add("DELEGATE_INSTRUCTION_EMPTY", "error", where, "empty instruction")
        if not re.fullmatch(r"'(?:[^']|'\"'\"')*'", raw):
            r.add("DELEGATE_FORMAT_INVALID", "error", where, "instruction must use single quotes")
        if HOME_PATH.search(raw):
            r.add("DELEGATE_HARDCODED_HOME_PATH", "warning", where, "hard-coded home path")
        if DYNAMIC.search(raw):
            r.add("DELEGATE_DYNAMIC_VALUE_UNRESOLVED", "warning", where, DYNAMIC.search(raw).group(0))
    if count == 0:
        r.add("DELEGATION_WORKFLOW_STATIC_VALIDATION_INCOMPLETE", "warning", "SKILL.md", "no delegate commands")
    missing = [t for t in STATUS_TOKENS if t not in source]
    if missing:
        r.add("DELEGATION_RESULT_HANDLING_MISSING", "error", "SKILL.md", ", ".join(missing))
    if count > 1 and not REAL_RESULT.search(source):
        r.add("DELEGATION_WORKFLOW_STATIC_VALIDATION_INCOMPLETE", "warning", "SKILL.md", "no real-result passing statement")
    if count > 0 and QUERY_INTENT.search(source) and not EMPTY_RESULT.search(source):
        r.add("EMPTY_RESULT_HANDLING_MISSING", "warning", "SKILL.md", "no empty-result handling")
    return targets


def check_evidence(source: str, targets: list[tuple[str, int]], r: Report) -> None:
    heading = EVIDENCE_HEADING.search(source)
    evidence = []
    if heading:
        rest = source[heading.end():]
        nxt = re.search(r"^#\s+", rest, re.M)
        section = rest[: nxt.start()] if nxt else rest
        evidence = EVIDENCE_LINE.findall(section)
    if targets and not evidence:
        r.add("CAPABILITY_EVIDENCE_MISSING", "error", "SKILL.md", "no capability evidence section")
        return
    agents, seen = set(), set()
    for cli, agent in evidence:
        if cli in seen:
            r.add("CAPABILITY_EVIDENCE_DUPLICATE", "error", "SKILL.md", cli)
            continue
        seen.add(cli)
        if cli not in CLI_AGENTS:
            r.add("CAPABILITY_EVIDENCE_CLI_UNKNOWN", "error", "SKILL.md", cli)
        elif CLI_AGENTS[cli] != agent:
            r.add("CAPABILITY_EVIDENCE_AGENT_MISMATCH", "error", "SKILL.md", f"{cli} -> {agent}")
        else:
            agents.add(agent)
    for target, line in targets:
        if target not in agents:
            r.add("DELEGATE_TARGET_EVIDENCE_MISSING", "error", f"SKILL.md:{line}", target)


def scan_security(name: str, source: str, r: Report) -> None:
    for i, line in enumerate(source.splitlines(), 1):
        where = f"{name}:{i}"
        checks = [
            (RUNTIME_FENCE.search(line), "SECURITY_SCRIPT_EXECUTION_UNSUPPORTED"),
            (PRIVATE_KEY.search(line) or CREDENTIAL.search(line), "SECURITY_CREDENTIAL_LITERAL"),
            (REMOTE_DOWNLOAD.search(line), "SECURITY_REMOTE_DOWNLOAD"),
            (CLI_INVOKE.search(line) and not CLI_INVOKE_NEGATED.search(line), "RUNTIME_DIRECT_CLI_INVOKE"),
            (INTERNAL.search(line), "SECURITY_INTERNAL_CAPABILITY"),
            (COMPACT.search(line), "RUNTIME_PROFILE_UNSUPPORTED"),
            (BYPASS.search(line), "SECURITY_GATEWAY_BYPASS"),
            (
                "delegate --" not in line and (DIRECT_FILE_API.search(line) or HTTP_CALL.search(line) or NAS_PATH.search(line)),
                "SECURITY_DIRECT_FILE_ACCESS",
            ),
        ]
        for hit, code in checks:
            if hit:
                r.add(code, "error", where, line.strip()[:100])


def check(skill_dir: Path) -> Report:
    r = Report()
    if not (skill_dir / "SKILL.md").is_file():
        r.add("FILE_REQUIRED_MISSING", "error", "SKILL.md", "missing")
        return r
    files = [p for p in skill_dir.rglob("*") if p.is_file()]
    if len(files) > PACKAGE_MAX_FILES:
        r.add("PACKAGE_FILE_COUNT_EXCEEDED", "error", str(skill_dir), f"{len(files)} files")
    if sum(p.stat().st_size for p in files) > PACKAGE_MAX:
        r.add("PACKAGE_SIZE_EXCEEDED", "error", str(skill_dir), "over 10 MB")
    for entry in skill_dir.iterdir():
        if entry.name == "SKILL.md" or (entry.name == "references" and entry.is_dir() and not entry.is_symlink()):
            continue
        r.add("RESOURCE_UNSUPPORTED", "error", entry.name, "root may hold only SKILL.md and references/")
    sources: dict[str, str] = {}
    for p in files:
        rel = p.relative_to(skill_dir).as_posix()
        if p.is_symlink():
            r.add("RESOURCE_PATH_INVALID", "error", rel, "symbolic link")
            continue
        if p.stat().st_size > SINGLE_FILE_MAX:
            r.add("FILE_SIZE_EXCEEDED", "error", rel, "over 1 MB")
        if rel != "SKILL.md" and not rel.endswith(".md"):
            r.add("RESOURCE_UNSUPPORTED", "error", rel, "references may hold only Markdown")
            continue
        sources[rel] = p.read_text(encoding="utf-8")
    skill = sources["SKILL.md"]
    fm = check_markdown(skill, r)
    name = fm.get("name", "")
    if name and not SKILL_NAME.match(name):
        r.add("SKILL_NAME_INVALID", "error", "SKILL.md:2", name)
    elif name and name != skill_dir.name:
        r.add("SKILL_NAME_MISMATCH", "error", "SKILL.md:2", f"{name} != {skill_dir.name}")
    links = set(LINK.findall(skill))
    for rel in sources:
        if rel != "SKILL.md" and rel not in links:
            r.add("RESOURCE_UNREFERENCED", "warning", rel, "not linked from SKILL.md")
    for link in links:
        if link not in sources:
            r.add("RESOURCE_PATH_INVALID", "error", "SKILL.md", f"broken link {link}")
    targets = check_delegates(skill, r)
    check_evidence(skill, targets, r)
    for rel, text in sources.items():
        scan_security(rel, text, r)
    return r


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    report = check(Path(argv[1]))
    for severity, code, where, message in report.items:
        print(f"{severity.upper():7} {code:48} {where}  {message}")
    status = "static-pass" if report.errors == 0 else "not-uploadable"
    print(f"\n{status}: {report.errors} error(s), {report.warnings} warning(s)")
    return 0 if report.errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
