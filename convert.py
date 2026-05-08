import docx
import os
import re

def escape_latex(text):
    # Escape special LaTeX characters
    chars = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
        '\\': r'\textbackslash{}',
    }
    # Be careful not to double escape. A simple replacement:
    for c, r in chars.items():
        text = text.replace(c, r)
    return text

def convert_docx_to_latex(docx_path, out_dir):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    doc = docx.Document(docx_path)
    
    latex_preamble = r"""\documentclass[13pt,a4paper]{report}
\usepackage[utf8]{inputenc}
\usepackage[T5]{fontenc}
\usepackage[vietnamese]{babel}
\usepackage{amsmath}
\usepackage{amsfonts}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage[left=3cm,right=2cm,top=2cm,bottom=2cm]{geometry}
\usepackage{titlesec}
\usepackage{tocloft}
\usepackage{hyperref}
\usepackage{float}
\usepackage{tabularx}
\usepackage{caption}
\usepackage{chngcntr}
\usepackage{setspace}
\usepackage{microtype}
\usepackage{enumitem}
\usepackage{tikz}
\usepackage{pgf}
\usepackage{pgfpages}

\counterwithin{figure}{chapter}
\counterwithin{table}{chapter}

\tolerance=1000
\emergencystretch=10pt
\hyphenpenalty=10000

\titleformat{\chapter}[display]
  {\normalfont\bfseries\Large\centering}{\chaptertitlename\ \thechapter}{10pt}{\LARGE}
\titlespacing*{\chapter}{0pt}{-20pt}{20pt}

\hypersetup{
    colorlinks=true,
    linkcolor=black,
    filecolor=magenta,      
    urlcolor=blue,
    pdftitle={Báo cáo Đồ án BusGIS},
}

\begin{document}

\begin{titlepage}
\begin{tikzpicture}[remember picture, overlay]
  \draw[line width = 2pt] ($(current page.north west) + (3cm,-2cm)$) rectangle ($(current page.south east) + (-2cm,2cm)$);
  \draw[line width = 0.5pt] ($(current page.north west) + (3.1cm,-2.1cm)$) rectangle ($(current page.south east) + (-2.1cm,2.1cm)$);
\end{tikzpicture}

\begin{center}
    \vspace*{1cm}
    \Large \textbf{TRƯỜNG ĐẠI HỌC ...} \\
    \Large \textbf{KHOA CÔNG NGHỆ THÔNG TIN} \\
    \vspace{2cm}
    
    \includegraphics[width=4cm]{images/logo.png} 
    
    \vspace{2.5cm}
    \LARGE \textbf{BÁO CÁO ĐỒ ÁN} \\
    \vspace{1cm}
    \Huge \textbf{HỆ THỐNG WEBGIS QUẢN LÝ VÀ TRA CỨU TUYẾN XE BUÝT THÔNG MINH (BUSGIS)} \\
    \vspace{3cm}
    
    \Large
    \begin{tabular}{ll}
        \textbf{Giảng viên hướng dẫn:} & TS. Nguyễn Văn A \\
        \textbf{Sinh viên thực hiện:} & Lê Văn B \\
        \textbf{Mã số sinh viên:} & 12345678 \\
    \end{tabular}
    
    \vfill
    \Large TP. Hồ Chí Minh, \the\year
\end{center}
\end{titlepage}

\tableofcontents
\listoffigures
\listoftables
\newpage

\setstretch{1.3}

"""

    main_tex = latex_preamble
    
    current_heading1 = ""
    current_heading2 = ""
    skip_section = False
    in_list = False
    
    chapter_mapped = set()
    img_counter = 1
    
    def end_list_if_needed():
        nonlocal in_list, main_tex
        if in_list:
            main_tex += "\\end{itemize}\n\n"
            in_list = False
            
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
            
        style = para.style.name
        safe_text = escape_latex(text)
        
        # Check for image captions like "Hình 1.1: Sơ đồ..." or "Sơ đồ 4.3..."
        if re.match(r'^(Hình|Sơ đồ)\s*[\d\.\-]+\s*:', text, re.IGNORECASE):
            end_list_if_needed()
            caption_text = re.sub(r'^(Hình|Sơ đồ)\s*[\d\.\-]+\s*:\s*', '', safe_text, flags=re.IGNORECASE)
            main_tex += f"\\begin{{figure}}[H]\n\\centering\n\\includegraphics[width=\\textwidth]{{images/image{img_counter}.png}}\n\\caption{{{caption_text}}}\n\\end{{figure}}\n\n"
            img_counter += 1
            continue
            
        if style.startswith('Heading 1'):
            end_list_if_needed()
            skip_section = False
            current_heading1 = text.upper()
            
            # Map to 6 chapters
            if "LỜI MỞ ĐẦU" in current_heading1 or "TỔNG QUAN" in current_heading1:
                if "CH1" not in chapter_mapped:
                    main_tex += "\\chapter{TỔNG QUAN ĐỀ TÀI}\n\n"
                    chapter_mapped.add("CH1")
                elif "LỜI MỞ ĐẦU" in current_heading1:
                    main_tex += "\\section*{Lời mở đầu}\n\n"
                    
            elif "CƠ SỞ LÝ THUYẾT" in current_heading1 or "DỮ LIỆU SỬ DỤNG" in current_heading1:
                if "CH2" not in chapter_mapped:
                    main_tex += "\\chapter{CƠ SỞ LÝ THUYẾT VÀ DỮ LIỆU SỬ DỤNG}\n\n"
                    chapter_mapped.add("CH2")
                if "DỮ LIỆU SỬ DỤNG" in current_heading1:
                    main_tex += "\\section{Dữ liệu sử dụng}\n\n"
                    
            elif "PHƯƠNG PHÁP" in current_heading1:
                if "CH3" not in chapter_mapped:
                    main_tex += "\\chapter{PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG}\n\n"
                    chapter_mapped.add("CH3")
                    
            elif "XÂY DỰNG WEBSITE" in current_heading1:
                if "CH4" not in chapter_mapped:
                    main_tex += "\\chapter{KẾT QUẢ TRIỂN KHAI VÀ XÂY DỰNG WEBSITE}\n\n"
                    chapter_mapped.add("CH4")
                    
            elif "KẾT QUẢ" in current_heading1 or "ĐÁNH GIÁ CHẤT LƯỢNG" in current_heading1:
                if "CH5" not in chapter_mapped:
                    main_tex += "\\chapter{ĐÁNH GIÁ CHẤT LƯỢNG HỆ THỐNG}\n\n"
                    chapter_mapped.add("CH5")
                    
            elif "KẾT LUẬN" in current_heading1:
                if "CH6" not in chapter_mapped:
                    main_tex += "\\chapter{KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN TƯƠNG LAI}\n\n"
                    chapter_mapped.add("CH6")
            else:
                main_tex += f"\\chapter{{{safe_text}}}\n\n"
                
        elif style.startswith('Heading 2'):
            end_list_if_needed()
            current_heading2 = text
            skip_section = False
            
            if "Kết cấu" in text and "đề tài" in text:
                skip_section = True
                continue
                
            main_tex += f"\\section{{{safe_text}}}\n\n"
            
            if "Thuật toán Haversine" in text:
                main_tex += r"""Việc tính toán khoảng cách thực tế giữa hai điểm trên bề mặt Trái Đất sử dụng thuật toán Haversine. Công thức được biểu diễn theo phương trình sau:

\begin{equation}
    a = \sin^2\left(\frac{\Delta \varphi}{2}\right) + \cos(\varphi_1) \cdot \cos(\varphi_2) \cdot \sin^2\left(\frac{\Delta \lambda}{2}\right)
\end{equation}

\begin{equation}
    c = 2 \cdot \text{atan2}\left(\sqrt{a}, \sqrt{1-a}\right)
\end{equation}

\begin{equation}
    d = R \cdot c
\end{equation}

Trong đó $d$ là khoảng cách địa lý, $R$ là bán kính Trái Đất (6371 km), $\varphi$ và $\lambda$ là vĩ độ và kinh độ.
"""
                skip_section = True # Skip the rest of the old text for this section
                
            elif "Kiến trúc hệ thống" in text:
                main_tex += "Kiến trúc hệ thống BusGIS được xây dựng dựa trên mô hình ba lớp (Three-tier Architecture) nhằm đảm bảo tính phân tách rõ ràng giữa các thành phần, tối ưu hóa hiệu suất và nâng cao khả năng mở rộng. Sự phân tách này giúp bảo trì thuận tiện và tăng bảo mật. Bao gồm Tầng Trình diễn (Frontend) dùng React/HTML/CSS/LeafletJS, Tầng Xử lý (Backend) dùng Django Python, và Tầng Dữ liệu dùng PostgreSQL/PostGIS với khả năng lưu trữ không gian vượt trội.\n\n"
            
            elif "Data Flow" in text or "Luồng dữ liệu" in text:
                main_tex += "Quá trình luân chuyển dữ liệu bên trong hệ thống BusGIS được thiết kế khoa học nhằm kiểm soát chặt chẽ trạng thái thông tin. Dữ liệu thô từ OpenStreetMap được tiền xử lý (Data Cleansing) bằng Python scripts, loại bỏ node thừa, chuẩn hóa tọa độ. Sau đó chuyển đổi (Transform) sang dạng hình học WKT để ánh xạ vào PostGIS. Khi truy vấn, Django ORM tính toán và trả về JSON cho Frontend hiển thị qua LeafletJS API.\n\n"
                
            elif "Công nghệ sử dụng" in text:
                main_tex += "Hệ thống sử dụng các công nghệ hiện đại. Cụ thể, Django (Python) làm Web Framework ở Backend mang lại kiến trúc an toàn, tốc độ phát triển nhanh. Hệ quản trị CSDL PostgreSQL kết hợp PostGIS cho phép lưu trữ và xử lý truy vấn không gian phức tạp. Ở Frontend, HTML/CSS và Bootstrap kết hợp cùng LeafletJS cung cấp trải nghiệm bản đồ mượt mà, thân thiện với người dùng.\n\n"
                
        elif style.startswith('Heading 3'):
            end_list_if_needed()
            if skip_section: continue
            main_tex += f"\\subsection{{{safe_text}}}\n\n"
            
        elif style == 'List Paragraph' or re.match(r'^[a-d\-\+]\.\s+', text) or re.match(r'^[\-\+]\s+', text):
            if skip_section: continue
            
            # If under 2.4 or 2.5, force text instead of list
            if "Công nghệ" in current_heading2 or "Nguồn dữ liệu" in current_heading2:
                end_list_if_needed()
                main_tex += f"{safe_text} "
            else:
                if not in_list:
                    main_tex += "\\begin{itemize}\n"
                    in_list = True
                
                # clean bullets
                clean_text = re.sub(r'^[a-d\-\+\.]+\s*', '', safe_text)
                main_tex += f"    \\item {clean_text}\n"
                
        else:
            if skip_section: continue
            end_list_if_needed()
            
            if "Lý do chọn đề tài" in current_heading2:
                # Split long paragraph by sentences
                sentences = safe_text.split('. ')
                for s in sentences:
                    if s:
                        main_tex += f"{s}.\n\n"
            else:
                main_tex += f"{safe_text}\n\n"

    end_list_if_needed()
    main_tex += "\\end{document}\n"
    
    with open(os.path.join(out_dir, "main.tex"), "w", encoding="utf-8") as f:
        f.write(main_tex)
        
if __name__ == "__main__":
    convert_docx_to_latex("Đề tài.docx", "latex_project_real")

