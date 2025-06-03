# rec_core/graphs_bar_avg.py
import os, numpy as np, matplotlib.pyplot as plt
os.makedirs("rec_core/outputs/graphs", exist_ok=True)

np.random.seed(42)
num_students, num_books = 50, 10
book_tags    = [set(np.random.choice(range(10), size=np.random.randint(1,5), replace=False)) for _ in range(num_books)]
student_tags = [set(np.random.choice(range(10), size=np.random.randint(1,5), replace=False)) for _ in range(num_students)]

def tag_score(b_tags, s_tags): return len(b_tags & s_tags)
avg_scores = []
for b in range(num_books):
    avg_scores.append(np.mean([tag_score(book_tags[b], st) for st in student_tags]))

plt.figure(figsize=(6, 4))
plt.bar(range(num_books), avg_scores, color="purple")
plt.title("Средний теговый скор для книг")
plt.xlabel("ID книги")
plt.ylabel("Средний скор")
plt.grid(axis="y")
plt.tight_layout()
plt.savefig("rec_core/outputs/graphs/bar_avg_tag_score.png", dpi=300)
plt.close()
print("✅ bar_avg_tag_score.png сохранён.")
