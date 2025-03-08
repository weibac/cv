import json
import os
import argparse
import re
from datetime import datetime
from pathlib import Path

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

def download_image(url, output_path):
    """
    Download an image from a URL and save it to the specified path.
    
    Args:
        url (str): URL of the image to download
        output_path (str): Local path where the image will be saved
        
    Returns:
        bool: True if download was successful, False otherwise
    """
    try:
        import requests
        from pathlib import Path
        
        # Create directory if it doesn't exist
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Download the image
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return True
        else:
            print(f"Failed to download image: HTTP status code {response.status_code}")
            return False
    except Exception as e:
        print(f"Error downloading image: {str(e)}")
        return False

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
    
    # Handle profile picture
    picture_url = json_data.get('picture', '')
    
    # Handle education and skills
    education = json_data.get('education', {})
    titulo = education.get('titulo', '')
    major = education.get('major', '')
    major_track = education.get('major-track', '')
    minor = education.get('minor', '')
    certificado = education.get('certificado academico', '')
    awards = json_data.get('awards', [])
    
    # Handle languages
    languages = json_data.get('languages', {})
    english = languages.get('english', '')
    spanish = languages.get('spanish', '')
    french = languages.get('french', '')
    
    # Handle teaching experience
    teaching = json_data.get('teaching', [])
    
    # Handle courses
    courses = json_data.get('courses', [])
    
    # Handle technical skills
    dev_technologies = json_data.get('dev-technologies', [])
    dev_techniques = json_data.get('dev-techniques', [])
    dev_soft_skills = json_data.get('dev-soft-skills', [])
    favorite_paradigm = json_data.get('favorite-paradigm', '')
    favorite_editor = json_data.get('favorite-code-editor', '')
    
    # Handle publications and additional information
    publications = json_data.get('publications', '')
    dev_philosophy = json_data.get('dev-philosophy', '')
    admin_skills = json_data.get('admin-skills', [])
    preferred_role = json_data.get('preferred role', '')
    metadata = json_data.get('metadata', {})
    
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
    latex.append("\\usepackage{needspace}")
    latex.append("\\usepackage{placeins}")
    latex.append("\\usepackage{graphicx}")
    
    # Add commands to prevent page breaks in sections
    latex.append("\\newcommand{\\preventbreaksection}[1]{")
    latex.append("  \\needspace{3\\baselineskip}")
    latex.append("  \\section{#1}")
    latex.append("  \\FloatBarrier")
    latex.append("}")
    
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
    
    # Profile picture
    if picture_url:
        # Photo will be added through moderncv's photo command
        latex.append("\\photo[64pt][0.4pt]{profile-pic}")  # Size and frame thickness
    
    # Social accounts
    if 'github' in json_data and 'username' in json_data['github']:
        latex.append("\\social[github]{" + json_data['github']['username'] + "}")
    
    latex.append("\\begin{document}")
    latex.append("\\hypersetup{colorlinks=true, linkcolor=blue, urlcolor=blue}")
    latex.append("\\makecvtitle")
    
    # Education section
    latex.append("\\preventbreaksection{Education}")
    
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
    if languages:
        latex.append("\\preventbreaksection{Languages}")
        if english:
            latex.append("\\cvitem{English}{" + escape_latex(english) + "}")
        if spanish:
            latex.append("\\cvitem{Spanish}{" + escape_latex(spanish) + "}")
        if french:
            latex.append("\\cvitem{French}{" + escape_latex(french) + "}")
    
    # Technical Skills
    latex.append("\\preventbreaksection{Technical Skills}")
    
    if dev_technologies:
        technologies_str = ", ".join(escape_latex(tech) for tech in dev_technologies)
        latex.append("\\cvitem{Technologies}{" + technologies_str + "}")
    
    if favorite_paradigm:
        latex.append("\\cvitem{Preferred Paradigm}{" + escape_latex(favorite_paradigm) + "}")
    
    if favorite_editor:
        latex.append("\\cvitem{Preferred Editor}{" + escape_latex(favorite_editor) + "}")
    
    if dev_techniques:
        techniques_str = ", ".join(escape_latex(tech) for tech in dev_techniques)
        latex.append("\\cvitem{Development Techniques}{" + techniques_str + "}")
    
    if dev_soft_skills:
        soft_skills_str = ", ".join(escape_latex(skill) for skill in dev_soft_skills)
        latex.append("\\cvitem{Domain Knowledge}{" + soft_skills_str + "}")
    
    # Courses section
    if courses:
        latex.append("\\preventbreaksection{Relevant Coursework}")
        
        # Sort courses by semester
        sorted_courses = sorted(courses, key=lambda x: x.get('semester', ''))
        
        for course in sorted_courses:
            course_name = escape_latex(course.get('name', ''))
            semester = escape_latex(course.get('semester', ''))
            latex.append("\\cvitem{" + semester + "}{" + course_name + "}")
    
    # Teaching assistant experience
    if teaching:
        latex.append("\\preventbreaksection{Teaching Experience}")
        for item in teaching:
            course = item.get('course', '')
            role = item.get('role', '')
            if course and role:
                latex.append("\\cvitem{" + escape_latex(role) + "}{" + escape_latex(course) + "}")
    
    # Graphic Design section
    if graphic_design:
        latex.append("\\preventbreaksection{Graphic Design}")
        # Join the first few examples with proper LaTeX formatting for hyperlinks
        examples = graphic_design[:4]  # Increased to 4 examples as requested
        examples_str = ""
        for i, example in enumerate(examples):
            if i > 0:
                examples_str += ", "
            # Create hyperlink for each example - extract the filename from the URL
            filename = example.split('/')[-1]
            examples_str += f"\\href{{{example}}}{{{filename}}}"
        
        if examples:
            latex.append("\\cvitem{Portfolio Samples}{" + examples_str + "}")
            if len(graphic_design) > 4:
                latex.append("\\cvitem{}{Additional examples available on request}")
    
    # Administrative Skills
    if admin_skills:
        latex.append("\\preventbreaksection{Administrative Skills}")
        for skill in admin_skills:
            latex.append("\\cvitem{}{" + escape_latex(skill) + "}")
    
    # Publications
    if publications:
        latex.append("\\preventbreaksection{Publications \\& Research}")
        
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
        latex.append("\\preventbreaksection{Development Philosophy}")
        # Use the directly provided philosophy text which has already been refined
        escaped_philosophy = escape_latex(dev_philosophy)
        latex.append("\\cvitem{}{" + escaped_philosophy + "}")
    
    # Preferred Role
    if preferred_role:
        latex.append("\\preventbreaksection{Preferred Role}")
        latex.append("\\cvitem{}{" + escape_latex(preferred_role) + "}")
    
    # Metadata and source code link
    if metadata:
        uri = metadata.get('uri', '')
        explanation = metadata.get('explanation', '')
        if uri and explanation:
            # Process the explanation text to replace {uri} with the actual URI
            explanation = explanation.replace('{uri}', uri)
            
            latex.append("\\preventbreaksection{Meta}")
            latex.append("\\cvitem{}{" + escape_latex(explanation) + "}")
            latex.append("\\cvitem{Source}{\\href{" + uri + "}{" + uri + "}}")
    
    # Close document
    latex.append("\\end{document}")
    
    return "\n".join(latex)

def main():
    parser = argparse.ArgumentParser(description='Convert JSON resume to LaTeX CV')
    parser.add_argument('json_file', help='Path to JSON resume file')
    parser.add_argument('--output', '-o', help='Output LaTeX file path (default: cv.tex)')
    parser.add_argument('--no-image', action='store_true', help='Skip downloading profile image')
    
    args = parser.parse_args()
    output_file = args.output if args.output else 'cv.tex'
    output_dir = os.path.dirname(output_file) or '.'
    
    try:
        with open(args.json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Handle profile picture if URL is provided
        picture_url = json_data.get('picture', '')
        if picture_url and not args.no_image:
            # Determine image file extension
            image_ext = os.path.splitext(picture_url.split('/')[-1])[1]
            if not image_ext:
                image_ext = '.jpg'  # Default to jpg if no extension
                
            # Set image output path
            image_path = os.path.join(output_dir, 'profile-pic' + image_ext)
            
            # Download image
            print(f"Downloading profile picture from {picture_url}...")
            success = download_image(picture_url, image_path)
            
            if success:
                print(f"Profile picture downloaded to {image_path}")
                # Strip extension for LaTeX since moderncv handles extensions
                if image_ext:
                    base_image_path = os.path.splitext(os.path.basename(image_path))[0]
                    json_data['picture'] = base_image_path
            else:
                print("Failed to download profile picture, continuing without image")
                json_data['picture'] = ''
        
        latex_cv = json_to_latex_cv(json_data)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(latex_cv)
        
        print(f"CV successfully generated: {output_file}")
        print("Compile it with: pdflatex " + output_file)
        
    except FileNotFoundError:
        print(f"Error: The file {args.json_file} was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file {args.json_file} is not valid JSON.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()

