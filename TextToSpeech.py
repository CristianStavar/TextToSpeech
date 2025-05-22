"""Takes text and pdf files and transfom it in audio."""
import tkinter as tk
from tkinter import filedialog, messagebox, Tk

import os
from pydub import AudioSegment
from TTS.api import TTS

import re
import pdfplumber
from num2words import num2words


class TextToSpeechApp:

    chosen_lang = "en"
    total_pages = 0
    reader = ""
    first_warning = 0

    def text_to_speech_list(self, text_chunks, lang='en', output_file='output.wav',  temp_dir='temp_audio'):
        """ TTS Models.

        print("SPANISH   -   'tts_models/es/css10/vits'  ")
        print("ENGLISH   -   'tts_models/en/ljspeech/vits'  ")

        """
        # Create temporary directory
        os.makedirs(temp_dir, exist_ok=True)

        temp_files = []

        try:
            if lang == "es":
                tts = TTS(model_name="tts_models/es/css10/vits",
                          progress_bar=True)
            else:
                tts = TTS(model_name="tts_models/en/ljspeech/vits",
                          progress_bar=True)

            # Process each chunk separately
            for i, chunk in enumerate(text_chunks):
                print(f"Processing chunk {i+1}/{len(text_chunks)}")

                # Generate speech
                temp_file = os.path.join(temp_dir, f'temp_{i}.wav')
                tts.tts_to_file(text=chunk, file_path=temp_file)

                temp_files.append(temp_file)

            # Combine all audio files
            print("Combining audio files...")
            combined = AudioSegment.empty()

            for temp_file in temp_files:
                sound = AudioSegment.from_wav(temp_file)
                combined += sound

            # Export combined audio
            combined.export(output_file, format=output_file.split('.')[-1])
            print(f"Successfully created {output_file}")

        finally:
            # Clean up temporary files
            for temp_file in temp_files:
                try:
                    os.remove(temp_file)
                except:
                    pass

    def on_check(self, lang):
        #Changes the language and the chekboxes
        if lang == "es":
            self.checkbox_en.set(0)
            self.chosen_lang = "es"
        else:
            self.checkbox_es.set(0)
            self.chosen_lang = "en"

    def __init__(self, root):
        self.root = root
        self.root.title("Text/PDF Processor")

        # Left side - Text input
        self.text_frame = tk.Frame(root)
        self.text_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.text_label = tk.Label(self.text_frame, text="Enter Text:")
        self.text_label.pack(anchor=tk.W)

        self.text_entry = tk.Text(self.text_frame, height=20, width=40)
        self.text_entry.pack()

        self.process_text_btn = tk.Button(
            self.text_frame, text="Process Text", command=self.process_text)
        self.process_text_btn.pack(pady=5)

        # Right side - PDF input
        self.pdf_frame = tk.Frame(root)
        self.pdf_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        self.checkbox_frame = tk.Frame(self.pdf_frame)
        self.checkbox_frame.pack(pady=5)

        # Variables for mutual exclusion
        self.checkbox_es = tk.IntVar()
        self.checkbox_en = tk.IntVar()

        self.cb_es = tk.Checkbutton(
            self.checkbox_frame,
            text="Español",
            variable=self.checkbox_es,
            command=lambda: self.on_check("es")
        )
        self.cb_es.pack(side=tk.LEFT, padx=5)

        self.cb_en = tk.Checkbutton(
            self.checkbox_frame,
            text="English",
            variable=self.checkbox_en,
            command=lambda: self.on_check("en")
        )
        self.cb_en.pack(side=tk.LEFT, padx=5)

        self.pdf_label = tk.Label(self.pdf_frame, text="No PDF selected")
        self.pdf_label.pack()
        self.pdf_label_pages = tk.Label(self.pdf_frame, text="")
        self.pdf_label_pages.pack()

        self.select_pdf_btn = tk.Button(
            self.pdf_frame, text="Select PDF", command=self.select_pdf)
        self.select_pdf_btn.pack(pady=5)

        # Number input fields
        self.numbers_frame = tk.Frame(self.pdf_frame)
        self.numbers_frame.pack(pady=10)

        self.num1_entry = tk.Entry(self.numbers_frame, width=5)
        self.num1_entry.pack(side=tk.LEFT, padx=5)
        self.num2_entry = tk.Entry(self.numbers_frame, width=5)
        self.num2_entry.pack(side=tk.LEFT, padx=5)

        self.numbers_label_frame = tk.Frame(self.pdf_frame)
        self.numbers_label_frame.pack()

        tk.Label(self.numbers_label_frame, text="Starting page").pack(
            side=tk.LEFT, padx=18)
        tk.Label(self.numbers_label_frame, text="End page").pack(
            side=tk.LEFT, padx=18)

        self.process_pdf_btn1 = tk.Button(
            self.pdf_frame, text="Process selected pages", command=self.process_pdf_pages)
        self.process_pdf_btn1.pack(pady=5)

        self.process_pdf_btn2 = tk.Button(
            self.pdf_frame, text="Process whole document ", command=self.process_pdf_full)
        self.process_pdf_btn2.pack(pady=5)

        # Store PDF path
        self.pdf_path = None

    def extract_pdf_page(self, page_num):
        try:
            page = self.reader.pages[page_num]
            page.cropbox = page.mediabox
            # Returns empty string if no text
            return page.extract_text(x_tolerance=1, y_tolerance=1) or ""

        except Exception as e:
            print(f"Error reading page {page_num}: {str(e)}")
            return ""

    def clean_text(self, text):

        # Convert multiple newlines → single space
        text = re.sub(r'\n+', ' ', text)
        text = re.sub(r'[^\w\s.,!?]', '', text)  # Remove special chars
        text = text.strip()  # Remove whitespace
        #Changes numbers for strings, easier for the tts
        if self.chosen_lang == "es":
            processed = re.sub(
                r'\d+', lambda x: num2words(x.group(), lang='es'), text)
        else:
            processed = re.sub(
                r'\d+', lambda x: num2words(x.group(), lang='en'), text)

        if len(processed) > 3 or text.isdigit():
            return processed
        else:
            return ""

    def process_text(self):
        text = self.text_entry.get("1.0", tk.END).strip()
        cleaned_text = self.clean_text(text)
        list_txt = [cleaned_text]

        if text:
            # Show first 50 chars
            show_info("Processing Text", f"Text:\n{text[:50]}...")

            self.text_to_speech_list(list_txt, self.chosen_lang)

        else:
            messagebox.showwarning(
                "Empty Text", "Please enter some text to process")

    def select_pdf(self):
        self.pdf_path = filedialog.askopenfilename(
            filetypes=[("PDF Files", "*.pdf")])
        if self.pdf_path:
            self.pdf_label.config(
                text=f"Selected: {self.pdf_path.split('/')[-1]}")

            self.reader = pdfplumber.open(self.pdf_path)
            self.total_pages = len(self.reader.pages)
            self.pdf_label_pages.config(text=f"Pages: {self.total_pages}")

    def process_pdf_pages(self):
        if self.pdf_path:
            pages_list = []
            try:
                num1 = int(self.num1_entry.get())
                num2 = int(self.num2_entry.get())

                if num1 < 1 or num2 < 1:
                    messagebox.showinfo(
                        "Error", f"Pages musst be bigger than 0.")
                    return
                if num1 > num2:
                    messagebox.showinfo(
                        "Error", f"Starting page: {num1} can't be bigger than end page: {num2}.")
                    return

                if num1 > self.total_pages or num2 > self.total_pages:
                    messagebox.showinfo(
                        "Error", f"Starting and ending page cant be bigger than the total pages of the document.")
                    return

                if num1 == num2:
                    page = self.extract_pdf_page(num1)
                    pages_list.append(page)

                else:
                    for page in range(num1-1, num2):
                        page_text = self.extract_pdf_page(page)

                        pages_list.append(page_text)

                show_info("Processing pages",
                          f"Processing PDF pages from {num1} to {num2}.")
                pages_list = [self.clean_text(
                    page) for page in pages_list if self.clean_text(page)]
                self.text_to_speech_list(pages_list, self.chosen_lang)
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers")
        else:
            messagebox.showwarning("No PDF", "Please select a PDF file first")

    def process_pdf_full(self):
        if self.pdf_path:
            try:
                if self.total_pages >= 5 and self.first_warning < 1:
                    messagebox.showerror(
                        "Error", "Warning big files take longer to process.\n Try again to ignore this message.")
                    self.first_warning += 1
                    return

                pages_list = []
                show_info("Processing",
                          "Processing all pages, this may take a while.")
                for page in range(self.total_pages):
                    page_text = self.extract_pdf_page(page)

                    pages_list.append(page_text)

                pages_list = [self.clean_text(
                    page) for page in pages_list if self.clean_text(page)]
                self.text_to_speech_list(pages_list, self.chosen_lang)
            except ValueError:
                messagebox.showerror(
                    "Error", "Try a smaller file or select pages.")
        else:
            messagebox.showwarning("No PDF", "Please select a PDF file first")


def show_info(panel_name, panel_text):
    blank_root = Tk()
    blank_root.withdraw()
    top = tk.Toplevel()
    top.title(panel_name)
    tk.Label(top, text=panel_text).pack(pady=10)
    tk.Button(top, text="OK", command=top.destroy).pack(pady=5)
    blank_root.update()


if __name__ == "__main__":
    root = tk.Tk()
    app = TextToSpeechApp(root)
    root.mainloop()
