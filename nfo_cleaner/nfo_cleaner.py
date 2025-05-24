import os
import sys
from pathlib import Path

def log(msg):
    print(msg)

def find_files_to_delete_streamed(root_dir):
    to_delete = []
    to_keep = []

    dir_count = 0

    for dirpath, _, filenames in os.walk(root_dir):
        dir_count += 1
        print(f"📁 正在处理目录 {dir_count}: {dirpath}")

        strm_names = {os.path.splitext(f)[0] for f in filenames if f.endswith('.strm')}
        nfo_files = [f for f in filenames if f.endswith('.nfo')]

        for nfo_file in nfo_files:
            base_name = os.path.splitext(nfo_file)[0]
            full_path = os.path.join(dirpath, nfo_file)

            # 保留特殊 nfo 文件
            if nfo_file.lower() in ("season.nfo", "tvshow.nfo"):
                to_keep.append(full_path)
                continue

            if base_name not in strm_names:
                to_delete.append(full_path)
            else:
                to_keep.append(full_path)

    print(f"\n✅ 总共扫描目录数：{dir_count}")
    return to_keep, to_delete

def export_delete_list(file_list):
    desktop = Path.home() / "Desktop"
    export_file = desktop / "nfo_cleaner_delete_list.txt"
    try:
        with open(export_file, "w", encoding="utf-8") as f:
            f.write("将要删除的 NFO 文件列表：\n")
            for path in file_list:
                f.write(path + "\n")
        log(f"\n📄 删除列表已导出到：{export_file}")
    except Exception as e:
        log(f"⚠️ 删除列表导出失败: {str(e)}")

def delete_files(file_list):
    deleted = 0
    for f in file_list:
        try:
            os.remove(f)
            log(f"✅ 已删除: {f}")
            deleted += 1
        except Exception as e:
            log(f"⚠️ 删除失败: {f} ({str(e)})")
    log(f"\n✅ 总共删除 {deleted} 个 .nfo 文件。")

def main():
    if len(sys.argv) != 2:
        print("用法：python3 nfo_cleaner.py /要处理的目录路径")
        return

    path = sys.argv[1]
    if not os.path.isdir(path):
        print(f"❌ 路径无效：{path}")
        return

    log(f"📂 正在扫描目录：{path}")
    keep, delete = find_files_to_delete_streamed(path)

    log(f"\n✅ 保留的 NFO 文件（{len(keep)} 个）:")
    for f in keep:
        log(f"    ✅ {f}")

    log(f"\n🗑️ 将要删除的多余 NFO 文件（{len(delete)} 个）:")
    for f in delete:
        log(f"    🗑️ {f}")

    export_delete_list(delete)

    if delete:
        confirm = input(f"\n❓ 确认删除以上 {len(delete)} 个 NFO 文件？(y/n): ").strip().lower()
        if confirm == 'y':
            delete_files(delete)
        else:
            log("❌ 取消删除操作。")
    else:
        log("✅ 未发现多余的 NFO 文件。")

if __name__ == "__main__":
    main()