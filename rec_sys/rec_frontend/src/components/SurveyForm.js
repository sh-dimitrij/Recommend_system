  // src/components/SurveyForm.js
  import React, { useState, useEffect, useRef } from "react";
  import "./SurveyForm.css";

  export default function SurveyForm({ userData }) {
    /* ---------- Факультеты ---------- */
    const [facultiesList, setFacultiesList] = useState([]);
    const [faculty, setFaculty] = useState(userData?.faculty || "");
    const [filteredFaculties, setFilteredFaculties] = useState([]);
    const [facultyOpen, setFacultyOpen] = useState(false);
    const [selectingFaculty, setSelectingFaculty] = useState(false);

    /* ---------- Кафедры ---------- */
    const [departmentsList, setDepartmentsList] = useState([]);
    const [department, setDepartment] = useState([]);
    const [filteredDepartments, setFilteredDepartments] = useState([]);
    const [departmentOpen, setDepartmentOpen] = useState(false);
    const [selectingDepartment, setSelectingDepartment] = useState(false);

    /* ---------- Курс ---------- */
    const [coursesList, setCoursesList] = useState([]);
    const [course, setCourse] = useState("");

    /* ---------- Предмет ---------- */
    const [subjectsList, setSubjectsList] = useState([]);
    const [subject, setSubject] = useState(userData?.subject?.id || null);
    const [subjectName, setSubjectName] = useState(userData?.subject?.name || "");
    const [filteredSubjects, setFilteredSubjects] = useState([]);
    const [subjectOpen, setSubjectOpen] = useState(false);
    const [selectingSubject, setSelectingSubject] = useState(false);

    /* ---------- Тэги ---------- */
    const [allTags, setAllTags] = useState([]);
    const [tags, setTags] = useState([]);
    const [tagInput, setTagInput] = useState("");
    const [tagOpen, setTagOpen] = useState(false);
    const [filteredTags, setFilteredTags] = useState([]);
    const tagRef = useRef(null);

    /* ---------- Прочие поля ---------- */
    const [freeTime, setFreeTime] = useState("");
    const [difficulty, setDifficulty] = useState("");

    /* refs для клика вне компонента */
    const facRef = useRef(null);
    const depRef = useRef(null);
    const subjectRef = useRef(null);
    const tagInputRef = useRef(null);



    /* ──────────────────── Загрузка факультетов ──────────────────── */
    useEffect(() => {
      (async () => {
        try {
          const res = await fetch("/api/faculties/");
          const data = await res.json();
          setFacultiesList(data);
          setFilteredFaculties(data);
        } catch (e) {
          console.error("Ошибка загрузки факультетов:", e);
        }
      })();
    }, []);

    /* ──────────────────── Загрузка кафедр ──────────────────── */
    useEffect(() => {
      (async () => {
        try {
          const url = faculty ? `/api/departments/?faculty=${encodeURIComponent(faculty)}` : "/api/departments/";
          const res = await fetch(url);
          const data = await res.json();
          setDepartmentsList(data);
          setFilteredDepartments(data);
        } catch (e) {
          console.error("Ошибка загрузки кафедр:", e);
        }
      })();
    }, [faculty]);
    /* ──────────────────── Загрузка курсов ──────────────────── */
    useEffect(() => {
      (async () => {
        try {
          const res = await fetch("/api/courses/");
          const data = await res.json();
          setCoursesList(data);
        } catch (e) {
          console.error("Ошибка загрузки курсов:", e);
        }
      })();
    }, []);
    /* ──────────────────── Загрузка тэги ──────────────────── */
    useEffect(() => {
      (async () => {
        try {
          const res  = await fetch("/api/tags/");
          const data = await res.json();        // [{id, name}, ...]
          setAllTags(data);
          setFilteredTags(data);
        } catch (e) {
          console.error("Ошибка загрузки тегов:", e);
        }
      })();
    }, []);
    useEffect(() => {
      const search = tagInput.toLowerCase();
    
      const filt = allTags.filter(
        (t) =>
          t.name.toLowerCase().includes(search) &&
          !tags.some((sel) => sel.id === t.id)        // уже выбрали?
      );
    
      setFilteredTags(filt);
    }, [allTags, tags, tagInput]);
    
    
    /* ──────────────────── Загрузка предметов ──────────────────── */
    useEffect(() => {
      (async () => {
        try {
          const params = new URLSearchParams();
          if (course) params.append("course", course);
          if (department) params.append("department", department);
          if (faculty) params.append("faculty", faculty);
    
          const res = await fetch(`/api/subjects/?${params.toString()}`);
          const data = await res.json();
          setSubjectsList(data);
          setFilteredSubjects(data);
        } catch (e) {
          console.error("Ошибка загрузки предметов:", e);
        }
      })();
    }, [course, department, faculty]);
    
    /* ───── закрывать dropdown при клике вне блока ───── */
    useEffect(() => {
      function handleClickOutside(e) {
        if (facRef.current && !facRef.current.contains(e.target)) setFacultyOpen(false);
        if (depRef.current && !depRef.current.contains(e.target)) setDepartmentOpen(false);
        if (subjectRef.current && !subjectRef.current.contains(e.target)) setSubjectOpen(false);
        if (tagRef.current && !tagRef.current.contains(e.target)) setTagOpen(false);

      }
      document.addEventListener("click", handleClickOutside);
      return () => document.removeEventListener("click", handleClickOutside);
    }, []);


    /* ──────────────────── Сохранение формы ──────────────────── */
    const handleSubmit = async (e) => {
      e.preventDefault();
    
      const payload = {
        faculty,
        department,
        course,
        subject,
        free_time: freeTime ? Number(freeTime) : null,
        difficulty_level: difficulty,
        interest_tags: tags.map(t => t.id),
      };
    
      const access = localStorage.getItem('accessToken');   // достаём токен

      try {
        const res = await fetch('http://localhost:8000/api/questionnaire/save/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${access}`,
            // если нужен CSRF, добавить заголовок
          },
          body: JSON.stringify(payload),
        });
    
        if (res.ok) {
          alert('Форма успешно сохранена!');
          // Тут можно сделать что-то ещё, например, перейти на другую страницу
        } else {
          const err = await res.json();
          alert('Ошибка при сохранении анкеты: ' + JSON.stringify(err));
        }
      } catch (error) {
        alert('Ошибка сети: ' + error.message);
      }
    };
    /* ──────────────────── Фильтрация факультетов ──────────────────── */
    const handleFacultyChange = (e) => {
      const val = e.target.value;
      setFaculty(val);

      if (selectingFaculty) {
        setSelectingFaculty(false);
        return;
      }

      const search = val.toLowerCase();
      const filt = facultiesList.filter(
        (f) => f.name.toLowerCase().includes(search) || f.short_name.toLowerCase().includes(search)
      );
      setFilteredFaculties(filt);
      setFacultyOpen(true);
    };

    const chooseFaculty = (name) => {
      setFaculty(name);
      setSelectingFaculty(true);
      setFacultyOpen(false);
      setDepartment("");     // сброс кафедры
      setSubject(null);      // сброс предмета
      setSubjectName("");
    };

    /* ──────────────────── Фильтрация кафедр ──────────────────── */
    const handleDepartmentChange = (e) => {
      const val = e.target.value;
      setDepartment(val);
      
      if (selectingDepartment) {
        setSelectingDepartment(false);
        return;
      }
      
      const search = val.toLowerCase();
      const filt = departmentsList.filter(
        (d) => d.name.toLowerCase().includes(search) || d.short_name.toLowerCase().includes(search)
      );
      setFilteredDepartments(filt);
      setDepartmentOpen(true);
    };
    
    /* ──────────────────── Фильтрация тэгов ──────────────────── */
      /* ──────────────────── Фильтрация тегов ──────────────────── */
    // const handleTagInputChange = (e) => {
    //   const val = e.target.value;
    //   setTagInput(val);

    //   // const search = val.toLowerCase();
    //   // const filt = ALL_TAGS.filter(
    //   //   (t) =>
    //   //     t.toLowerCase().includes(search) &&
    //   //     !tags.includes(t)               // исключаем уже выбранные
    //   // );
    //   // setFilteredTags(filt);  
    //   setTagOpen(true);
    // };

    const chooseTag = (tagObj) => {
      setTags((prev) => [...prev, tagObj]);
      setTagInput("");
      setTagOpen(true);                // оставляем выпадашку открытой
      tagInputRef.current?.focus();
    };
    
    const removeTag = (id) => {
      setTags((prev) => prev.filter((t) => t.id !== id));
    };
    /* ──────────────────── Фильтрация предметов ──────────────────── */
    const handleSubjectChange = (e) => {
      const val = e.target.value;
      setSubjectName(val);
    
      if (selectingSubject) {
        setSelectingSubject(false);
        return;
      }
    
      const search = val.toLowerCase();
      const filt = subjectsList.filter(
        (s) =>
          s.name.toLowerCase().includes(search) ||
          (s.short_name && s.short_name.toLowerCase().includes(search))
      );
      setFilteredSubjects(filt);
      setSubjectOpen(true);
    };
    
    /* Обработчик выбора предмета из списка */
    const chooseSubject = (subj) => {
      setSubject(subj.id);
      setSubjectName(subj.name);
      setSelectingSubject(true);
      setSubjectOpen(false);
    };

    const chooseDepartment = (name) => {
      setDepartment(name);
      setSelectingDepartment(true);
      setDepartmentOpen(false);
      setSubject(null);      // сброс предмета
      setSubjectName("");
    };

    /* ──────────────────── JSX ──────────────────── */
    return (
      <form className="survey-form" onSubmit={handleSubmit}>
        <h2>Форма пользователя</h2>

        {/* ---------- Факультет ---------- */}
        <label style={{ position: "relative" }} ref={facRef}>
          Факультет
          <input
            type="text"
            className="custom-select-input"
            value={faculty}
            onChange={handleFacultyChange}
            onFocus={() => !selectingFaculty && setFacultyOpen(true)}
            placeholder="Введите факультет"
            autoComplete="off"
          />
          {facultyOpen && (
            <ul className="custom-select-dropdown">
              {filteredFaculties.length ? (
                filteredFaculties.map((f) => (
                  <li key={f.id} onClick={() => chooseFaculty(f.name)}>
                    {f.short_name} | {f.name}
                  </li>
                ))
              ) : (
                <li key="no-fac" className="no-option">Нет вариантов</li>

              )}
            </ul>
          )}
        </label>

        {/* ---------- Кафедра ---------- */}
        <label style={{ position: "relative" }} ref={depRef}>
          Кафедра
          <input
            type="text"
            className="custom-select-input"
            value={department}
            onChange={handleDepartmentChange}
            onFocus={() => !selectingDepartment && setDepartmentOpen(true)}
            placeholder="Введите кафедру"
            autoComplete="off"
            disabled={!facultiesList.length} /* если факультеты ещё не загружены */
          />
          {departmentOpen && (
            <ul className="custom-select-dropdown">
              {filteredDepartments.length ? (
                filteredDepartments.map((d) => (
                  <li key={d.id} onClick={() => chooseDepartment(d.name)}>
                    {d.short_name} | {d.name}
                  </li>
                ))
              ) : (
                <li key="no-fac" className="no-option">Нет вариантов</li>

              )}
            </ul>
          )}
        </label>

        {/* ---------- Курс ---------- */}
        <label>
          Курс
          <select
            value={course}
            onChange={(e) => {
              setCourse(e.target.value);
              setSubject(null);
              setSubjectName("");
            }}
            className={`custom-select ${course === "" ? "placeholder" : ""}`}
          >
            <option value="" disabled hidden>Выберите курс</option>
            <option value="">— Нет выбора —</option>
            {coursesList.map((c) => (
              <option key={c.id} value={c.number}>
                {c.number} курс
              </option>
            ))}
          </select>
        </label>



        {/* ---------- Предмет ---------- */}
        {/* Заглушка; логику предметов можно добавить по тому же принципу */}
        <label style={{ position: "relative" }} ref={subjectRef}>
          Предмет
          <input
            type="text"
            className="custom-select-input"
            value={subjectName}
            onChange={handleSubjectChange}
            onFocus={() => !selectingSubject && setSubjectOpen(true)}
            placeholder="Введите предмет"
            autoComplete="off"
          />
          {subjectOpen && (
            <ul className="custom-select-dropdown">
              {filteredSubjects.length ? (
                filteredSubjects.map((s) => (
                  <li key={s.id} onClick={() => chooseSubject(s)}>
                    {s.short_name ? `${s.short_name} | ` : ""}{s.name}
                  </li>
                ))
              ) : (
                <li key="no-fac" className="no-option">Нет вариантов</li>

              )}
            </ul>
          )}
        </label>


        {/* ---------- Остальные поля ---------- */}
        <label>
          Свободное время (часы)
          <input
            type="number"
            value={freeTime}
            onChange={(e) => setFreeTime(e.target.value)}
            placeholder="Например: 5"
          />
        </label>

        <fieldset className="difficulty-group">
          <legend>Уровень сложности</legend>
          <div className="difficulty-group-options">
            {["Начинающий", "Средний", "Продвинутый"].map((lvl) => (
              <label key={lvl} className={`difficulty-option ${difficulty === lvl ? "selected" : ""}`}>
                <input
                  type="radio"
                  name="difficulty"
                  value={lvl}
                  checked={difficulty === lvl}
                  onChange={(e) => setDifficulty(e.target.value)}
                />
                {lvl}
              </label>
            ))}
          </div>
        </fieldset>

        <label style={{ position: "relative" }} ref={tagRef}>
          Тэги (интересы)

          <div className="tags-chips-container">
            <div
              className="tags-chips"
              onMouseDown={(e) => {
                // клик по свободному месту чип-области
                if (e.target === e.currentTarget) {
                  tagInputRef.current?.focus();
                  e.preventDefault();
                }
              }}
            >
              {tags.map((t) => (
                <span key={t.id} className="tag-chip">
                  {t.name}
                  <button
                    type="button"
                    onMouseDown={(e) => {
                      e.stopPropagation();   // не даём всплыть выше
                      removeTag(t.id);
                    }}
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>

            <input
              ref={tagInputRef}
              type="text"
              className="tag-input"
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onFocus={() => setTagOpen(true)}
              placeholder={tags.length ? "" : "Введите тэг"}
              autoComplete="off"
            />
          </div>

          {tagOpen && (
            <ul className="custom-select-dropdown">
              {filteredTags.length ? (
                filteredTags.map((t) => (
                  <li
                    key={t.id}
                    onMouseDown={(e) => {
                      e.preventDefault();
                      chooseTag(t);
                    }}
                  >
                    {t.name}
                  </li>
                ))
              ) : (
                <li key="no-fac" className="no-option">Нет вариантов</li>

                
              )}
            </ul>
          )}
        </label>


        <button type="submit">Получить рекомендацию</button>
      </form>
    );
  }
