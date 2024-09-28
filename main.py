# "@File    :   pkg解包自动化,
# "@Time    :   2024/9/30,
# "@Author  :   wilsssssssson ",
# "@Version :   1.0",
# "@Contact :   betterWL@hotmail.com"    
from config import TARGET_FILE_FOLDER,SOURCE_FILE_FOLDER,LAST_RUN_TIME,PKG_UNPACK_FILE_PATH
import time,os,json,threading,re
import shutil
import uuid
import subprocess
import config
class WallpaperUnpackge:
   
    def __init__(self):
        self.file_needs_run_list:list=[] 
        self.last_run_time=LAST_RUN_TIME
        self.target_file_folder=TARGET_FILE_FOLDER
        self.source_file_folder=SOURCE_FILE_FOLDER
        self.pkg_unpack_file_path=PKG_UNPACK_FILE_PATH
        self.working_dir=os.getcwd()
        self.get_folder()

    def read_title_from_json_file(self,file_path):
        with open(file_path+'\project.json', 'r',encoding='utf-8') as file:
            data = json.load(file)
        return data['title']
    
    @staticmethod
    def remove_all_spaces(s):
        uuid_string = str(uuid.uuid4())
        pattern = r'[\u4e00-\u9fa5a-zA-Z\s]+'
        result = re.findall(pattern, s)
        output=''.join(result)+uuid_string
        # 将匹配到的字符列表合并成一个字符串
        return output.replace(' ','-')

    def get_folder(self):    #通过其中的json文件修改时间判断其下载时间
        for filename in os.listdir(self.source_file_folder):
            file_path = os.path.join(self.source_file_folder, filename)
            if os.path.isdir(file_path):
                file_mtime = os.path.getmtime(file_path+'\project.json')
                if file_mtime>self.last_run_time:
                    pkg_name=self.remove_all_spaces(self.read_title_from_json_file(file_path))
                    self.file_needs_run_list.append((pkg_name,file_path))
        config.LAST_RUN_TIME=time.time()
        
    @staticmethod
    def find_pkgfile(directory, filename):
        for root, dirs, files in os.walk(directory):
            if filename in files:
                return os.path.join(root, filename)
        return None
    
    def do_copy(self):#将上次之前新增文件复制到当前目录

        for file_name,file_path in self.file_needs_run_list:
            try:
                scene_file_path=self.find_pkgfile(file_path,'scene.pkg')
                destination_file_path=os.path.join(self.working_dir+'\load',file_name+'.pkg')
                if not os.path.exists(self.working_dir+'\load'):
                    os.makedirs(self.working_dir+'\load')
                shutil.copy(scene_file_path, destination_file_path)
                print(f'文件已复制并重命名到：{destination_file_path}')
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
    
    def delete_file_of_this_time(self):#删除复制的pkg
        for file_name,file_path in self.file_needs_run_list:  
            delete_file_path=os.path.join(self.working_dir+'\load',file_name+'.pkg')
            if os.path.exists(delete_file_path):
                os.remove(delete_file_path)
                print(f"文件 {delete_file_path} 已被删除。")
            else:
                # 文件不存在
                print(f"文件 {delete_file_path} 不存在。")
            
    def run_unpack(self):  #运行解包程序
        print('正在解包')  
    
        def read_output(stream, label):  
            for line in stream:  
                print(f"{label}: {line.strip()}")  
        
        command = self.pkg_unpack_file_path + r'\PKG解包程序.exe'  
         
        process = subprocess.Popen(  
            command,  
            stdin=subprocess.PIPE,  
            stdout=subprocess.PIPE,  
            stderr=subprocess.PIPE,  
            text=True,  
            cwd=self.working_dir + r'\load'  
        )  
        process.stdin.write('\n')  
        process.stdin.flush()  
        stdout_thread = threading.Thread(target=read_output, args=(process.stdout, '输出'))  
        stderr_thread = threading.Thread(target=read_output, args=(process.stderr, '错误'))    
        stdout_thread.start()  
        stderr_thread.start()  
        
        return_code = process.wait()  
        stdout_thread.join()  
        stderr_thread.join()  
        
        if return_code:  
            print('子进程返回错误代码:', return_code)



    def reflesh_timestamp(self):
        config_file_path = 'config.py'

        with open(config_file_path, 'r',encoding='utf-8') as file:
            lines = file.readlines()

        current_time_stamp = str(time.time())

        for i, line in enumerate(lines):
            if line.startswith("LAST_RUN_TIME"):
                lines[i] = f"LAST_RUN_TIME = {current_time_stamp}\n"
                break  # 找到并修改后退出循环

        with open(config_file_path, 'w',encoding='utf-8') as file:
            file.writelines(lines)

    def extract_photo(self):
        if not os.path.exists(self.target_file_folder):
                os.makedirs(self.target_file_folder)

        for file_name , file_path in self.file_needs_run_list:
            source_folder=os.path.join(self.working_dir,'load',file_name+'-解包','materials')

            try:
                for check_name in os.listdir(source_folder):
                    # 检查文件扩展名是否是我们需要的类型
                    if check_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                        source_file = os.path.join(source_folder, check_name)
                        destination_file = os.path.join(self.target_file_folder, check_name)
                        shutil.copy2(source_file, destination_file)
                        print(f'Copied {file_name} to {self.target_file_folder}')
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

if __name__=='__main__':
    app=WallpaperUnpackge()
    if app.file_needs_run_list==[]:
        print('当前无新增文件') 
    else:
        app.do_copy()
        app.run_unpack()
  
        app.reflesh_timestamp()
        app.delete_file_of_this_time()
        app.extract_photo()
