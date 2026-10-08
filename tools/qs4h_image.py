"""The image builder: QS4h's sandbox image, built and checked, its ID recorded.

    python tools/qs4h_image.py [--local <dir>] [--check-only]

1. `docker ps` is read first; P2's pinned base must be present (it is never pulled).
2. `docker build --pull=false --network default -f sandbox/qs4h.Dockerfile` from an
   empty context under <local>, tagged hh-qs4h-sandbox:<12 hex of the Dockerfile's
   SHA-256>: the base is the one on this desktop, never pulled. The build's container
   reaches PyPI for the 18 pinned wheels, each checked by --require-hashes. With
   --check-only the tagged image must exist already.
3. One container of the image, started as P2's sandbox starts a run's (no network, a
   read-only root, nobody), named hh-qs4h-<id>, checks: Python's version; `pip list`
   holds the 18 pins at their versions; `pip check` passes; there is no docker command;
   a connection out fails; and the image's own /opt/qs4h/requirements.txt is the
   Dockerfile's. The container is removed.
4. <local>/image.json records the tag, the ID, the Dockerfile's SHA-256, the base's ID,
   the sizes and the new layers, and what the check found. QS4h's inputs refuse to
   mount unless that ID is the image Docker holds.

It prints no absolute path, and exits 0 only when every check holds.
"""
from __future__ import annotations

import argparse
import json
import re
import secrets
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from qs.agent.sandbox import SandboxError  # noqa: E402
from qs.suites import qs4, qs4h  # noqa: E402

PIN = re.compile(r"^([A-Za-z0-9._-]+)==(\S+) --hash=sha256:([0-9a-f]{64})$")


def canonical(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def requirements(dockerfile: bytes) -> bytes:
    """The Dockerfile's inline requirements, as the image holds them."""
    text = dockerfile.decode("utf-8")
    m = re.search(r"^COPY <<EOF /opt/qs4h/requirements\.txt\n(.*?)^EOF$", text, re.M | re.S)
    if not m:
        raise qs4.InputError("sandbox/qs4h.Dockerfile holds no inline requirements")
    return m.group(1).encode("utf-8")


def pins(reqs: bytes) -> dict[str, str]:
    out = {}
    for line in reqs.decode("utf-8").splitlines():
        m = PIN.match(line.strip())
        if not m:
            raise qs4.InputError("a requirement is not pinned by version and SHA-256")
        out[canonical(m.group(1))] = m.group(2)
    return out


def docker(*args: str, timeout: float = 120) -> subprocess.CompletedProcess:
    return subprocess.run(["docker", *args], capture_output=True, text=True, timeout=timeout)


def size_of(ref: str) -> int:
    return int(docker("image", "inspect", "--format", "{{.Size}}", ref).stdout.strip())


def check_in_container(image: str, scratch: Path) -> dict:
    """The image's checks, in one container started as a run's would be."""
    scratch.mkdir(parents=True, exist_ok=False)
    box = qs4h.BuildSandbox(scratch, [], image=image, lifetime_s=900)
    out: dict = {}
    try:
        facts = box.start()
        out["python"], out["git"] = facts.get("python"), facts.get("git")
        r = box.shell("python3 -m pip list --format=json --disable-pip-version-check", 120)
        out["packages"] = {canonical(p["name"]): p["version"]
                           for p in json.loads((r.head + r.tail).decode("utf-8"))}
        r = box.shell("python3 -m pip check --disable-pip-version-check", 120)
        out["pip_check"] = (r.exit_code, (r.head + r.tail).decode("utf-8", "replace").strip()[:200])
        r = box.shell("command -v docker || echo NO-DOCKER", 60)
        out["docker_absent"] = (r.head + r.tail).decode().strip() == "NO-DOCKER"
        r = box.shell("python3 -c \"import socket; socket.create_connection(('1.1.1.1', 443), timeout=5)\"", 60)
        out["network_refused"] = r.exit_code not in (0, None)
        r = box.shell("sha256sum /opt/qs4h/requirements.txt", 60)
        out["requirements_sha256"] = (r.head + r.tail).decode().split()[0]
    finally:
        out["removed"] = bool(box.stop().get("removed"))
        qs4._remove(scratch)
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--local", default=str(qs4h.LOCAL))
    ap.add_argument("--check-only", action="store_true")
    a = ap.parse_args(argv)
    local = Path(a.local)
    dockerfile = qs4h.DOCKERFILE_PATH.read_bytes()
    df_sha = qs4.sha256(dockerfile)
    tag = f"{qs4h.IMAGE_REPO}:{df_sha[:12]}"
    try:
        reqs = requirements(dockerfile)
        want = pins(reqs)
        ps = docker("ps", "--format", "{{.Names}}")
        if ps.returncode != 0:
            raise qs4.InputError("docker ps did not answer")
        print(f"docker ps: {len(ps.stdout.split())} containers running")
        base_id = qs4h.inspect_image(qs4h.BASE_IMAGE)
        if not base_id:
            raise qs4.InputError("P2's pinned base image is not on this desktop, and is never pulled here")
        if not a.check_only:
            ctx = local / "image-context"
            ctx.mkdir(parents=True, exist_ok=True)
            if any(ctx.iterdir()):
                raise qs4.InputError("the build's context directory is not empty")
            r = subprocess.run(["docker", "build", "--pull=false", "--network", "default", "--progress", "plain",
                                "-f", str(qs4h.DOCKERFILE_PATH), "-t", tag, str(ctx)], capture_output=True,
                               text=True, timeout=1800)
            (local / "image-build.log").write_text(r.stdout + r.stderr, encoding="utf-8")
            if r.returncode != 0:
                raise qs4.InputError(f"docker build failed (exit {r.returncode}); see local/qs4h/image-build.log")
        image_id = qs4h.inspect_image(tag)
        if not image_id:
            raise qs4.InputError(f"the image {tag} is not there")
        size, base_size = size_of(image_id), size_of(base_id)
        hist = docker("history", "--no-trunc", "--format", "{{.Size}}\t{{.CreatedBy}}", image_id).stdout
        layers = [{"size": ln.split("\t", 1)[0], "created_by": ln.split("\t", 1)[1][:70]}
                  for ln in hist.splitlines()[:2]]
        found = check_in_container(image_id, local / "tmp" / f"img-{secrets.token_hex(4)}")
    except (qs4.InputError, SandboxError, subprocess.TimeoutExpired, OSError, ValueError) as e:
        print(f"REFUSED: {type(e).__name__}: {e}")
        return 2
    wrong = {k: (v, found["packages"].get(k)) for k, v in want.items() if found["packages"].get(k) != v}
    extra = {k: v for k, v in found["packages"].items() if k not in want}
    checks = {"pins": not wrong, "pip check": found["pip_check"][0] == 0, "no docker": found["docker_absent"],
              "no network": found["network_refused"], "requirements": found["requirements_sha256"] == qs4.sha256(reqs),
              "removed": found["removed"]}
    record = {"format": 1, "tag": tag, "id": image_id, "dockerfile_sha256": df_sha, "base_image": qs4h.BASE_IMAGE,
              "base_id": base_id, "size": size, "base_size": base_size, "added_bytes": size - base_size,
              "layers": layers, "python": found["python"], "git": found["git"], "pins": want,
              "other_packages": extra, "pip_check": found["pip_check"][1], "checks": checks,
              "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    (local / "image.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"image {tag}: {image_id[:19]}, {size} bytes, {size - base_size} more than the base; "
          f"new layers {', '.join(x['size'] for x in layers)}")
    print(f"in a container: {found['python']}, {found['git']}; {len(want) - len(wrong)} of {len(want)} pins as "
          f"pinned; others {sorted(extra)}; pip check: {found['pip_check'][1]}")
    for name, ok in checks.items():
        print(f"  {name:13} {'ok' if ok else 'FAIL'}")
    if wrong:
        print(f"  not as pinned: {wrong}")
    print("wrote image.json")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
