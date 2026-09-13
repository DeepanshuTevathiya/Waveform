import os
import shutil
import subprocess
import platform
import urllib.request
import zipfile


def ensure_deno():
    deno = shutil.which("deno")

    if deno:
        return deno

    deno_dir = os.path.expanduser("~/.deno/bin")
    deno_path = os.path.join(deno_dir, "deno")

    os.makedirs(deno_dir, exist_ok=True)

    # Streamlit Cloud runs Linux x86_64
    if platform.system() == "Linux":
        url = "https://github.com/denoland/deno/releases/latest/download/deno-x86_64-unknown-linux-gnu.zip"
        zip_path = os.path.join(deno_dir, "deno.zip")

        urllib.request.urlretrieve(url, zip_path)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(deno_dir)

        os.remove(zip_path)

        os.chmod(deno_path, 0o755)

    else:
        raise RuntimeError(
            "Deno was not found. Please install Deno manually on this system."
        )

    if not os.path.exists(deno_path):
        raise RuntimeError("Deno installation failed")

    os.environ["PATH"] = deno_dir + os.pathsep + os.environ.get("PATH", "")

    return deno_path