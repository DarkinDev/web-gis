import docx
import sys

def extract_headings(docx_path, out_path):
    try:
        doc = docx.Document(docx_path)
        with open(out_path, 'w', encoding='utf-8') as f:
            for i, para in enumerate(doc.paragraphs):
                if para.style.name.startswith('Heading'):
                    f.write(f"{para.style.name}: {para.text}\n")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_headings(sys.argv[1], "headings.txt")
