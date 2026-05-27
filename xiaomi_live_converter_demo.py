import os
from pathlib import Path

# 动态照片目录
INPUT_DIR = r"F:\backup\小米14备份\test"

# 输出目录
OUTPUT_DIR = os.path.join(INPUT_DIR, "output")

os.makedirs(OUTPUT_DIR, exist_ok=True)


def extract_mp4_from_jpg(jpg_path):
    try:
        with open(jpg_path, "rb") as f:
            data = f.read()

        # 查找 MP4 文件头
        mp4_start = data.find(b'ftyp')

        if mp4_start == -1:
            print(f"❌ 未找到视频: {jpg_path}")
            return

        # MP4 真正开始位置
        mp4_start -= 4

        mp4_data = data[mp4_start:]

        output_file = os.path.join(
            OUTPUT_DIR,
            Path(jpg_path).stem + ".mp4"
        )

        with open(output_file, "wb") as f:
            f.write(mp4_data)

        print(f"✅ 提取成功: {output_file}")

    except Exception as e:
        print(f"❌ 处理失败 {jpg_path}: {e}")


def main():
    for file in os.listdir(INPUT_DIR):
        if file.lower().endswith(".jpg"):
            full_path = os.path.join(INPUT_DIR, file)
            extract_mp4_from_jpg(full_path)


if __name__ == "__main__":
    main()