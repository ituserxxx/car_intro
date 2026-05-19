"""
Fix mojibake filenames in doc/.
The issue: GBK-encoded Chinese bytes were decoded as cp437, creating garbled names.
Fix: encode as cp437 -> decode as gbk.
"""
import os
import re
from pathlib import Path

DOC_DIR = Path(__file__).parent / "doc"

def try_fix_name(name):
    """Try to fix cp437-decoded-gbk mojibake."""
    try:
        fixed = name.encode('cp437').decode('gbk')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return None
    
    # If fixed is same as original, no change needed
    if fixed == name:
        return None
    
    # Sanity check: fixed name should contain mostly common chars
    # Allow Chinese, ASCII alnum, space, and common punctuations in filenames
    allowed = set(
        'abcdefghijklmnopqrstuvwxyz'
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        '0123456789'
        ' \u3000'  # space and full-width space
        '-_()[]{}.+=&~@#%\uff08\uff09\u2014\u2018\u2019'
    )
    
    for ch in fixed:
        if ch in allowed:
            continue
        cp = ord(ch)
        # CJK Unified Ideographs
        if 0x4E00 <= cp <= 0x9FFF:
            continue
        # CJK Unified Ideographs Extension A
        if 0x3400 <= cp <= 0x4DBF:
            continue
        # Fullwidth ASCII variants
        if 0xFF01 <= cp <= 0xFF5E:
            continue
        # CJK Symbols and Punctuation
        if 0x3000 <= cp <= 0x303F:
            continue
        # General Punctuation
        if 0x2000 <= cp <= 0x206F:
            continue
        return None
    
    return fixed

def safe_name(name):
    return re.sub(r'[\\/:*?"<>|]', '_', name).strip()

def main():
    log_lines = ["Scanning for mojibake filenames..."]
    renamed = 0
    skipped = 0
    errors = 0
    
    for f in sorted(DOC_DIR.iterdir()):
        if not f.is_file():
            continue
        
        original = f.name
        fixed = try_fix_name(original)
        
        if fixed is None:
            skipped += 1
            continue
        
        fixed = safe_name(fixed)
        dest = DOC_DIR / fixed
        
        # Handle collision
        counter = 1
        original_dest = dest
        while dest.exists() and dest != f:
            stem = original_dest.stem
            dest = DOC_DIR / f"{stem}_{counter}{original_dest.suffix}"
            counter += 1
        
        log_lines.append(f"RENAME: {original[:60]} -> {dest.name[:60]}")
        f.rename(dest)
        renamed += 1
    
    log_lines.append(f"\nDone: renamed {renamed}, skipped {skipped}, errors {errors}")
    
    log_path = Path(__file__).parent / "fix_encoding_log.txt"
    with open(log_path, "w", encoding="utf-8") as lf:
        lf.write("\n".join(log_lines))
    
    for line in log_lines:
        print(line.encode('ascii', 'replace').decode('ascii'))

if __name__ == "__main__":
    main()
