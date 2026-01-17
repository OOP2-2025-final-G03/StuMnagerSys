document.addEventListener('DOMContentLoaded', () => {
        const studentSelect = document.getElementById('student_select');
        const subjectSelect = document.getElementById('subject_select');
        const unitInput = document.getElementById('unit_input');

        if (!studentSelect || !subjectSelect || !unitInput) return;

        const endpointTemplate = "/grade/enrolled_subjects/__STUDENT__";

        const resetSubjects = (message) => {
            subjectSelect.innerHTML = '';
            const opt = document.createElement('option');
            opt.value = '';
            opt.textContent = message;
            subjectSelect.appendChild(opt);
            subjectSelect.disabled = true;
            unitInput.value = '';
        };

        const populateSubjects = (subjects, selectedId) => {
            subjectSelect.innerHTML = '';

            const defaultOpt = document.createElement('option');
            defaultOpt.value = '';
            defaultOpt.textContent = '科目を選択してください';
            subjectSelect.appendChild(defaultOpt);

            for (const s of subjects) {
                const opt = document.createElement('option');
                opt.value = String(s.id);
                opt.textContent = `${s.name}（${s.id}）`;
                opt.dataset.credits = String(s.credits);
                if (selectedId && String(selectedId) === String(s.id)) {
                    opt.selected = true;
                }
                subjectSelect.appendChild(opt);
            }

            subjectSelect.disabled = false;

            // 既に選択済みなら単位も反映
            const sel = subjectSelect.selectedOptions && subjectSelect.selectedOptions[0];
            if (sel && sel.dataset && sel.dataset.credits) {
                unitInput.value = sel.dataset.credits;
            } else {
                unitInput.value = '';
            }
        };

        const loadEnrolledSubjects = async (studentId, selectedSubjectId) => {
            if (!studentId) {
                resetSubjects('学籍番号を先に選択してください');
                return;
            }

            const url = endpointTemplate.replace('__STUDENT__', encodeURIComponent(studentId));
            try {
                const res = await fetch(url, {headers: {'Accept': 'application/json', credentials: 'same-origin' }});
                if (!res.ok) throw new Error('HTTP ' + res.status);
                const data = await res.json();

                if (!Array.isArray(data) || data.length === 0) {
                    resetSubjects('履修科目がありません');
                    return;
                }

                populateSubjects(data, selectedSubjectId);
            } catch (e) {
                resetSubjects('科目の取得に失敗しました');
            }
        };

        // 学籍番号変更で履修科目を再取得
        studentSelect.addEventListener('change', () => {
            const sid = studentSelect.value;
            // 学籍番号変更時は科目・単位をリセット
            resetSubjects('読み込み中...');
            loadEnrolledSubjects(sid, '');
        });

        // 科目変更で単位を自動入力
        subjectSelect.addEventListener('change', () => {
            const sel = subjectSelect.selectedOptions && subjectSelect.selectedOptions[0];
            if (sel && sel.dataset && sel.dataset.credits) {
                unitInput.value = sel.dataset.credits;
            } else {
                unitInput.value = '';
            }
        });

        // 初期表示：POSTエラーで戻った場合でも復元できるようにする
        const initialStudent = studentSelect.value;
        const initialSelectedSubject = subjectSelect.dataset.selected || '';
        if (initialStudent) {
            resetSubjects('読み込み中...');
            loadEnrolledSubjects(initialStudent, initialSelectedSubject);
        } else {
            resetSubjects('学籍番号を先に選択してください');
        }
    });