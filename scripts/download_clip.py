#!/usr/bin/env python3
import argparse
import hashlib
import os
import sys
import urllib.request
import warnings
from pathlib import Path
from tqdm import tqdm

MODELS = {
    "RN50": "https://openaipublic.azureedge.net/clip/models/afeb0e10f9e5a86da6080e35cf09123aca3b358a0c3e3b6c78a7b63bc04b6762/RN50.pt",
    "RN101": "https://openaipublic.azureedge.net/clip/models/8fa8567bab74a42d41c5915025a8e4538c3bdbe8804a470a72f30b0d94fab599/RN101.pt",
    "RN50x4": "https://openaipublic.azureedge.net/clip/models/7e526bd135e493cef0776de27d5f42653e6b4c8bf9e0f653bb11773263205fdd/RN50x4.pt",
    "RN50x16": "https://openaipublic.azureedge.net/clip/models/52378b407f34354e150460fe41077663dd5b39c54cd0bfd2b27167a4a06ec9aa/RN50x16.pt",
    "RN50x64": "https://openaipublic.azureedge.net/clip/models/be1cfb55d75a9666199fb2206c106743da0f6468c9d327f3e0d0a543a9919d9c/RN50x64.pt",
    "ViT-B/32": "https://openaipublic.azureedge.net/clip/models/40d365715913c9da98579312b702a82c18be219cc2a73407c4526f58eba950af/ViT-B-32.pt",
    "ViT-B/16": "https://openaipublic.azureedge.net/clip/models/5806e77cd80f8b59890b7e101eabd078d9fb84e6937f9e85e4ecb61988df416f/ViT-B-16.pt",
    "ViT-L/14": "https://openaipublic.azureedge.net/clip/models/b8cca3fd41ae0c99ba7e8951adf17d267cdb84cd88be6f7c2e0eca1737a03836/ViT-L-14.pt",
    "ViT-L/14@336px": "https://openaipublic.azureedge.net/clip/models/3035c92b350959924f9f00213499208652fc7ea050643e8b385c2dac08641f02/ViT-L-14-336px.pt",
}

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def download(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    expected = url.rstrip("/").split("/")[-2]
    tmp = dest.with_suffix(dest.suffix + ".part")

    # If exists, verify
    if dest.is_file():
        if sha256_file(dest) == expected:
            return dest
        warnings.warn(f"{dest} exists but checksum mismatch, re-downloading")

    # Stream download with progress
    with urllib.request.urlopen(url) as source, open(tmp, "wb") as out:
        total = int(source.info().get("Content-Length", "0")) or None
        with tqdm(total=total, ncols=80, unit="iB", unit_scale=True, unit_divisor=1024) as bar:
            while True:
                buf = source.read(8192)
                if not buf:
                    break
                out.write(buf)
                bar.update(len(buf))

    # Verify and move
    if sha256_file(tmp) != expected:
        tmp.unlink(missing_ok=True)
        raise RuntimeError("Checksum mismatch after download")
    tmp.replace(dest)
    return dest

def main():
    parser = argparse.ArgumentParser(description="Download CLIP model weights with SHA256 verification.")
    parser.add_argument("models", nargs="*", help="Model names to download (default: all).")
    parser.add_argument("--list", action="store_true", help="List available models and exit.")
    parser.add_argument("--root", default=str(Path.home() / ".cache" / "clip"), help="Download directory.")
    args = parser.parse_args()

    if args.list:
        for k in MODELS:
            print(k)
        return

    selection = args.models or list(MODELS.keys())
    unknown = [m for m in selection if m not in MODELS]
    if unknown:
        print(f"Unknown models: {unknown}\nAvailable: {list(MODELS.keys())}", file=sys.stderr)
        sys.exit(1)

    root = Path(args.root)
    for name in selection:
        url = MODELS[name]
        filename = os.path.basename(url)
        dest = root / filename
        print(f"Downloading {name} -> {dest}")
        path = download(url, dest)
        print(f"OK: {path}")

if __name__ == "__main__":
    main()