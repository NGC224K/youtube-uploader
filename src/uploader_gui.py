# 필요한 라이브러리 임포트
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk, Toplevel
import sqlite3
import pyperclip
import re

# ==============================================================================
# 데이터베이스 초기화 및 연동
# ==============================================================================
def init_db():
    """데이터베이스 파일을 만들고 'templates' 테이블을 초기화합니다."""
    conn = sqlite3.connect('youtube_uploader.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY,
            template_name TEXT NOT NULL,
            title_template TEXT,
            description_template TEXT,
            tags_template TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_template(name, title, desc, tags):
    """새로운 템플릿을 데이터베이스에 저장합니다."""
    conn = sqlite3.connect('youtube_uploader.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO templates (template_name, title_template, description_template, tags_template) VALUES (?, ?, ?, ?)",
                       (name, title, desc, tags))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"데이터베이스 저장 오류: {e}")
        return False
    finally:
        conn.close()

def update_template(template_id, name, title, desc, tags):
    """기존 템플릿을 데이터베이스에서 수정합니다."""
    conn = sqlite3.connect('youtube_uploader.db')
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE templates SET template_name=?, title_template=?, description_template=?, tags_template=? WHERE id=?",
                       (name, title, desc, tags, template_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"데이터베이스 수정 오류: {e}")
        return False
    finally:
        conn.close()

def delete_template(template_id):
    """데이터베이스에서 템플릿을 삭제합니다."""
    conn = sqlite3.connect('youtube_uploader.db')
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM templates WHERE id=?", (template_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"데이터베이스 삭제 오류: {e}")
        return False
    finally:
        conn.close()

def get_templates():
    """데이터베이스에서 모든 템플릿 목록을 가져옵니다."""
    conn = sqlite3.connect('youtube_uploader.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, template_name FROM templates ORDER BY id DESC")
    templates = cursor.fetchall()
    conn.close()
    return templates

def get_template_by_id(template_id):
    """특정 ID의 템플릿 내용을 가져옵니다."""
    conn = sqlite3.connect('youtube_uploader.db')
    cursor = conn.cursor()
    cursor.execute("SELECT title_template, description_template, tags_template FROM templates WHERE id=?", (template_id,))
    template = cursor.fetchone()
    conn.close()
    return template

# ==============================================================================
# GUI 인터페이스
# ==============================================================================
class YouTubeUploaderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("유튜브 업로더 템플릿 관리")
        self.geometry("750x600")

        self.create_widgets()
        self.refresh_template_list()
        self.selected_template_id = None  # 선택된 템플릿 ID를 저장할 변수

    def create_widgets(self):
        """GUI 위젯들을 생성하고 배치합니다."""
        main_frame = tk.Frame(self, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 템플릿 관리 영역
        template_frame = tk.LabelFrame(main_frame, text="템플릿 관리", padx=10, pady=10)
        template_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.template_listbox = tk.Listbox(template_frame, height=20, width=30)
        self.template_listbox.pack(fill=tk.BOTH, expand=True)
        self.template_listbox.bind('<<ListboxSelect>>', self.load_selected_template)
        
        # 저장/수정/삭제 버튼 프레임
        action_frame = tk.Frame(template_frame)
        action_frame.pack(pady=5, fill=tk.X)
        self.save_button = tk.Button(action_frame, text="새 템플릿 저장", command=self.save_current_template)
        self.save_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))
        self.update_button = tk.Button(action_frame, text="수정", command=self.update_current_template)
        self.update_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        self.delete_button = tk.Button(action_frame, text="삭제", command=self.delete_current_template)
        self.delete_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(2, 0))

        # 템플릿 내용 편집 영역
        editor_frame = tk.LabelFrame(main_frame, text="템플릿 내용 편집", padx=10, pady=10)
        editor_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        tk.Label(editor_frame, text="템플릿 이름").pack(anchor='w')
        self.template_name_entry = tk.Entry(editor_frame, width=60)
        self.template_name_entry.pack(fill=tk.X, pady=(0, 10))

        tk.Label(editor_frame, text="제목").pack(anchor='w')
        self.title_text = scrolledtext.ScrolledText(editor_frame, height=2, width=60, wrap=tk.WORD)
        self.title_text.pack(fill=tk.X, pady=(0, 5))

        tk.Label(editor_frame, text="설명").pack(anchor='w')
        self.description_text = scrolledtext.ScrolledText(editor_frame, height=10, width=60, wrap=tk.WORD)
        self.description_text.pack(fill=tk.X, pady=(0, 5))

        tk.Label(editor_frame, text="태그 (쉼표로 구분)").pack(anchor='w')
        self.tags_text = scrolledtext.ScrolledText(editor_frame, height=2, width=60, wrap=tk.WORD)
        self.tags_text.pack(fill=tk.X, pady=(0, 10))

        # 동적 변수 관리 버튼
        tk.Button(editor_frame, text="변수 입력 및 적용", command=self.open_variable_input).pack(pady=(0, 10), fill=tk.X)

        # 클립보드 복사 버튼들
        button_frame = tk.Frame(editor_frame)
        button_frame.pack(fill=tk.X)
        tk.Button(button_frame, text="제목 복사", command=lambda: self.copy_to_clipboard('title')).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        tk.Button(button_frame, text="설명 복사", command=lambda: self.copy_to_clipboard('desc')).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        tk.Button(button_frame, text="태그 복사", command=lambda: self.copy_to_clipboard('tags')).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        tk.Button(button_frame, text="모두 복사", command=lambda: self.copy_to_clipboard('all')).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        # 동적 변수 도움말 섹션
        help_frame = tk.LabelFrame(editor_frame, text="📌 변수 사용법", padx=10, pady=5)
        help_frame.pack(fill=tk.X, pady=(10, 0))
        help_text = "템플릿에 `{{변수이름}}` 형태로 변수를 넣어두면, [변수 입력 및 적용] 버튼을 눌러 값을 채울 수 있습니다.\n예시: `{{게임명}}`, `{{플레이타임}}`"
        tk.Label(help_frame, text=help_text, justify=tk.LEFT).pack(anchor='w')


    def refresh_template_list(self):
        """템플릿 리스트박스를 최신화합니다."""
        self.template_listbox.delete(0, tk.END)
        self.templates_data = get_templates()
        for template in self.templates_data:
            self.template_listbox.insert(tk.END, template[1]) # template_name

    def load_selected_template(self, event):
        """리스트박스에서 템플릿을 선택하면 내용을 불러옵니다."""
        selected_index = self.template_listbox.curselection()
        if not selected_index:
            self.selected_template_id = None
            return

        self.selected_template_id = self.templates_data[selected_index[0]][0]
        template_name = self.templates_data[selected_index[0]][1]
        title, desc, tags = get_template_by_id(self.selected_template_id)
        
        self.template_name_entry.delete(0, tk.END)
        self.template_name_entry.insert(tk.END, template_name)
        
        self.title_text.delete('1.0', tk.END)
        self.title_text.insert('1.0', title)

        self.description_text.delete('1.0', tk.END)
        self.description_text.insert('1.0', desc)

        self.tags_text.delete('1.0', tk.END)
        self.tags_text.insert('1.0', tags)

    def save_current_template(self):
        """현재 입력된 내용을 새로운 템플릿으로 저장합니다."""
        name = self.template_name_entry.get()
        title = self.title_text.get('1.0', tk.END).strip()
        desc = self.description_text.get('1.0', tk.END).strip()
        tags = self.tags_text.get('1.0', tk.END).strip()

        if not name or not title:
            messagebox.showwarning("입력 오류", "템플릿 이름과 제목은 필수입니다.")
            return

        if save_template(name, title, desc, tags):
            messagebox.showinfo("성공", "템플릿이 저장되었습니다!")
            self.refresh_template_list()
            self.clear_editor()

    def update_current_template(self):
        """현재 선택된 템플릿을 수정합니다."""
        if not self.selected_template_id:
            messagebox.showwarning("오류", "수정할 템플릿을 먼저 선택해주세요.")
            return

        name = self.template_name_entry.get()
        title = self.title_text.get('1.0', tk.END).strip()
        desc = self.description_text.get('1.0', tk.END).strip()
        tags = self.tags_text.get('1.0', tk.END).strip()

        if not name or not title:
            messagebox.showwarning("입력 오류", "템플릿 이름과 제목은 필수입니다.")
            return
        
        if update_template(self.selected_template_id, name, title, desc, tags):
            messagebox.showinfo("성공", "템플릿이 수정되었습니다!")
            self.refresh_template_list()
            self.clear_editor()

    def delete_current_template(self):
        """현재 선택된 템플릿을 삭제합니다."""
        if not self.selected_template_id:
            messagebox.showwarning("오류", "삭제할 템플릿을 먼저 선택해주세요.")
            return

        response = messagebox.askyesno("삭제 확인", "정말 이 템플릿을 삭제하시겠습니까?")
        if response:
            if delete_template(self.selected_template_id):
                messagebox.showinfo("성공", "템플릿이 삭제되었습니다!")
                self.refresh_template_list()
                self.clear_editor()

    def clear_editor(self):
        """편집기를 초기화합니다."""
        self.template_name_entry.delete(0, tk.END)
        self.title_text.delete('1.0', tk.END)
        self.description_text.delete('1.0', tk.END)
        self.tags_text.delete('1.0', tk.END)
        self.selected_template_id = None

    def open_variable_input(self):
        """템플릿의 변수들을 추출하고 입력받는 새 창을 엽니다."""
        # 텍스트 필드에서 모든 변수를 찾음
        all_text = self.title_text.get('1.0', tk.END) + self.description_text.get('1.0', tk.END) + self.tags_text.get('1.0', tk.END)
        variables = sorted(list(set(re.findall(r'\{\{(.*?)\}\}', all_text))))

        if not variables:
            messagebox.showinfo("알림", "템플릿에 변수(`{{변수명}}`)가 없습니다.")
            return

        # 새 창 생성
        var_window = Toplevel(self)
        var_window.title("변수 입력")
        
        entries = {}
        for i, var in enumerate(variables):
            tk.Label(var_window, text=f"{{{{{var}}}}}:").grid(row=i, column=0, padx=5, pady=5, sticky='e')
            entry = tk.Entry(var_window, width=50)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky='w')
            entries[var] = entry
        
        def apply_variables():
            """입력된 변수 값들을 템플릿에 적용합니다."""
            processed_title = self.title_text.get('1.0', tk.END)
            processed_desc = self.description_text.get('1.0', tk.END)
            processed_tags = self.tags_text.get('1.0', tk.END)

            for var, entry in entries.items():
                value = entry.get()
                processed_title = processed_title.replace(f'{{{{{var}}}}}', value)
                processed_desc = processed_desc.replace(f'{{{{{var}}}}}', value)
                processed_tags = processed_tags.replace(f'{{{{{var}}}}}', value)

            self.title_text.delete('1.0', tk.END)
            self.title_text.insert('1.0', processed_title)
            self.description_text.delete('1.0', tk.END)
            self.description_text.insert('1.0', processed_desc)
            self.tags_text.delete('1.0', tk.END)
            self.tags_text.insert('1.0', processed_tags)
            
            var_window.destroy()

        tk.Button(var_window, text="적용", command=apply_variables).grid(row=len(variables), columnspan=2, pady=10)

    def copy_to_clipboard(self, item_type):
        """선택된 항목을 클립보드에 복사합니다."""
        title = self.title_text.get('1.0', tk.END).strip()
        desc = self.description_text.get('1.0', tk.END).strip()
        tags = self.tags_text.get('1.0', tk.END).strip()
        
        output = ""
        if item_type == 'title':
            output = title
        elif item_type == 'desc':
            output = desc
        elif item_type == 'tags':
            output = tags
        elif item_type == 'all':
            output = f"{title}\n\n{desc}\n\n{tags}"
        
        if output:
            pyperclip.copy(output)
            messagebox.showinfo("복사 완료", f"{item_type}이(가) 클립보드에 복사되었습니다.")

# ==============================================================================
# 프로그램 실행
# ==============================================================================
if __name__ == "__main__":
    init_db()
    app = YouTubeUploaderApp()
    app.mainloop()

