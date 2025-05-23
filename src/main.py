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
    primary_email = email_data.get('uc', email_data.get('google', email_data.get('proton', '')))
    
    # Handle profile picture
    picture_url = json_data.get('picture', '')
    
    # Handle education and skills
    education = json_data.get('education', {})
    uc_education = education.get('uc', {})
    titulo = uc_education.get('titulo', '')
    major = uc_education.get('major', '')
    major_track = uc_education.get('major-track', '')
    minor = uc_education.get('minor', '')
    certificado = uc_education.get('certificado academico', '')
    awards = education.get('awards', [])
    
    # Handle additional education with potential links
    additional_edu = education.get('additional', '')
    additional_edu_url = education.get('additional_url', '')
    
    # Handle links in additional education - check if it's a dictionary format
    if isinstance(education.get('additional', ''), dict):
        additional_edu = education['additional'].get('name', '')
        additional_edu_url = education['additional'].get('url', '')
    
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
    # Check if dev-technologies is a list of objects (new format) or strings (old format)
    if dev_technologies and isinstance(dev_technologies[0], dict):
        tech_has_links = True
    else:
        tech_has_links = False
        
    dev_techniques = json_data.get('dev-techniques', [])
    dev_soft_skills = json_data.get('dev-soft-skills', [])
    
    # Handle favorite paradigm with potential links
    favorite_paradigm = json_data.get('favorite-paradigm', '')
    favorite_paradigm_links = json_data.get('favorite-paradigm-links', {})
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
    latex.append("\\usepackage[scale=0.85]{geometry}")  # Increased margins
    latex.append("\\usepackage[utf8]{inputenc}")
    latex.append("\\usepackage{needspace}")
    latex.append("\\usepackage{placeins}")
    latex.append("\\usepackage{graphicx}")
    latex.append("\\usepackage{xcolor}")
    
    # Define a more sophisticated blue
    latex.append("\\definecolor{sophisticatedblue}{RGB}{41, 103, 166}")
    latex.append("\\colorlet{myblue}{sophisticatedblue}")
    
    # Custom styling for more refined look
    latex.append("\\renewcommand{\\sectionfont}{\\Large\\bfseries\\color{myblue}}")
    latex.append("\\renewcommand{\\subsectionfont}{\\large\\mdseries\\color{myblue}}")
    
    # Add vertical space before sections using etoolbox package
    latex.append("\\usepackage{etoolbox}")
    latex.append("\\newcommand{\\sectionspace}{\\vspace{0.6em}}")
    latex.append("\\pretocmd{\\section}{\\sectionspace}{}{}")
    
    # Improve table alignment for cvitems
    latex.append("\\renewcommand{\\cvitem}[3][.25em]{%")
    latex.append("  \\begin{tabular}{@{}p{0.18\\textwidth}@{\\hspace{.5em}}p{0.76\\textwidth}@{}}%")
    latex.append("    \\raggedleft\\bfseries#2 & #3 \\\\%")
    latex.append("  \\end{tabular}%")
    latex.append("  \\par\\addvspace{#1}%")
    latex.append("}")
    
    # Add commands to prevent page breaks in sections
    latex.append("\\newcommand{\\preventbreaksection}[1]{")
    latex.append("  \\needspace{3\\baselineskip}")
    latex.append("  \\section{#1}")
    latex.append("  \\FloatBarrier")
    latex.append("}")
    
    # Personal information
    latex.append("\\name{\\LARGE " + name + "}{}")  # Larger name
    if address:
        latex.append("\\address{" + address + "}{}")
    if phone:
        latex.append("\\phone{" + phone + "}")
    if primary_email:
        latex.append("\\email{" + primary_email + "}")
    if website:
        latex.append("\\homepage{" + website + "}")
    
    # Profile picture - smaller size, better frame
    if picture_url:
        latex.append("\\photo[52pt][1.2pt]{profile-pic}")  # Reduced size, stronger frame
    
    # Social accounts
    if 'github' in json_data and 'username' in json_data['github']:
        latex.append("\\social[github]{" + json_data['github']['username'] + "}")
    
    latex.append("\\begin{document}")
    latex.append("\\hypersetup{colorlinks=true, linkcolor=myblue, urlcolor=myblue}")  # Updated link colors
    latex.append("\\makecvtitle")
    
    # Add some spacing after the title
    latex.append("\\vspace{0.5em}")
    
    # Education section
    latex.append("\\preventbreaksection{Education}")
    
    # UC Education
    if titulo or major or minor or certificado:
        latex.append("\\subsection{Pontificia Universidad Católica de Chile}")
        
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
    
    # Additional Education
    if additional_edu:
        latex.append("\\subsection{Additional Education}")
        if additional_edu_url:
            # Format as hyperlink if URL is available
            latex.append("\\cvitem{}{\\href{" + additional_edu_url + "}{" + escape_latex(additional_edu) + "}}")
        else:
            latex.append("\\cvitem{}{" + escape_latex(additional_edu) + "}")
    
    if awards:
        latex.append("\\subsection{Awards}")
        for award in awards:
            latex.append("\\cvitem{}{" + escape_latex(award) + "}")
    

    # Technical Skills
    latex.append("\\preventbreaksection{Technical Skills}")
    
    if dev_technologies:
        if tech_has_links:
            # New format: List of objects with name and url
            tech_items = []
            for tech in dev_technologies:
                tech_name = escape_latex(tech.get('name', ''))
                tech_url = tech.get('url', '')
                if tech_url:
                    tech_items.append(f"\\href{{{tech_url}}}{{{tech_name}}}")
                else:
                    tech_items.append(tech_name)
            technologies_str = ", ".join(tech_items)
        else:
            # Old format: List of strings
            technologies_str = ", ".join(escape_latex(tech) for tech in dev_technologies)
        
        latex.append("\\cvitem{Technologies}{" + technologies_str + "}")
    
    if favorite_paradigm:
        # First escape the paradigm text
        escaped_paradigm = escape_latex(favorite_paradigm)
        
        # Then add hyperlinks if links are provided (without escaping the href commands)
        if favorite_paradigm_links:
            for lang, url in favorite_paradigm_links.items():
                # Create pattern to match the escaped language name
                import re
                escaped_lang = escape_latex(lang)
                pattern = re.compile(re.escape(escaped_lang), re.IGNORECASE)
                
                # Replace with hyperlink (don't escape the href command)
                # Use raw string for the replacement to avoid escape sequence issues
                replacement = r"\\href{" + url + "}{" + escaped_lang + "}"
                escaped_paradigm = pattern.sub(replacement, escaped_paradigm)
        
        latex.append("\\cvitem{Preferred Paradigm}{" + escaped_paradigm + "}")
    
    if favorite_editor:
        latex.append("\\cvitem{Preferred Editor}{" + escape_latex(favorite_editor) + "}")
    
    if dev_techniques:
        techniques_str = ", ".join(escape_latex(tech) for tech in dev_techniques)
        latex.append("\\cvitem{Development Techniques}{" + techniques_str + "}")
    
    if dev_soft_skills:
        soft_skills_str = ", ".join(escape_latex(skill) for skill in dev_soft_skills)
        latex.append("\\cvitem{Domain Knowledge}{" + soft_skills_str + "}")

    # Courses section - using a more compact layout with multiple courses per row
    if courses:
        latex.append("\\preventbreaksection{Relevant Coursework}")
        
        # Sort courses by semester
        sorted_courses = sorted(courses, key=lambda x: x.get('semester', ''))
        
        # Group courses by semester for more compact display
        semesters = {}
        for course in sorted_courses:
            semester = course.get('semester', '')
            course_name = course.get('name', '')
            if semester not in semesters:
                semesters[semester] = []
            semesters[semester].append(course_name)
        
        # Create more compact display of courses
        for semester, course_list in sorted(semesters.items()):
            courses_text = ", ".join([escape_latex(course) for course in course_list])
            latex.append("\\cvitem{" + escape_latex(semester) + "}{" + courses_text + "}")

    # Teaching assistant experience
    if teaching:
        latex.append("\\preventbreaksection{Teaching Experience}")
        for item in teaching:
            course = item.get('course', '')
            role = item.get('role', '')
            url = item.get('url', '')
            if course and role:
                # If URL is available, create a hyperlink for the course name
                if url:
                    course_text = f"\\href{{{url}}}{{{escape_latex(course)}}}"
                else:
                    course_text = escape_latex(course)
                latex.append("\\cvitem{" + escape_latex(role) + "}{" + course_text + "}")

    # Languages
    if languages:
        latex.append("\\preventbreaksection{Languages}")
        if english:
            latex.append("\\cvitem{English}{" + escape_latex(english) + "}")
        if spanish:
            latex.append("\\cvitem{Spanish}{" + escape_latex(spanish) + "}")
        if french:
            latex.append("\\cvitem{French}{" + escape_latex(french) + "}")
    
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
   
    # Add additional commands for compact layout
    latex.append("\\setlength{\\parskip}{0pt}")  # Minimize paragraph spacing
    latex.append("\\setlength{\\parsep}{0pt}")   # Minimize list item spacing
    latex.append("\\setlength{\\itemsep}{0pt}")  # Minimize space between items

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

