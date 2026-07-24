import pandas as pd
import matplotlib.pyplot as plt
import csv_tool
import logging
import argparse

# ========== 日志配置区域 ========== 日志器（Logger）多 Handler 分发配置
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# logger.setLevel(logging.INFO)`
# 可选：`DEBUG` / `INFO` / `WARNING` / `ERROR`
# # 防止重复添加handler，避免日志重复打印
if logger.handlers:
    logger.handlers.clear()

log_format = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
# 控制台输出
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_format)
# 文件输出
file_handler = logging.FileHandler("energy_plot_log.txt", encoding="utf-8-sig")
file_handler.setFormatter(log_format)

logger.addHandler(console_handler)
logger.addHandler(file_handler)


# logger.info("正常运行信息")
# logger.warning("警告信息")
# logger.error("错误信息")
# =================================

class EnergyPlotter:
    # class：定义类 → 对象的模板（图纸），可以打包一堆变量 + 一堆函数
    def __init__(self):
        # __init__ = 工厂出厂初始化流程
        plt.rcParams["font.family"] = ["SimHei"]
        plt.rcParams["axes.unicode_minus"] = False
        # self.变量名：对象属性，整个类所有方法共享
        self.df = None
        self.x_data = None
        self.y_data = None

    def load_data(self, csv_path=None):
        if csv_path is None:
            csv_path = csv_tool.get_latest_csv()
            logger.info(f"未传入csv路径，自动获取最新csv: {csv_path}")
        else:
            logger.info(f"使用指定csv文件: {csv_path}")

        self.df = pd.read_csv(csv_path)
        self.x_data = self.df["文件夹"]
        self.y_data = self.df["最终能量(eV)"]
        logger.info(f"成功载入数据，共 {len(self.df)} 组任务")

    def draw_plot(self, figsize=(8, 6), text_offset=0.03):
        plt.figure(figsize=figsize)
        line, = plt.plot(self.x_data, self.y_data, "bo-", linewidth=2, markersize=8)
        xs = line.get_xdata()
        ys = line.get_ydata()
        plt.xlabel("计算任务", fontsize=12)
        plt.ylabel("最终能量(eV)", fontsize=12)
        plt.title("各任务能量对比图", fontsize=14)
        plt.grid(True, linestyle='--', alpha=0.6)

        for xi, yi in zip(xs, ys):
            plt.text(xi, yi + text_offset, f"{yi:.4f}", ha='center', va='bottom', fontsize=10)
        logger.info("绘图画布绘制完成")

    def save_and_show(self):
        plt.savefig("energy_comparison.png", dpi=300, bbox_inches='tight')  # 控制保存图片的边框空白
        plt.savefig("energy_comparison.svg", bbox_inches="tight")  # 矢量图
        logger.info("图片已保存：energy_comparison.png / energy_comparison.svg")
        plt.show()

    def run(self, figsize=(8, 6), text_offset=0.03, csv_path=None):
        try:
            self.load_data(csv_path=csv_path)
            self.draw_plot(figsize=figsize, text_offset=text_offset)
            self.save_and_show()
        except Exception as e:
            logger.error(f"绘图流程发生异常：{e}", exc_info=True)
            raise


def draw_energy(figsize=(8, 6), text_offset=0.03, csv_path=None):
    plotter = EnergyPlotter()
    plotter.run(figsize=figsize, text_offset=text_offset, csv_path=csv_path)


def main():
    parser = argparse.ArgumentParser(description="能量对比绘图工具，读取CSV绘制各任务能量曲线")
    parser.add_argument("--csv-path", type=str, default=None, help="指定CSV文件路径，不填自动选取最新csv")
    parser.add_argument("--fig-width", type=float, default=8.0, help="画布宽度，默认8.0")
    parser.add_argument("--fig-height", type=float, default=6.0, help="画布高度，默认6.0")
    parser.add_argument("--text-offset", type=float, default=0.03, help="数值标签向上偏移量，默认0.03")
    args = parser.parse_args()

    figsize = (args.fig_width, args.fig_height)
    draw_energy(
        figsize=figsize,
        text_offset=args.text_offset,
        csv_path=args.csv_path
    )

# 终端命令行参数
# → args对象(main函数)
# → draw_energy()
# → EnergyPlotter.run()
# → load_data() / draw_plot()
# → 真正执行绘图、读取文件

if __name__ == "__main__":
    main()



# # 默认，自动加载最新CSV
# py .\class_plot_energy.py

# # 指定csv + 自定义画布
# py .\class_plot_energy.py --csv-path 汇总_体系信息.csv --fig-width 10 --fig-height 6 --text-offset 0.05

# # 查看帮助
# py .\class_plot_energy.py -h
###