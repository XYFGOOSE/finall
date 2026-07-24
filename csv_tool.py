import os
def get_latest_csv(folder="."):
    csv_list=[]
    for file in os.listdir(folder): #`os.listdir(路径)`：拿到文件夹内**所有条目名称(列表)
     # 判断：文件名小写后以 .csv 结尾
    # file.lower() 兼容 .CSV 大写后缀
      if file.lower().endswith(".csv"):
       full_path=os.path.join(folder,file)
    # os.path.getmtime() 获取文件【最后修改时间戳】
    # 返回一串数字：距离1970-01-01的秒数，数字越大 = 文件越新
       mtime=os.path.getatime(full_path)#获取文件【最后修改时间戳】
       csv_list.append([mtime,full_path])
    if not csv_list:
     raise FileNotFoundError("当前目录没有找到任何CSV文件!")
  # 排序
    # key=lambda x:x\[0\] → 拿元组第0项（时间戳）作为排序依据
    # reverse=True → 从大到小（新文件放前面）  
    csv_list.sort(reverse=True,key=lambda x:x[0])
    latest_file_path=csv_list[0][1]
    print(f"✅自动识别最新CSV:{os.path.basename(latest_file_path)}")#使用 `os.path.basename()`，只打印 csv 文件名，没完整路径，控制台输出简洁好看。
    return latest_file_path

###