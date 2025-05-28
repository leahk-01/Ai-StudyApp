import flet as ft
import requests

API_URL = "http://127.0.0.1:8005"


PRIMARY_COLOR = "#A8D5BA"
SECONDARY_COLOR = "#D4ECC2"
PAGE_BG = "#F8FFF6"


def main(page: ft.Page):
    page.title = "AI Study Assistant"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = PAGE_BG
    page.padding = 20

    content = ft.Column(expand=True, spacing=20)

    # transcribe
    file_picker = ft.FilePicker()
    file_picker.allowed_extensions = ["wav", "mp3", "m4a", "ogg", "flac"]
    file_picker.file_type = ft.FilePickerFileType.CUSTOM
    page.overlay.append(file_picker)

    transcribe_output = ft.TextField(
        label="Detailed Notes",
        multiline=True,
        expand=True,
        read_only=True,
    )

    def on_file_result(e: ft.FilePickerResultEvent):
        if e.files:
            f = e.files[0]
            resp = requests.post(
                f"{API_URL}/ai/transcribe_detailed_notes",
                files={"audio": (f.name, f.read_bytes())},
            )
            data = resp.json()
            transcribe_output.value = data.get("detailed_notes") or data.get("error") or "Unknown error"
            page.update()

    file_picker.on_result = on_file_result

    transcribe_section = ft.Column(
        [
            ft.Text("Transcribe Audio → Detailed Notes", size=18, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton(
                "Choose Audio File",
                on_click=lambda _: file_picker.pick_files(allow_multiple=False),
                bgcolor=PRIMARY_COLOR,
            ),
            transcribe_output,
        ],
        spacing=10,
        expand=True,
    )

    # summarize
    summar_input = ft.TextField(label="Paste or Type Notes to Summarize", multiline=True, expand=True)
    summar_output = ft.TextField(label="Summary", multiline=True, expand=True, read_only=True)

    def summarize_notes(_):
        resp = requests.post(f"{API_URL}/ai/summary", json={"notes": summar_input.value})
        summar_output.value = resp.json().get("summary", "Error")
        page.update()

    summar_section = ft.Column(
        [
            ft.Text("Summarize Notes", size=18, weight=ft.FontWeight.BOLD),
            summar_input,
            ft.Row(
                [
                    ft.ElevatedButton("Summarize", on_click=summarize_notes, bgcolor=SECONDARY_COLOR),
                    ft.ElevatedButton(
                        "Clear",
                        on_click=lambda _: (
                            setattr(summar_input, "value", ""),
                            setattr(summar_output, "value", ""),
                            page.update(),
                        ),
                    ),
                ],
                spacing=10,
            ),
            summar_output,
        ],
        spacing=10,
        expand=True,
    )

    # -generate botes
    topic_input = ft.TextField(label="Enter Topic", expand=True)
    detailed_output = ft.TextField(label="Generated Notes", multiline=True, expand=True, read_only=True)

    def gen_notes(_):
        resp = requests.post(f"{API_URL}/ai/notes", json={"topic": topic_input.value})
        detailed_output.value = resp.json().get("notes", "Error")
        page.update()

    gen_notes_section = ft.Column(
        [
            ft.Text("Generate Detailed Study Notes", size=18, weight=ft.FontWeight.BOLD),
            topic_input,
            ft.Row(
                [
                    ft.ElevatedButton("Generate Notes", on_click=gen_notes, bgcolor=PRIMARY_COLOR),
                    ft.ElevatedButton(
                        "Clear",
                        on_click=lambda _: (
                            setattr(topic_input, "value", ""),
                            setattr(detailed_output, "value", ""),
                            page.update(),
                        ),
                    ),
                ],
                spacing=10,
            ),
            detailed_output,
        ],
        spacing=10,
        expand=True,
    )

    # upload notes
    upload_input = ft.TextField(label="Paste Notes to Upload", multiline=True, expand=True)

    def upload_notes(_):
        resp = requests.post(f"{API_URL}/ai/upload_notes", json={"notes": upload_input.value})
        msg = resp.json().get("message") or resp.json().get("error") or "Unknown error"
        page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=PRIMARY_COLOR)
        page.snack_bar.open = True
        page.update()

    upload_section = ft.Column(
        [
            ft.Text("Upload Notes to Vector Store", size=18, weight=ft.FontWeight.BOLD),
            upload_input,
            ft.Row(
                [
                    ft.ElevatedButton("Upload", on_click=upload_notes, bgcolor=SECONDARY_COLOR),
                    ft.ElevatedButton(
                        "Clear",
                        on_click=lambda _: (
                            setattr(upload_input, "value", ""),
                            page.update(),
                        ),
                    ),
                ],
                spacing=10,
            ),
        ],
        spacing=10,
        expand=True,
    )

    # quiz
    quiz_subject = ft.TextField(label="Subject", expand=True)
    quiz_num = ft.TextField(label="Number of Questions", expand=True, value="5")
    quiz_output = ft.TextField(label="Quiz", multiline=True, expand=True, read_only=True)

    def gen_quiz(_):
        resp = requests.post(
            f"{API_URL}/ai/generate_quiz",
            json={"subject": quiz_subject.value, "num_questions": int(quiz_num.value)},
        )
        questions = resp.json().get("questions", [])
        quiz_output.value = "\n".join(questions) if questions else str(resp.json())
        page.update()

    quiz_section = ft.Column(
        [
            ft.Text("Generate Quiz", size=18, weight=ft.FontWeight.BOLD),
            quiz_subject,
            quiz_num,
            ft.Row(
                [
                    ft.ElevatedButton("Generate Quiz", on_click=gen_quiz, bgcolor=PRIMARY_COLOR),
                    ft.ElevatedButton(
                        "Clear",
                        on_click=lambda _: (
                            setattr(quiz_subject, "value", ""),
                            setattr(quiz_num, "value", "5"),
                            setattr(quiz_output, "value", ""),
                            page.update(),
                        ),
                    ),
                ],
                spacing=10,
            ),
            quiz_output,
        ],
        spacing=10,
        expand=True,
    )

    #  qa
    qa_input = ft.TextField(label="Ask a Question", expand=True)
    qa_output = ft.TextField(label="Answer", multiline=True, expand=True, read_only=True)

    def ask_qa(_):
        resp = requests.post(f"{API_URL}/ai/qa", json={"query": qa_input.value})
        qa_output.value = resp.json().get("answer", "Error")
        page.update()

    qa_section = ft.Column(
        [
            ft.Text("Ask a Question", size=18, weight=ft.FontWeight.BOLD),
            qa_input,
            ft.Row(
                [
                    ft.ElevatedButton("Ask", on_click=ask_qa, bgcolor=SECONDARY_COLOR),
                    ft.ElevatedButton(
                        "Clear",
                        on_click=lambda _: (
                            setattr(qa_input, "value", ""),
                            setattr(qa_output, "value", ""),
                            page.update(),
                        ),
                    ),
                ],
                spacing=10,
            ),
            qa_output,
        ],
        spacing=10,
        expand=True,
    )



    def on_nav_change(e):
        sections = [
            transcribe_section,
            summar_section,
            gen_notes_section,
            upload_section,
            qa_section,
            quiz_section,
        ]
        content.controls = [sections[e.control.selected_index]]
        page.drawer.open = False
        page.update()

    page.drawer = ft.NavigationDrawer(
        controls=[
            ft.Text("📘 AI Study Assistant", size=24, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR),
            ft.NavigationDrawerDestination(icon=ft.Icons.MIC, label="Transcribe Audio"),
            ft.NavigationDrawerDestination(icon=ft.Icons.SUMMARIZE, label="Summarize Notes"),
            ft.NavigationDrawerDestination(icon=ft.Icons.NOTE_ADD, label="Generate Notes"),
            ft.NavigationDrawerDestination(icon=ft.Icons.UPLOAD_FILE, label="Upload Notes"),
            ft.NavigationDrawerDestination(icon=ft.Icons.HELP, label="Ask a Question"),
            ft.NavigationDrawerDestination(icon=ft.Icons.QR_CODE, label="Generate Quiz"),
        ],
        selected_index=0,
        on_change=on_nav_change,
    )

    page.appbar = ft.AppBar(
        title=ft.Text("AI Study Assistant"),
        bgcolor=PRIMARY_COLOR,
        leading=ft.IconButton(
            icon=ft.Icons.MENU,
            on_click=lambda _: (setattr(page.drawer, "open", True), page.update()),
        ),
    )

    content.controls = [transcribe_section]
    page.add(content)


if __name__ == "__main__":
    ft.app(target=main, view=ft.WEB_BROWSER)
