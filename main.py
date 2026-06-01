from nicegui import ui
import json
import os
from datetime import date

# =========================
# 달력 스타일 설정
# =========================
ui.add_head_html("""
<style>
/* 달력 상단 파란색 헤더 배경 */
.q-date__header {
    background-color: #4a90e2 !important;
}

/* 파란색 헤더 안의 선택된 날짜/년도 표시 */
.q-date__header,
.q-date__header *,
.q-date__header-title,
.q-date__header-title span,
.q-date__header-subtitle,
.q-date__header-subtitle span,
.q-date__header-label,
.q-date__header-label span,
.q-date__header button,
.q-date__header button span {
    color: white !important;
    font-weight: bold !important;
}

/* 선택된 년도 숫자가 들어가는 영역 */
.q-date__header-title {
    font-size: 26px !important;
    color: white !important;
}

/* 년도 선택 화면에서 선택된 년도 버튼 */
.q-date__years-item--active,
.q-date__years-item--active span,
.q-date__years-item--active button,
.q-date__years-item--active button span {
    color: white !important;
    font-weight: bold !important;
}
</style>
""")

# =========================
# 파일 설정
# =========================
TASK_FILE = 'tasks.json'

# =========================
# 전역 상태
# =========================
tasks = []
current_filter = 'all'  # all, active, completed

task_list_area = None
all_filter_button = None
active_filter_button = None
completed_filter_button = None


# =========================
# 데이터 저장 / 불러오기
# =========================
def load_tasks():
    global tasks

    if not os.path.exists(TASK_FILE):
        tasks = []
        save_tasks()
        return

    try:
        with open(TASK_FILE, 'r', encoding='utf-8') as file:
            tasks = json.load(file)
    except json.JSONDecodeError:
        tasks = []
        save_tasks()


def save_tasks():
    with open(TASK_FILE, 'w', encoding='utf-8') as file:
        json.dump(tasks, file, ensure_ascii=False, indent=4)


def get_next_id():
    if not tasks:
        return 1

    max_id = max(task['id'] for task in tasks)
    return max_id + 1


# =========================
# 기능 함수
# =========================
def add_task(title_input, description_input, due_date_input):
    title = title_input.value.strip()
    description = description_input.value.strip()
    due_date = due_date_input.value

    if title == '':
        ui.notify('과제 제목을 입력하세요.', color='negative')
        return

    if due_date is None or due_date == '':
        ui.notify('마감일을 선택하세요.', color='negative')
        return

    new_task = {
        'id': get_next_id(),
        'title': title,
        'description': description,
        'due_date': str(due_date),
        'completed': False
    }

    tasks.append(new_task)
    save_tasks()

    title_input.value = ''
    description_input.value = ''
    due_date_input.set_value(date.today().isoformat())

    ui.notify('과제가 추가되었습니다.', color='positive')
    render_tasks()


def toggle_task(task_id):
    for task in tasks:
        if task['id'] == task_id:
            task['completed'] = not task['completed']
            break

    save_tasks()
    render_tasks()


def delete_task(task_id):
    global tasks

    tasks = [task for task in tasks if task['id'] != task_id]
    save_tasks()

    ui.notify('과제가 삭제되었습니다.', color='warning')
    render_tasks()


def set_filter(filter_type):
    global current_filter

    current_filter = filter_type
    update_filter_button_styles()
    render_tasks()


def update_filter_button_styles():
    buttons = [
        (all_filter_button, current_filter == 'all'),
        (active_filter_button, current_filter == 'active'),
        (completed_filter_button, current_filter == 'completed')
    ]
    
    for btn, is_selected in buttons:
        if btn:
            # 모든 테두리 클래스 제거
            btn.classes(remove='border-2 border-green-500 border border-gray-300')
            # 선택 여부에 따라 새 클래스 적용
            if is_selected:
                btn.classes('border-2 border-green-500 bg-white text-black font-bold')
            else:
                btn.classes('border border-gray-300 bg-white text-black font-bold')


def get_filtered_tasks():
    if current_filter == 'completed':
        return [task for task in tasks if task['completed']]
    elif current_filter == 'active':
        return [task for task in tasks if not task['completed']]
    else:
        return tasks


# =========================
# 화면 렌더링
# =========================
def render_tasks():
    task_list_area.clear()

    filtered_tasks = get_filtered_tasks()

    with task_list_area:
        if not filtered_tasks:
            ui.label('표시할 과제가 없습니다.').classes(
                'text-gray-500 text-center w-full mt-4'
            )
            return

        for task in filtered_tasks:
            status_text = '완료' if task['completed'] else '미완료'

            with ui.card().classes('w-full mb-3 p-4'):
                with ui.row().classes('w-full items-center justify-between'):
                    with ui.column().classes('gap-1'):
                        if task['completed']:
                            ui.label(task['title']).classes(
                                'text-lg font-bold line-through text-gray-500'
                            )
                        else:
                            ui.label(task['title']).classes(
                                'text-lg font-bold'
                            )

                        if task['description']:
                            ui.label(task['description']).classes(
                                'text-sm text-gray-600'
                            )

                        ui.label(f'마감일: {task["due_date"]}').classes(
                            'text-sm text-blue-700'
                        )

                        ui.label(f'상태: {status_text}').classes(
                            'text-sm text-gray-700'
                        )

                    with ui.row().classes('gap-2'):
                        if task['completed']:
                            ui.button(
                                '미완료로 변경',
                                on_click=lambda task_id=task['id']: toggle_task(task_id)
                            ).props('outline')
                        else:
                            ui.button(
                                '완료',
                                on_click=lambda task_id=task['id']: toggle_task(task_id)
                            ).props('outline')

                        ui.button(
                            '삭제',
                            on_click=lambda task_id=task['id']: delete_task(task_id)
                        ).props('color=negative outline')


# =========================
# 앱 화면 구성
# =========================
load_tasks()

ui.label('AI 기반 대학생 과제 관리 웹앱').classes(
    'text-3xl font-bold mb-2'
)

ui.label('바이브코딩을 활용하여 개발한 과제 관리 프로그램입니다.').classes(
    'text-gray-600 mb-6'
)

with ui.card().classes('w-full max-w-3xl p-5'):
    ui.label('과제 추가').classes('text-xl font-bold mb-3')

    title_input = ui.input('과제 제목').classes('w-full text-black')
    description_input = ui.textarea('과제 설명').classes('w-full text-black')
    today = date.today().isoformat()
    due_date_input = ui.date(value=today).classes('w-full text-black')

    ui.timer(
        0.1,
        lambda: due_date_input.set_value(date.today().isoformat()),
        once=True
    )

    ui.button(
        '과제 추가',
        on_click=lambda: add_task(title_input, description_input, due_date_input)
    ).classes('mt-3')

with ui.card().classes('w-full max-w-3xl p-5 mt-5'):
    ui.label('과제 목록').classes('text-xl font-bold mb-3')

    with ui.row().classes('gap-2 mb-4'):
        all_filter_button = ui.button('전체', on_click=lambda: set_filter('all')).classes('border-2 border-green-500 bg-white text-black font-bold')
        completed_filter_button = ui.button('완료', on_click=lambda: set_filter('completed')).classes('border border-gray-300 bg-white text-gray-700 font-bold')
        active_filter_button = ui.button('미완료', on_click=lambda: set_filter('active')).classes('border border-gray-300 bg-white text-gray-700 font-bold')

    update_filter_button_styles()
    task_list_area = ui.column().classes('w-full')

render_tasks()

ui.run(port=8090)
