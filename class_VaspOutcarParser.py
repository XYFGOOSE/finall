import argparse
import os
import re
import logging

# --------------------------日志全局配置--------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 防止重复添加handler（多次调用脚本不会重复打印日志）
if logger.handlers:
    logger.handlers.clear()

log_format = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# 控制台
sh = logging.StreamHandler()
sh.setFormatter(log_format)
# 文件
fh = logging.FileHandler("outcar_parse_log.txt", encoding="utf-8-sig")
fh.setFormatter(log_format)

logger.addHandler(sh)
logger.addHandler(fh)
# ----------------------------------------------------------------

class VaspOutcarParser :
    def __init__(self,start:int,end:int,natom:int=2,csv_sys:str="汇总_体系信息.csv",csv_atom:str="汇总_原子d磁矩.csv"):
        self.start=start
        self.end=end
        self.natom=natom
        self.csv_sys=csv_sys
        self.csv_atom=csv_atom
        self.reg_energy = r"Final: energy without entropy\s*=\s*([-+]?\d+\.\d+)"
        self.reg_mag = r"Magnetic moment\s*=\s*([-+]?\d+\.\d+)"
        self.reg_Fermi_energy = r"Fermi energy :\s+([-+]?\d+\.\d+)"
        self.reg_atom_mag = r"^\s+(\d+)\s+([+-]?\d+\.\d+)\s+([+-]?\d+\.\d+)\s+([+-]?\d+\.\d+)\s+([+-]?\d+\.\d+)"
        self.sys_results=[]
        self.atom_results=[]

  #解析单个文件夹
    def scan_single_outcar(self,folder:str):
        outcar_path=os.path.join(folder,"OUTCAR")
        if not os.path.exists(outcar_path):
            logger.warning(f"⚠️ {folder} OUTCAR不存在,跳过")
            return#`return` 退出函数
        try:
            with open(outcar_path,"r",encoding="utf-8", errors="ignore") as f:
                content=f.read()
        except Exception as e:
            logger.error(f"{folder} OUTCAR读取失败，错误信息: {str(e)}")
            return

        all_e=re.findall(self.reg_energy,content)
        energy=float(all_e[-1]) if all_e else None
            # if all_e:
            #     energy = float(all_e[-1])
            # else:
            #     energy = None
        all_m = re.findall(self.reg_mag, content)
        mag = float(all_m[-1]) if all_m else None
        all_fermi = re.findall(self.reg_Fermi_energy, content)
        fermi = float(all_fermi[-1]) if all_fermi else None
        self.sys_results.append([folder, energy, mag, fermi])
        all_mag_rows=re.findall(self.reg_atom_mag,content,flags=re.MULTILINE)   #**加上 `re.MULTILINE`（多行模式）**- `^`：匹配**任意一行的开头**（`\n` 换行符之后）
        if len(all_mag_rows)>=self.natom:
            last_group=all_mag_rows[-self.natom:]
            for item in last_group:
                atom_id=int(item[0])# 原子编号
                d_mu=float(item[3])  
                self.atom_results.append([folder, atom_id, d_mu])
            logger.info(f"{folder} 最终能量(eV): {energy} , 总磁矩(mu_B): {mag}, 费米能量:{fermi}")
        else:
            logger.warning(f"⚠️ {folder} 未能读到完整{self.natom}个原子磁矩数据")   

    def run_scan(self):
        folders=[f"run_{i}" for i in range(self.start,self.end)]
        for folder in folders:
            self.scan_single_outcar(folder) 
            # 括号里的 `folder` 是**实参**，把当前循环拿到的文件夹名字传给函数。

            # 执行流程演示：

            # 1. `folder = "run_1"`
            # 2. 调用 `self.scan_single_outcar("run_1")`
            # → 进入函数内部，解析 run_1 的 OUTCAR
            # 3. 函数执行完毕（遇到 return 或者函数代码走完）
            # 4. 回到 for 循环，取下一个 `folder = "run_2"`
            # 5. 再次调用解析函数……
    def write_csv(self):
        with open(self.csv_sys,"w", encoding="utf-8-sig") as f:
            f.write("文件夹,最终能量(eV),总磁矩(mu_B),费米能量(eV)\n")
            for row in self.sys_results:
                f.write(f"{row[0]},{row[1]},{row[2]},{row[3]}\n")
        with open(self.csv_atom,"w", encoding="utf-8-sig") as f:
                f.write("文件夹,原子编号,d轨道磁矩(μB)\n")
                for row in self.atom_results:
                        f.write(f"{row[0]},{row[1]},{row[2]}\n") 
        logger.info("\n✅ 导出完成！")
        logger.info(f"体系信息：{self.csv_sys}")
        logger.info(f"原子d磁矩: {self.csv_atom}") 

    def execute(self):
        self.run_scan()
        self.write_csv()       
# =====================顶层封装函数=====================
def parse_vasp(start, end, natom=2, csv_sys="汇总_体系信息.csv", csv_atom="汇总_原子d磁矩.csv"):
    VaspOutcarParser(start, end, natom, csv_sys, csv_atom).execute()

def main():
   parser=argparse.ArgumentParser(description="批量解析VASP OUTCAR,提取能量、总磁矩、费米能、原子d轨道磁矩")
   parser.add_argument("--start", type=int, required=True, help="run起始编号,如 1")
   parser.add_argument("--end", type=int, required=True, help="run终止编号(开区间),--end=4 代表 run_1,run_2,run_3")
   parser.add_argument("--natom", type=int, default=2, help="需要读取磁矩的原子数目,默认2")
   parser.add_argument("--csv_sys", type=str, default="汇总_体系信息.csv", help="体系能量总磁矩输出文件")
   parser.add_argument("--csv_atom", type=str, default="汇总_原子d磁矩.csv", help="原子d轨道磁矩输出文件")
   args = parser.parse_args()
   parse_vasp(start=args.start, end=args.end, natom=args.natom, csv_sys=args.csv_sys, csv_atom=args.csv_atom)

if __name__ == "__main__":
    main()

# 1. 终端输入命令：`python 文件.py --start 1 --end 4`
# 2. `parser.parse_args()` 解析命令，得到 `args.start=1，args.end=4`
# 3. 调用 `parse_vasp(……)`，把 args 里面的数据传进去
# 4. 进入 `parse_vasp` 函数内部
# 5. 执行 `VaspOutcarParser(...).execute()`
#    - 创建解析器实例
#    - 运行 execute → 批量扫描 OUTCAR、解析、写入 CSV



# # 示例1：基础用法，使用默认输出文件名
# py .\class_VaspOutcarParser.py --start 1 --end 5

# # 示例2：指定读取3个原子磁矩 + 自定义导出csv名称
# py .\class_VaspOutcarParser.py --start 1 --end 5 --natom 3 --csv_sys run1-4_体系.csv --csv_atom run1-4_原子磁矩.csv

# # 示例3：只修改体系csv名称，原子磁矩文件使用默认名
# py .\class_VaspOutcarParser.py --start 1 --end 8 --csv_sys result_sys.csv
#