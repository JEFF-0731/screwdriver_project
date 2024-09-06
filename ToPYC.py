import py_compile
import os
py_compile.compile(r'Screwdriver_Detection.py')
# py_compile.compile(r'ScrewDrive.py')

folder_path = r"C:\Users\YC03SRA003\Desktop\0723ProgramBackup\__pycache__"
# folder_path = r"C:\Users\YC03SRA003\Desktop\0507ProgramBackup\PLC\__pycache__"

# 遍历文件夹中的所有文件
for filename in os.listdir(folder_path):
    # 检查文件名是否以".pyc"结尾
    if filename.endswith('.pyc'):
        # 构建完整的文件路径
        file_path = os.path.join(folder_path, filename)

        # 新文件名，将".cpython-36"替换为空字符串
        new_filename = filename.replace('.cpython-39', '')

        # 构建新文件的完整路径
        new_file_path = os.path.join(folder_path, new_filename)

        # 重命名文件
        os.rename(file_path, new_file_path)

print("文件名中的'.cpython-36'已删除。")
print('done')