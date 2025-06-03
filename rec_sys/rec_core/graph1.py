# rec_core/graphs_scatter.py
import os, numpy as np, matplotlib.pyplot as plt
os.makedirs("rec_core/outputs/graphs", exist_ok=True)

np.random.seed(42)
num_students, max_modules = 50, 5
student_avg_scores = np.random.uniform(40, 100, num_students)
modules_completed  = np.random.randint(1, max_modules + 1, num_students)

plt.figure(figsize=(6, 4))
plt.scatter(modules_completed, student_avg_scores)
plt.title("Успеваемость vs количество модулей")
plt.xlabel("Пройдено модулей")
plt.ylabel("Средняя оценка")
plt.grid(True)
plt.tight_layout()
plt.savefig("rec_core/outputs/graphs/scatter_progress.png", dpi=300)
plt.close()
print("✅ scatter_progress.png сохранён.")
