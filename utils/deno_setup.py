import os
import shutil
import subprocess


def ensure_deno():
    deno = shutil.which("deno")

    if deno:
        return deno

    deno_dir = os.path.expanduser("~/.deno/bin")
    deno_path = os.path.join(deno_dir, "deno")

    os.makedirs(deno_dir, exist_ok=True)

    subprocess.run(
        [
            "bash",
            "-c",
            "curl -fsSL https://deno.land/install.sh | sh",
        ],
        check=True,
    )

    if not os.path.exists(deno_path):
        raise RuntimeError("Deno installation failed")

    # Make Deno discoverable by the current Python process
    os.environ["PATH"] = deno_dir + os.pathsep + os.environ.get("PATH", "")

    return deno_path