import json
import os
import argparse
from datetime import datetime

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
    admin_skills = json_data.get('admin-skills', [])
    
    # Create LaTeX document
    latex = []
    
    # Document class and packages
    latex.append(r"\documentclass[11pt,a4paper,sans]{moderncv}")
    latex.append(r"\moderncvstyle{classic}")
    latex.append(r"\moderncvcolor{blue}")
    latex.append(r"\usepackage[scale=0.75]{geometry}")
    latex.append(r"\usepackage[utf8]{inputenc}")
    
    # Personal information
    latex.append(r"\name{" + name + r"}{}")
    if address:
        latex.append(r"\address{" + address + r"}{}")
    if phone:
        latex.append(r"\phone{" + phone + r"}")
    if primary_email:
        latex.append(r"\email{" + primary_email + r"}")
    if website:
        latex.append(r"\homepage{" + website + r"}")
    
    # Social accounts
    if 'github' in json_data and 'username' in json_data['github']:
        latex.append(r"\social[github]{" + json_data['github']['username'] + r"}")
    
    latex.append(r"\begin{document}")
    latex.append(r"\makecvtitle")
    
    # Education section
    latex.append(r"\section{Education}")
    
    education_text = titulo
    if major:
        education_text += f", {major}"
    if minor:
        education_text += f", Minor in {minor}"
    
    latex.append(r"\cvitem{Degree}{" + education_text + r"}")
    
    if awards:
        latex.append(r"\subsection{Awards}")
        for award in awards:
            latex.append(r"\cvitem{}{" + award + r"}")
    
    # Languages
    if english:
        latex.append(r"\section{Languages}")
        latex.append(r"\cvitem{English}{" + english + r"}")
        latex.append(r"\cvitem{Spanish}{Native}")
    
    # Technical Skills
    latex.append(r"\section{Technical Skills}")
    
    if dev_technologies:
        technologies_str = ", ".join(dev_technologies)
        latex.append(r"\cvitem{Technologies}{" + technologies_str + r"}")
    
    if favorite_paradigm:
        latex.append(r"\cvitem{Preferred Paradigm}{" + favorite_paradigm + r"}")
    
    if dev_techniques:
        techniques_str = ", ".join(dev_techniques)
        latex.append(r"\cvitem{Development Techniques}{" + techniques_str + r"}")
    
    if dev_soft_skills:
        soft_skills_str = ", ".join(dev_soft_skills)
        latex.append(r"\cvitem{Domain Knowledge}{" + soft_skills_str + r"}")
    
    # Courses section
    if courses:
        latex.append(r"\section{Relevant Coursework}")
        
        # Sort courses by semester
        sorted_courses = sorted(courses, key=lambda x: x.get('semester', ''))
        
        for course in sorted_courses:
            course_name = course.get('name', '')
            semester = course.get('semester', '')
            latex.append(r"\cvitem{" + semester + r"}{" + course_name + r"}")
    
    # Teaching assistant experience
    if ayudantias:
        latex.append(r"\section{Teaching Experience}")
        for course in ayudantias:
            latex.append(r"\cvitem{Teaching Assistant}{" + course + r"}")
    
    # Administrative Skills
    if admin_skills:
        latex.append(r"\section{Administrative Skills}")
        for skill in admin_skills:
            latex.append(r"\cvitem{}{" + skill + r"}")
    
    # Publications
    if publications:
        latex.append(r"\section{Publications \& Research}")
        latex.append(r"\cvitem{}{" + publications + r"}")
    
    # Development Philosophy (as extra information)
    if dev_philosophy:
        latex.append(r"\section{Development Philosophy}")
        # Break down the philosophy into paragraphs
        philosophy_paragraphs = dev_philosophy.split(". ")
        philosophy_formatted = ""
        
        for i, paragraph in enumerate(philosophy_paragraphs):
            if i < len(philosophy_paragraphs) - 1:
                philosophy_formatted += paragraph + ". "
                if (i + 1) % 3 == 0:  # Create a new paragraph every 3 sentences
                    philosophy_formatted += "\\\\"
            else:
                philosophy_formatted += paragraph
        
        latex.append(r"\cvitem{}{" + philosophy_formatted + r"}")
    
    # Close document
    latex.append(r"\end{document}")
    
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
