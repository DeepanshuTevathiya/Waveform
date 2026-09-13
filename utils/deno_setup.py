import os
import deno


def ensure_deno():
    deno_path = deno.find_deno_bin()

    if not deno_path or not os.path.exists(deno_path):
        raise RuntimeError("Deno installation failed")

    return deno_path