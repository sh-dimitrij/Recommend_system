import React, { useEffect, useState } from "react";
import Sidebar from "./Sidebar";
import ProfilePopup from "./ProfilePopup";
import "./Home.css";
import "./GradeList.css";           // ⬅️ новый файл стилей

function GradeList() {
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);

  const [navOpen, setNavOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [userData, setUserData] = useState(null);

  /** локальный «черновик» всех изменений -------------------- */
  const [draftChanges, setDraftChanges] = useState({
    modules: {},      // { moduleProgressId: newScore }
    tasks: {},        // { taskProgressId: newIsCompleted }
  });
  /* --------------------------------------------------------- */

  /* ---------- начальная загрузка --------------------------------------- */
  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    console.log("Access token:", token);
    Promise.all([
        fetch("http://localhost:8000/api/user/", {
          headers: { Authorization: `Bearer ${token}` },
        }).then((r) => r.json()),
        fetch("http://localhost:8000/api/student-grades/", {
          headers: { Authorization: `Bearer ${token}` },
        }).then((r) => r.json()),
      ])
        .then(([user, subj]) => {
          console.log('Subjects from API:', subj);
          setUserData(user);
          if (subj && Array.isArray(subj.subjects)) {
            setSubjects(subj.subjects);
          } else {
            setSubjects([]);
          }
        })
        .catch(() => {
          localStorage.removeItem("accessToken");
          window.location.reload();
        })
        .finally(() => setLoading(false));
      
  }, []);
  
  /* --------------------------------------------------------------------- */

  /* ---------- обработчики черновика ----------------------------------- */
  /** ввод баллов */
  const handleScoreEdit = (moduleProgressId, value, maxScore) => {
    const num = Math.max(
      0,
      Math.min(parseInt(value || 0, 10), maxScore) // ограничение
    );
    setDraftChanges((prev) => ({
      ...prev,
      modules: { ...prev.modules, [moduleProgressId]: num },
    }));
    // моментально отражаем в UI, не трогая оригинальные данные
    setSubjects((prev) =>
      prev.map((sub) => ({
        ...sub,
        modules: sub.modules.map((m) =>
          m.module_progress_id === moduleProgressId ? { ...m, score: num } : m
        ),
      }))
    );
  };

  /** галочка */
  const handleCheckboxChange = (taskProgressId, currentValue) => {
    setDraftChanges((prev) => ({
      ...prev,
      tasks: { ...prev.tasks, [taskProgressId]: !currentValue },
    }));
    setSubjects((prev) =>
      prev.map((subj) => ({
        ...subj,
        modules: subj.modules.map((mod) => ({
          ...mod,
          tasks_progress: mod.tasks_progress.map((tp) =>
            tp.id === taskProgressId ? { ...tp, is_completed: !currentValue } : tp
          ),
        })),
      }))
    );
  };
  /* --------------------------------------------------------------------- */

  /* ---------- Сохранение ---------------------------------------------- */
  const handleSave = () => {
    const token = localStorage.getItem("accessToken");
  
    // Формируем payload, который ждет backend
    const payload = subjects.flatMap(subject =>
      subject.modules.map(module => ({
        id: module.module_progress_id,
        score: module.score,
        tasks_progress: module.tasks_progress.map(tp => ({
          id: tp.id,
          is_completed: tp.is_completed,
        })),
      }))
    );
  
    fetch("http://localhost:8000/api/save-progress/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    })
      .then((res) => {
        if (!res.ok) throw new Error("Ошибка сохранения");
        return res.json();
      })
      .then(() => {
        setDraftChanges({ modules: {}, tasks: {} }); // очистка черновика
        // alert("Прогресс успешно сохранён");
      })
      .catch((err) => {
        console.error(err);
        alert("Ошибка при сохранении");
      });
  };
  
  /* -------------------------------------------------------------------- */

  /* --------------------- Рендер --------------------------------------- */
  if (loading) return <div>Загрузка…</div>;

  const hasChanges =
    Object.keys(draftChanges.modules).length ||
    Object.keys(draftChanges.tasks).length;

  return (
    <>
      {/* бургер */}
      <button
        className={`nav-button ${navOpen ? "open" : ""}`}
        onClick={() => setNavOpen(!navOpen)}
        aria-label="Открыть навигацию"
      >
        {navOpen ? "×" : "≡"}
      </button>

      {/* профиль */}
      <button
        className="profile-button"
        onClick={() => setProfileOpen(true)}
        aria-label="Профиль"
      >
        <img
          className="profile-avatar"
          src="https://www.w3schools.com/howto/img_avatar.png"
          alt="profile"
        />
      </button>

      <Sidebar
        open={navOpen}
        onClose={() => setNavOpen(false)}
        onNavigate={(path) => (window.location.href = path)}
      />
      <ProfilePopup
        open={profileOpen}
        onClose={() => setProfileOpen(false)}
        user={userData}
        logout={() => {
          localStorage.removeItem("accessToken");
          window.location.reload();
        }}
      />

      {/* таблица */}
      <div className="main-container">
        <table className="grade-table">
          <thead>
            <tr>
              <th>Предмет</th>
              <th>Модуль и&nbsp;задания</th>
              <th>Баллы</th>
            </tr>
          </thead>
          <tbody>
            {subjects.map((subject) =>
              subject.modules.map((module, idx) => (
                <tr key={`${subject.id}-${module.id}`}>
                  {idx === 0 && (
                    <td rowSpan={subject.modules.length}>{subject.name}</td>
                  )}

                  <td>
                    <b>М{module.number}</b>
                    <ul className="task-list">
                      {module.tasks_progress.map((tp) => (
                        <li key={tp.task.id}>
                          <label className="nice-checkbox">
                            <input
                              type="checkbox"   
                              checked={tp.is_completed}
                              onChange={() =>
                                handleCheckboxChange(
                                  tp.id,
                                  tp.is_completed
                                )
                              }
                            />
                            <span></span>
                            {tp.task.type}{" "}
                              (до{" "}
                              {new Date(
                                tp.task.deadline
                              ).toLocaleDateString()}
                              )
                          </label>
                        </li>
                      ))}
                    </ul>
                  </td>

                  <td className="score-cell">
                    <input
                      type="number"
                      value={module.score}
                      min="0"
                      max={module.max_score}
                      onChange={(e) =>
                        handleScoreEdit(
                          module.module_progress_id,
                          e.target.value,
                          module.max_score
                        )
                      }
                    />{" "}
                    / {module.max_score}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>


        <div className="save-btn-container">
        <button
            className="save-btn"
            onClick={handleSave}
            disabled={!hasChanges}
        >
            Сохранить
        </button>
        </div>

      </div>
    </>
  );
}

export default GradeList;
