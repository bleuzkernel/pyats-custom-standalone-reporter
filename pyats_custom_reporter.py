from copy import deepcopy
from typing import Any, Sequence

from pyats.aetest.reporter.default import StandaloneReporter
from pyats.log.utils import banner
# from rich import print

# ──────────────────────────────────────────────────────────────────────────────
# ASCII Banners
# ──────────────────────────────────────────────────────────────────────────────

ASCII_DEATILED_BANNER = r"""
╺┳┓┏━╸╺┳╸┏━┓╻╻  ┏━╸╺┳┓   ┏━┓┏━╸┏━┓╻ ╻╻  ╺┳╸┏━┓
 ┃┃┣╸  ┃ ┣━┫┃┃  ┣╸  ┃┃   ┣┳┛┣╸ ┗━┓┃ ┃┃   ┃ ┗━┓
╺┻┛┗━╸ ╹ ╹ ╹╹┗━╸┗━╸╺┻┛   ╹┗╸┗━╸┗━┛┗━┛┗━╸ ╹ ┗━┛
"""

ASCII_SUMMARY_BANNER = r"""
┏━┓╻ ╻┏┳┓┏┳┓┏━┓┏━┓╻ ╻
┗━┓┃ ┃┃┃┃┃┃┃┣━┫┣┳┛┗┳┛
┗━┛┗━┛╹ ╹╹ ╹╹ ╹╹┗╸ ╹ 
"""


# ──────────────────────────────────────────────────────────────────────────────
# Labesl to Emoji mapping
# ──────────────────────────────────────────────────────────────────────────────

RESULT_TO_EMOJI: dict[str, str] = {
    "ABORTED": "🟡",
    "BLOCKED": "🚫",
    "ERRORED": "🚨",
    "FAILED": " ❌",
    "PASSED": " ✅",
    "PASSX": "  ✅",
    "SKIPPED": "⏭️",
}


# ──────────────────────────────────────────────────────────────────────────────
# Utilities
# ──────────────────────────────────────────────────────────────────────────────


def pad_to_column_len(left: str, target_col: int, min_gap: int = 1) -> str:
    gap = max(min_gap, target_col - len(left))
    return left + (" " * gap)


# ──────────────────────────────────────────────────────────────────────────────
# Reporter
# ──────────────────────────────────────────────────────────────────────────────


class CustomReporter(StandaloneReporter):
    """
    Custom reporter that prints detailed tree with emojis and a summary table."""

    # -------- normalization & replacement --------
    @staticmethod
    def _normalize_result_key(value: Any) -> str | None:
        for attr in ("name", "value"):
            if hasattr(value, attr):
                try:
                    raw = getattr(value, attr)
                    if isinstance(raw, str):
                        return raw.upper() if raw else None
                except Exception:
                    pass
        if isinstance(value, str):
            return raw.upper() if raw else None
        return None

    @classmethod
    def _with_emoji(cls, value: Any) -> str:
        key = cls._normalize_result_key(value)
        return f"{key} {RESULT_TO_EMOJI[key]}" if key else str(value)

    def _replace_results(self, obj: Any, *, in_place: bool = False) -> Any:
        if not in_place:
            obj = deepcopy(obj)

        def _walk(node: Any) -> Any:
            if isinstance(node, dict):
                if "result" in node:
                    node["result"] = self._with_emoji(node["result"])
                for k, v in list(node.items()):
                    node[k] = _walk(v)
                return node
            if isinstance(node, list):
                return [_walk(x) for x in node]
            if isinstance(node, tuple):
                return tuple(_walk(x) for x in node)
            return node

        return _walk(obj)

    # -------- width (len()) --------
    def _compute_max_span(self, node_or_list: Any, depth: int = 0) -> int:
        if isinstance(node_or_list, list):
            return max(
                (self._compute_max_span(n, depth) for n in node_or_list),
                default=0,
            )
        node = node_or_list
        name = node.get("name", "")
        span_here = (depth * 4) + 4 + len(name)  # indent + connector + name
        children = node.get("sections", []) or []
        return max(
            span_here,
            self._compute_max_span(children, depth + 1)
            if children
            else span_here,
        )

    # -------- printers --------
    def _print_tree(
        self,
        node: dict[str, Any],
        result_col: int,
        prefix: str = "",
        is_last: bool = True,
        depth: int = 0,
    ) -> None:
        connector = "`-- " if is_last else "|-- "
        name = node.get("name", "")
        left = f"{prefix}{connector}{name}"
        print(
            pad_to_column_len(left, result_col, min_gap=2)
            + (node.get("result", "") or "")
        )

        children: list[dict[str, Any]] = node.get("sections", []) or []
        if not children:
            return
        new_prefix = prefix + ("    " if is_last else "|   ")
        for idx, child in enumerate(children):
            last = idx == len(children) - 1
            self._print_tree(child, result_col, new_prefix, last, depth + 1)

    def _print_forest(
        self, roots: Sequence[dict[str, Any]], result_col: int
    ) -> None:
        for i, root in enumerate(roots):
            last_root = i == len(roots) - 1
            self._print_tree(
                root, result_col, prefix="", is_last=last_root, depth=0
            )

    # @staticmethod
    # def _banner(title: str, width: int) -> None:
    #     bar = "=" * width
    #     print(bar)
    #     print(title.center(width))
    #     print(bar)

    # -------- main --------
    def log_summary(self) -> None:
        if not self.section_details:
            print("(no sections)")
            return

        roots: list[dict[str, Any]] = (
            [self.section_details]
            if isinstance(self.section_details, dict)
            else list(self.section_details)
        )
        roots = self._replace_results(roots)

        max_span = self._compute_max_span(roots)
        spacing_compensation = 3
        spacing_headers_compensation = 11
        result_col = max_span + spacing_compensation
        total_width = result_col + spacing_headers_compensation

        # -------- Detailed Results --------
        # self._banner("Detailed Results", total_width)
        print(banner(ASCII_DEATILED_BANNER, width=total_width))
        left_hdr = " SECTIONS/TESTCASES"
        print(pad_to_column_len(left_hdr, result_col, min_gap=1) + "RESULT")
        print("~" * total_width)
        print(".")
        self._print_forest(roots, result_col)

        # -------- Summary --------
        # self._banner("Summary", total_width)
        print(banner(ASCII_SUMMARY_BANNER, width=total_width))

        # Per-status rows

        #  Number of ABORTED                                           0
        #  Number of BLOCKED                                           0
        #  Number of ERRORED                                           0
        #  Number of FAILED                                            0
        #  Number of PASSED                                            1
        #  Number of PASSX                                             0
        #  Number of SKIPPED                                           0
        for label, emoji in RESULT_TO_EMOJI.items():
            left = f" {emoji.lstrip()} Number of {label}"
            right = f"{dict(self.summary).get(label.lower(), 0)}  "
            gap = total_width - len(left) - len(right)
            if label != "SKIPPED":
                print(f"{left}{' ' * gap}{right}")
            else:
                print(f"{left}{' ' * gap} {right}")
        print("_" * total_width)

        # Totals

        #  Total Number                                                1
        #  Success Rate                                           100.0%
        left = " 📊 Total Number"
        right = f"{self.summary.total}  "
        gap = total_width - len(left) - len(right)
        print(f"{left}{' ' * gap}{right}")
        left = " 🎯 Success Rate"
        right = f"{self.summary.success_rate}%  "
        gap = total_width - len(left) - len(right)
        print(f"{left}{' ' * gap}{right}")

        print("~" * total_width)
        print()
