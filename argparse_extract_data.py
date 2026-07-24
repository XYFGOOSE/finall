import argparse
import os
import re

def main():
    parser = argparse.ArgumentParser(description="批量解析VASP OUTCAR,提取能量、总磁矩、费米能、原子d轨道磁矩")
    parser.add_argument("--start", type=int, required=True, help="run起始编号,如 1")
    parser.add_argument("--end", type=int, required=True, help="run终止编号(开区间),--end=4 代表 run_1,run_2,run_3")
    parser.add_argument("--natom", type=int, default=2, help="需要读取磁矩的原子数目,默认2")
    parser.add_argument("--csv_sys", type=str, default="汇总_体系信息.csv", help="体系能量总磁矩输出文件")
    parser.add_argument("--csv_atom", type=str, default="汇总_原子d磁矩.csv", help="原子d轨道磁矩输出文件")
    args = parser.parse_args()

    # 正则
    reg_energy = r"Final: energy without entropy\s*=\s*([-+]?\d+\.\d+)"
    reg_mag = r"Magnetic moment\s*=\s*([-+]?\d+\.\d+)"
    reg_Fermi_energy = r"Fermi energy :\s+([-+]?\d+\.\d+)"
    reg_atom_mag = r"^\s+(\d+)\s+([+-]?\d+\.\d+)\s+([+-]?\d+\.\d+)\s+([+-]?\d+\.\d+)\s+([+-]?\d+\.\d+)"

    folders = [f"run_{i}" for i in range(args.start, args.end)]
    sys_results = []    # 体系信息：folder, energy, total_mag, fermi
    atom_results = []   # 原子信息：folder, atom_id, d_mu

    for folder in folders:
        outcar_path = os.path.join(folder, "OUTCAR")
        if not os.path.exists(outcar_path):
            print(f"⚠️ {folder} OUTCAR不存在,跳过")
            continue

        with open(outcar_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # 提取体系物理量
        all_e = re.findall(reg_energy, content)
        energy = float(all_e[-1]) if all_e else None

        all_m = re.findall(reg_mag, content)
        mag = float(all_m[-1]) if all_m else None

        all_fermi = re.findall(reg_Fermi_energy, content)
        fermi = float(all_fermi[-1]) if all_fermi else None

        if energy is None:
            print(f"⏭️ {folder} 未找到Final能量,计算未收敛,跳过")
            continue
        sys_results.append([folder, energy, mag, fermi])

        # 提取原子分轨道磁矩
        all_mag_rows = re.findall(reg_atom_mag, content, flags=re.MULTILINE)
        if len(all_mag_rows) >= args.natom:
            last_group = all_mag_rows[-args.natom:]
            for item in last_group:
                atom_id = int(item[0])    # 修正：item[0]才是原子编号
                d_mu = float(item[3])
                atom_results.append([folder, atom_id, d_mu])
                print(f"{folder} 原子 {atom_id}, d轨道磁矩 = {d_mu}")
            print(f"{folder} 最终能量(eV): {energy} , 总磁矩(mu_B): {mag}, 费米能量:{fermi}")
        else:
            print(f"⚠️ {folder} 未能读到完整{args.natom}个原子磁矩数据")

    # 写入体系信息csv
    with open(args.csv_sys, "w", encoding="utf-8-sig") as f:
        f.write("文件夹,最终能量(eV),总磁矩(mu_B),费米能量(eV)\n")
        for row in sys_results:
            f.write(f"{row[0]},{row[1]},{row[2]},{row[3]}\n")

    # 写入原子d磁矩csv
    with open(args.csv_atom, "w", encoding="utf-8-sig") as f:
        f.write("文件夹,原子编号,d轨道磁矩(μB)\n")
        for row in atom_results:
            f.write(f"{row[0]},{row[1]},{row[2]}\n")

    print("\n✅ 导出完成！")
    print(f"体系信息：{args.csv_sys}")
    print(f"原子d磁矩:{args.csv_atom}")

if __name__ == "__main__":
    main()
