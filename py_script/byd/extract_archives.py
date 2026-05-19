"""
Extract all ZIP/RAR archives in doc/, keep only PDFs, delete archives.
"""
import os
import re
import zipfile
import shutil
import rarfile
from pathlib import Path

rarfile.UNRAR_TOOL = r"C:\Program Files\WinRAR\UnRAR.exe"

DOC_DIR = Path(__file__).parent / "doc"

def safe_name(name):
    return re.sub(r'[\\/:*?"<>|]', '_', name).strip()

def extract_zip(zip_path, extract_dir):
    pdf_files = []
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            for member in zf.namelist():
                zf.extract(member, extract_dir)
                extracted_path = Path(extract_dir) / member
                if extracted_path.suffix.lower() == '.pdf':
                    pdf_files.append(extracted_path)
        return pdf_files
    except Exception as e:
        print(f"    ERROR extracting zip: {e}")
        return []

def extract_rar(rar_path, extract_dir):
    pdf_files = []
    try:
        with rarfile.RarFile(rar_path, 'r') as rf:
            for member in rf.namelist():
                rf.extract(member, extract_dir)
                extracted_path = Path(extract_dir) / member
                if extracted_path.suffix.lower() == '.pdf':
                    pdf_files.append(extracted_path)
        return pdf_files
    except Exception as e:
        print(f"    ERROR extracting rar: {e}")
        return []

def move_pdfs(pdf_files, dest_dir):
    moved = 0
    for pdf in pdf_files:
        pdf_name = safe_name(pdf.name)
        pdf_dest = dest_dir / pdf_name
        counter = 1
        original_dest = pdf_dest
        while pdf_dest.exists():
            stem = original_dest.stem
            pdf_dest = dest_dir / f"{stem}_{counter}{original_dest.suffix}"
            counter += 1
        shutil.move(str(pdf), str(pdf_dest))
        moved += 1
    return moved

def main():
    print("=" * 60)
    print("Archive Extractor: keep only PDFs")
    print("=" * 60)

    archives = [f for f in DOC_DIR.iterdir() if f.suffix.lower() in ('.zip', '.rar')]
    print(f"Found {len(archives)} archives")

    total_extracted = 0
    total_archives = 0

    for archive in sorted(archives):
        print(f"\nProcessing: {archive.name}")
        extract_dir = DOC_DIR / f"_extract_{archive.stem[:30]}"
        extract_dir.mkdir(exist_ok=True)

        if archive.suffix.lower() == '.zip':
            pdf_files = extract_zip(archive, extract_dir)
        else:
            pdf_files = extract_rar(archive, extract_dir)

        if pdf_files:
            moved = move_pdfs(pdf_files, DOC_DIR)
            print(f"  -> Extracted {moved} PDFs")
            total_extracted += moved
            total_archives += 1
        else:
            print(f"  -> No PDF found")

        # Clean up extraction dir
        shutil.rmtree(extract_dir, ignore_errors=True)

        # Delete archive
        archive.unlink()
        print(f"  -> Deleted archive")

    # Clean up any old _extract_* directories
    old_dirs = [d for d in DOC_DIR.iterdir() if d.is_dir() and d.name.startswith('_extract_')]
    for d in old_dirs:
        shutil.rmtree(d, ignore_errors=True)
        print(f"Cleaned up old dir: {d.name}")

    print("\n" + "=" * 60)
    print(f"Done: processed {total_archives} archives, extracted {total_extracted} PDFs")
    print("=" * 60)

if __name__ == "__main__":
    main()
