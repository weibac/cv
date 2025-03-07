import json
import os
import argparse
from datetime import datetime

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
    titulo = json_data.get('titulo', '')
    major = json_data.get('major', '')
    minor = json_data.get('minor', '')
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
    # For clarity, no replacement needed here
    admin_skills = json_data.get('admin-skills', [])
    
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
    latex.append("\\makecvtitle")
    
    # Education section
    latex.append("\\section{Education}")
    
    education_text = escape_latex(titulo)
    if major:
        education_text += f", {escape_latex(major)}"
    if minor:
        education_text += f", Minor in {escape_latex(minor)}"
    
    latex.append("\\cvitem{Degree}{" + education_text + "}")
    
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
    
    # Administrative Skills
    if admin_skills:
        latex.append("\\section{Administrative Skills}")
        for skill in admin_skills:
            latex.append("\\cvitem{}{" + escape_latex(skill) + "}")
    
    # Publications
    if publications:
        latex.append("\\section{Publications \\& Research}")
        latex.append("\\cvitem{}{" + escape_latex(publications) + "}")
    
    # Development Philosophy (as extra information)
    if dev_philosophy:
        latex.append("\\section{Development Philosophy}")
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
