import os
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class LivePhotoConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("小米动态照片转视频工具")
        self.root.geometry("760x520")
        self.root.resizable(False, False)

        self.selected_files = []

        self.create_ui()

    def create_ui(self):
        title = tk.Label(
            self.root,
            text="小米动态照片批量转视频",
            font=("微软雅黑", 18, "bold")
        )
        title.pack(pady=15)

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        select_file_btn = tk.Button(
            button_frame,
            text="选择图片",
            width=18,
            height=2,
            command=self.select_files
        )
        select_file_btn.grid(row=0, column=0, padx=10)

        select_folder_btn = tk.Button(
            button_frame,
            text="选择文件夹",
            width=18,
            height=2,
            command=self.select_folder
        )
        select_folder_btn.grid(row=0, column=1, padx=10)

        start_btn = tk.Button(
            button_frame,
            text="开始转换",
            width=18,
            height=2,
            bg="#4CAF50",
            fg="white",
            command=self.start_convert
        )
        start_btn.grid(row=0, column=2, padx=10)

        self.progress = ttk.Progressbar(
            self.root,
            orient="horizontal",
            length=680,
            mode="determinate"
        )
        self.progress.pack(pady=15)

        self.log_text = tk.Text(
            self.root,
            width=92,
            height=22,
            font=("Consolas", 10)
        )
        self.log_text.pack(padx=15, pady=10)

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def select_files(self):
        files = filedialog.askopenfilenames(
            title="选择动态照片",
            filetypes=[("JPG Files", "*.jpg *.jpeg")]
        )

        if files:
            self.selected_files = list(files)
            self.log(f"已选择 {len(files)} 个文件")

    def select_folder(self):
        folder = filedialog.askdirectory(title="选择文件夹")

        if not folder:
            return

        jpg_files = []

        for file in os.listdir(folder):
            if file.lower().endswith((".jpg", ".jpeg")):
                jpg_files.append(os.path.join(folder, file))

        self.selected_files = jpg_files

        self.log(f"已加载文件夹")
        self.log(f"检测到 {len(jpg_files)} 张 JPG 图片")

    def is_live_photo(self, data):
        return b'ftyp' in data

    def extract_video(self, jpg_path, output_dir):
        try:
            with open(jpg_path, 'rb') as f:
                data = f.read()

            if not self.is_live_photo(data):
                self.log(f"⏭ 跳过（非动态照片）: {os.path.basename(jpg_path)}")
                return False

            mp4_start = data.find(b'ftyp')

            if mp4_start == -1:
                self.log(f"⏭ 跳过（未找到视频头）: {os.path.basename(jpg_path)}")
                return False

            mp4_start -= 4

            mp4_data = data[mp4_start:]

            output_file = os.path.join(
                output_dir,
                Path(jpg_path).stem + ".mp4"
            )

            with open(output_file, 'wb') as f:
                f.write(mp4_data)

            self.log(f"✅ 转换成功: {os.path.basename(output_file)}")
            return True

        except Exception as e:
            self.log(f"❌ 转换失败: {os.path.basename(jpg_path)}")
            self.log(str(e))
            return False

    def convert(self):
        if not self.selected_files:
            messagebox.showwarning("提示", "请先选择图片或文件夹")
            return

        output_dir = os.path.join(
            os.path.dirname(self.selected_files[0]),
            "output"
        )

        os.makedirs(output_dir, exist_ok=True)

        total = len(self.selected_files)
        success = 0

        self.progress["maximum"] = total
        self.progress["value"] = 0

        self.log("=" * 60)
        self.log("开始批量转换...")
        self.log(f"输出目录: {output_dir}")
        self.log("=" * 60)

        for index, file in enumerate(self.selected_files):
            result = self.extract_video(file, output_dir)

            if result:
                success += 1

            self.progress["value"] = index + 1
            self.root.update_idletasks()

        self.log("=" * 60)
        self.log(f"转换完成")
        self.log(f"成功: {success}")
        self.log(f"失败/跳过: {total - success}")
        self.log(f"输出目录: {output_dir}")
        self.log("=" * 60)

        messagebox.showinfo(
            "完成",
            f"转换完成！\n\n成功: {success}\n失败/跳过: {total - success}"
        )

    def start_convert(self):
        threading.Thread(target=self.convert, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = LivePhotoConverterApp(root)
    root.mainloop()