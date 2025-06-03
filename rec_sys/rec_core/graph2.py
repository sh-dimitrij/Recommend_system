# rec_core/graphs_hist_book0.py
import os, numpy as np, matplotlib.pyplot as plt
os.makedirs("rec_core/outputs/graphs", exist_ok=True)

np.random.seed(42)
num_students, num_books = 50, 10
book_tags    = [set(np.random.choice(range(10), size=np.random.randint(1,5), replace=False)) for _ in range(num_books)]
student_tags = [set(np.random.choice(range(10), size=np.random.randint(1,5), replace=False)) for _ in range(num_students)]

def tag_score(b_tags, s_tags): return len(b_tags & s_tags)
scores = [tag_score(book_tags[0], st) for st in student_tags]

plt.figure(figsize=(6, 4))
plt.hist(scores, bins=range(6), color="green", alpha=.7, rwidth=.8)
plt.title("Совпадения тэгов: книга №0")
plt.xlabel("Кол-во совпавших тэгов")
plt.ylabel("Число студентов")
plt.grid(True)
plt.tight_layout()
plt.savefig("rec_core/outputs/graphs/hist_book0.png", dpi=300)
plt.close()
print("✅ hist_book0.png сохранён.")
