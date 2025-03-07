import json
import os
import argparse
from datetime import datetime
import re

def escape_latex(text):
    """
    Escape LaTeX special characters in text.
    
    Args:
        text (str): Text to escape
        
    Returns:
        str: Text with LaTeX special characters escaped
    """
    # Define LaTeX special characters and their escaped versions
    special_chars = {
        '&': '\\&',
        '%': '\\%',
        '$': '\\$',
        '#': '\\#',
        '_': '\\_',
        '{': '\\{',
        '}': '\\}',
        '~': '\\textasciitilde{}',
        '^': '\\textasciicircum{}',
        '\\': '\\textbackslash{}',  # This needs to be last to avoid double escaping
    }
    
    # Replace special characters with their escaped versions
    for char, replacement in special_chars.items():
        if char == '\\':  # Handle backslash specially to avoid double escaping
            # Replace only standalone backslashes, not already escaped ones
            text = text.replace('\\', '\\textbackslash{}')
        else:
            text = text.replace(char, replacement)
    
    # Handle quotes properly
    text = text.replace('"', "''")
    
    return text

def json_to_latex_cv(json_data):
    """
    Convert a JSON resume data structure to LaTeX code for a CV.
    
    Args:
        json_data (dict): The resume data as a Python dictionary.
        
    Returns:
        str: LaTeX code for the CV.
    """
    # Extract data from JSON
    name = f"{json_data['name']['first']} {json_data['name']['first2']} {json_data['name']['family']} {json_data['name']['family2']}"
    
    # Handle contact information
    address = json_data.get('address', '')
    website = json_data.get('website', '')
    phone = json_data.get('phone', '')
    email_data = json_data.get('email', {})
    primary_email = email_data.get('google', email_data.get('uc', email_data.get('proton', '')))
    
    # Handle education and skills
    education = json_data.get('education', {})
    titulo = education.get('titulo', '')
    major = education.get('major', '')
    major_track = education.get('major-track', '')
    minor = education.get('minor', '')
    certificado = education.get('certificado academico', '')
    awards = json_data.get('awards', [])
    english = json_data.get('english', '')
    
    # Handle courses and teaching
    courses = json_data.get('courses', [])
    ayudantias = json_data.get('ayudantias', [])
    
    # Handle technical skills
    dev_technologies = json_data.get('dev-technologies', [])
    dev_techniques = json_data.get('dev-techniques', [])
    dev_soft_skills = json_data.get('dev-soft-skills', [])
    favorite_paradigm = json_data.get('favorite-paradigm', '')
    
    # Handle publications and additional information
    publications = json_data.get('publications', '')
    dev_philosophy = json_data.get('dev-philosophy', '')
    admin_skills = json_data.get('admin-skills', [])
    
    # Handle graphic design experience
    graphic_design = json_data.get('graphic-design-experience', [])
    
    # Create LaTeX document
    latex = []
    
    # Document class and packages
    latex.append("\\documentclass[11pt,a4paper,sans]{moderncv}")
    latex.append("\\moderncvstyle{classic}")
    latex.append("\\moderncvcolor{blue}")
    latex.append("\\usepackage[scale=0.75]{geometry}")
    latex.append("\\usepackage[utf8]{inputenc}")
    
    # Personal information
    latex.append("\\name{" + name + "}{}")
    if address:
        latex.append("\\address{" + address + "}{}")
    if phone:
        latex.append("\\phone{" + phone + "}")
    if primary_email:
        latex.append("\\email{" + primary_email + "}")
    if website:
        latex.append("\\homepage{" + website + "}")
    
    # Social accounts
    if 'github' in json_data and 'username' in json_data['github']:
        latex.append("\\social[github]{" + json_data['github']['username'] + "}")
    
    latex.append("\\begin{document}")
    latex.append("\\hypersetup{colorlinks=true, linkcolor=blue, urlcolor=blue}")
    latex.append("\\makecvtitle")
    
    # Education section
    latex.append("\\section{Education}")
    
    # List each education field separately
    if titulo:
        latex.append("\\cvitem{Título}{" + escape_latex(titulo) + "}")
    
    if major:
        major_text = escape_latex(major)
        if major_track:
            major_text += f" Track {escape_latex(major_track)}"
        latex.append("\\cvitem{Major}{" + major_text + "}")
    
    if minor:
        latex.append("\\cvitem{Minor}{" + escape_latex(minor) + "}")
    
    if certificado:
        latex.append("\\cvitem{Certificado Académico}{" + escape_latex(certificado) + "}")
    
    if awards:
        latex.append("\\subsection{Awards}")
        for award in awards:
            latex.append("\\cvitem{}{" + escape_latex(award) + "}")
    
    # Languages
    if english:
        latex.append("\\section{Languages}")
        latex.append("\\cvitem{English}{" + escape_latex(english) + "}")
        latex.append("\\cvitem{Spanish}{Native}")
    
    # Technical Skills
    latex.append("\\section{Technical Skills}")
    
    if dev_technologies:
        technologies_str = ", ".join(escape_latex(tech) for tech in dev_technologies)
        latex.append("\\cvitem{Technologies}{" + technologies_str + "}")
    
    if favorite_paradigm:
        latex.append("\\cvitem{Preferred Paradigm}{" + escape_latex(favorite_paradigm) + "}")
    
    if dev_techniques:
        techniques_str = ", ".join(escape_latex(tech) for tech in dev_techniques)
        latex.append("\\cvitem{Development Techniques}{" + techniques_str + "}")
    
    if dev_soft_skills:
        soft_skills_str = ", ".join(escape_latex(skill) for skill in dev_soft_skills)
        latex.append("\\cvitem{Domain Knowledge}{" + soft_skills_str + "}")
    
    # Courses section
    if courses:
        latex.append("\\section{Relevant Coursework}")
        
        # Sort courses by semester
        sorted_courses = sorted(courses, key=lambda x: x.get('semester', ''))
        
        for course in sorted_courses:
            course_name = escape_latex(course.get('name', ''))
            semester = escape_latex(course.get('semester', ''))
            latex.append("\\cvitem{" + semester + "}{" + course_name + "}")
    
    # Teaching assistant experience
    if ayudantias:
        latex.append("\\section{Teaching Experience}")
        for course in ayudantias:
            latex.append("\\cvitem{Teaching Assistant}{" + escape_latex(course) + "}")
    
    # Graphic Design section
    if graphic_design:
        latex.append("\\section{Graphic Design}")
        # Join the first few examples with proper LaTeX formatting for hyperlinks
        examples = graphic_design[:3]  # Limit to first 3 examples to avoid overcrowding
        examples_str = ""
        for i, example in enumerate(examples):
            if i > 0:
                examples_str += ", "
            # Create hyperlink for each example - extract the filename from the URL
            filename = example.split('/')[-1]
            examples_str += f"\\href{{{example}}}{{{filename}}}"
        
        if examples:
            latex.append("\\cvitem{Portfolio Samples}{" + examples_str + "}")
            if len(graphic_design) > 3:
                latex.append("\\cvitem{}{Additional examples available on request}")
    
    # Administrative Skills
    if admin_skills:
        latex.append("\\section{Administrative Skills}")
        for skill in admin_skills:
            latex.append("\\cvitem{}{" + escape_latex(skill) + "}")
    
    # Publications
    if publications:
        latex.append("\\section{Publications \\& Research}")
        
        # Use a different approach - split text into URL and non-URL parts
        pub_text = publications
        url_pattern = r'(https?://[^\s)"]+)'
        
        # Split the text by URLs - this gives us alternating non-URL and URL segments
        segments = re.split(url_pattern, pub_text)
        
        # Process each segment
        formatted_segments = []
        for i, segment in enumerate(segments):
            # Even indices are non-URL text, odd indices are URLs
            if i % 2 == 0:
                # Non-URL text: escape LaTeX special characters
                formatted_segments.append(escape_latex(segment))
            else:
                # URL: format as hyperlink
                url = segment
                display_url = url
                if len(url) > 40:
                    display_url = url[:37] + "..."
                href = f"\\href{{{url}}}{{{display_url}}}"
                formatted_segments.append(href)
        
        # Join all formatted segments
        final_text = ''.join(formatted_segments)
        latex.append("\\cvitem{}{" + final_text + "}")
    
    # Development Philosophy (as extra information)
    if dev_philosophy:
        latex.append("\\section{Development Philosophy}")
        # Use the directly provided philosophy text which has already been refined
        escaped_philosophy = escape_latex(dev_philosophy)
        latex.append("\\cvitem{}{" + escaped_philosophy + "}")
    
    # Close document
    latex.append("\\end{document}")
    
    return "\n".join(latex)

def main():
    parser = argparse.ArgumentParser(description='Convert JSON resume to LaTeX CV')
    parser.add_argument('json_file', help='Path to JSON resume file')
    parser.add_argument('--output', '-o', help='Output LaTeX file path (default: cv.tex)')
    
    args = parser.parse_args()
    output_file = args.output if args.output else 'cv.tex'
    
    try:
        with open(args.json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        latex_cv = json_to_latex_cv(json_data)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(latex_cv)
        
        print(f"CV successfully generated: {output_file}")
        
    except FileNotFoundError:
        print(f"Error: The file {args.json_file} was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file {args.json_file} is not valid JSON.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()

