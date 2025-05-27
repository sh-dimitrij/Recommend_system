import React, { useEffect, useState } from 'react';

function GradeList() {
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    console.log('Token:', token);
  
    if (!token) {
      setError('Нет токена');
      setLoading(false);
      return;
    }
  
    fetch('http://localhost:8000/api/student-grades/', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
      .then(res => {
        console.log('Response status:', res.status);
        if (res.status === 401) {
          localStorage.removeItem('accessToken');
          throw new Error('Неавторизован');
        }
        if (!res.ok) throw new Error('Ошибка сети');
        return res.json();
      })
      .then(data => {
        console.log('Data received:', data);
        if (!Array.isArray(data)) throw new Error('Неверный формат данных');
        setSubjects(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setError(err.message);
        setLoading(false);
      });
  }, []);
  

  const handleCheckboxChange = (taskProgressId, currentValue) => {
    const token = localStorage.getItem('accessToken');
    if (!token) {
      setError('Нет токена, пожалуйста, войдите в систему');
      return;
    }

    fetch(`http://localhost:8000/api/task-progress/${taskProgressId}/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({ is_completed: !currentValue })
    }).then(() => {
      setSubjects(prevSubjects => {
        return prevSubjects.map(subject => ({
          ...subject,
          modules: subject.modules.map(module => ({
            ...module,
            tasks_progress: module.tasks_progress.map(tp => 
              tp.id === taskProgressId ? { ...tp, is_completed: !currentValue } : tp
            )
          }))
        }));
      });
    }).catch(err => {
      setError('Ошибка при обновлении статуса задания');
    });
  };

  if (loading) return <div>Загрузка...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;

  return (
    <table border="1" cellPadding="5" cellSpacing="0">
      <thead>
        <tr>
          <th>Предмет</th>
          <th>Модуль и задания</th>
          <th>Баллы</th>
        </tr>
      </thead>
      <tbody>
        {subjects.map(subject => (
          <tr key={subject.id}>
            <td>{subject.name}</td>
            <td>
              {subject.modules.map(module => (
                <div key={module.id}>
                  <b>М{module.number}</b>
                  <ul style={{ marginTop: 0, marginBottom: '10px' }}>
                    {module.tasks_progress.map(tp => (
                      <li key={tp.task.id}>
                        <label>
                          <input
                            type="checkbox"
                            checked={tp.is_completed}
                            onChange={() => handleCheckboxChange(tp.id, tp.is_completed)}
                          />
                          {tp.task.type} (до {new Date(tp.task.deadline).toLocaleDateString()})
                        </label>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </td>
            <td>
              {subject.modules.map(module => (
                <div key={module.id}>М{module.number}: {module.max_score}</div>
              ))}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default GradeList;
