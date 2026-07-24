import os
import re
reg_atom_mag = r"^\s+(\d+)\s+([+-]?\d+\.\d+)\s+([+-]?\d+\.\d+)\s+([+-]?\d+\.\d+)\s+([+-]?\d+\.\d+)"
natom=2
folders=[f"run_{i}" for i in range(1,4)]
results=[]

for folder in folders:
    outcar_path=os.path.join(folder,"OUTCAR")
    if not os.path.exists(outcar_path):
        print(f"{folder}不存在OUTCAR")
        continue
    with open(outcar_path,"r",encoding="utf-8") as f:
        content=f.read()
    all_mag_rows=re.findall(reg_atom_mag,content,flags=re.MULTILINE)   #**加上 `re.MULTILINE`（多行模式）**- `^`：匹配**任意一行的开头**（`\n` 换行符之后）
    if len(all_mag_rows)>=natom:
        last_group=all_mag_rows[-natom:]
        for item in last_group:
            ion_id=item[0]# 原子编号
            d_mu=item[3]
            results.append([folder,ion_id,d_mu])
    else:
        print(f"{folder} 未能读到完整原子磁矩数据")
with open("d轨道磁矩汇总.csv","w",encoding="utf-8-sig") as fw:
     fw.write("文件夹,原子编号,d轨道磁矩(μB)\n")
     for row in results:
       fw.write(f"{row[0]},{row[1]},{row[2]}\n")   
print("提取完成")