"""`chess-ocr env`: verify the CUDA / bitsandbytes environment.

torch and bitsandbytes are imported lazily so the rest of the CLI works
without the `gpu` dependency group (e.g. in CI).
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field

INSTALL_HINT = "torch is not installed. Run `uv sync --group gpu` first."

# Relative error allowed between the NF4 4-bit layer and its bf16 reference.
# NF4 on Gaussian weights typically lands around 0.1.
NF4_MAX_REL_ERROR = 0.25


@dataclass
class Check:
    name: str
    ok: bool
    detail: str = ""


@dataclass
class EnvReport:
    info: dict[str, str] = field(default_factory=dict)
    checks: list[Check] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return bool(self.checks) and all(c.ok for c in self.checks)


def _gib(n_bytes: int) -> str:
    return f"{n_bytes / 2**30:.2f} GiB"


def nf4_smoke_test(size: int = 512, batch: int = 16) -> float:
    """Run an NF4 Linear4bit forward pass on the GPU; return its relative error vs bf16."""
    import bitsandbytes as bnb
    import torch

    torch.manual_seed(0)
    ref = torch.nn.Linear(size, size, bias=False, dtype=torch.bfloat16)
    q = bnb.nn.Linear4bit(size, size, bias=False, compute_dtype=torch.bfloat16, quant_type="nf4")
    q.weight = bnb.nn.Params4bit(ref.weight.data.clone(), requires_grad=False, quant_type="nf4")
    ref, q = ref.cuda(), q.cuda()  # moving Params4bit to CUDA quantizes it
    x = torch.randn(batch, size, device="cuda", dtype=torch.bfloat16)
    with torch.no_grad():
        expected, got = ref(x).float(), q(x).float()
    if not torch.isfinite(got).all():
        return float("inf")
    return ((got - expected).norm() / expected.norm()).item()


def collect() -> EnvReport:
    """Gather versions and run the checks. Raises ImportError if torch is missing."""
    import torch

    report = EnvReport()
    report.info["torch"] = torch.__version__
    report.info["CUDA (torch build)"] = str(torch.version.cuda)

    cuda = torch.cuda.is_available()
    report.checks.append(Check("CUDA available", cuda))
    if not cuda:
        return report

    idx = torch.cuda.current_device()
    major, minor = torch.cuda.get_device_capability(idx)
    arch = f"sm_{major}{minor}"
    free, total = torch.cuda.mem_get_info(idx)
    report.info["GPU"] = torch.cuda.get_device_name(idx)
    report.info["compute capability"] = f"{major}.{minor} ({arch})"
    report.info["VRAM"] = f"{_gib(free)} free / {_gib(total)} total"

    arch_list = torch.cuda.get_arch_list()
    report.checks.append(
        Check(f"{arch} kernels in torch build", arch in arch_list, " ".join(arch_list))
    )
    report.checks.append(Check("bf16 supported", torch.cuda.is_bf16_supported()))

    try:
        import bitsandbytes as bnb

        report.info["bitsandbytes"] = bnb.__version__
        rel = nf4_smoke_test()
        report.checks.append(
            Check(
                "bitsandbytes NF4 4-bit matmul",
                rel <= NF4_MAX_REL_ERROR,
                f"relative error {rel:.4f} (max {NF4_MAX_REL_ERROR})",
            )
        )
    except Exception as exc:  # report any bnb failure instead of crashing
        report.checks.append(
            Check("bitsandbytes NF4 4-bit matmul", False, f"{type(exc).__name__}: {exc}")
        )
    return report


def format_report(report: EnvReport) -> str:
    width = max((len(k) for k in report.info), default=0)
    lines = [f"{k.ljust(width)}  {v}" for k, v in report.info.items()]
    lines.append("")
    for c in report.checks:
        line = f"[{'PASS' if c.ok else 'FAIL'}] {c.name}"
        if c.detail:
            line += f": {c.detail}"
        lines.append(line)
    lines.append("")
    lines.append("Environment OK" if report.ok else "Environment check FAILED")
    return "\n".join(lines)


def run(args: argparse.Namespace) -> int:
    try:
        report = collect()
    except ImportError:
        print(INSTALL_HINT, file=sys.stderr)
        return 1
    print(format_report(report))
    return 0 if report.ok else 1
