import re
import json
import os
import requests
import pandas as pd
import xml.etree.ElementTree as ET

# Save data to a JSON file
def save_json(data, file_path):
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)  # Pretty-print with indent

# This section demonstrates how to link the doi with the full text
def doi_to_unique_id(doi):
    """
    Converts a DOI to a unique identifier by replacing slashes with underscores.

    Args:
        doi (str): The DOI of a journal article.

    Returns:
        str: A unique identifier where slashes are replaced with underscores.

    Example:
        >>> doi_to_unique_id("10.1016/j.trc.2023.104311")
        "10.1016_j.trc.2023_104311"
    """
    return doi.replace('/', '_')

import xml.etree.ElementTree as ET
import xml.etree.ElementTree as ET

def extract_sections_and_text_from_xml(file_path):
    """
    Extracts sections and text from an XML file.
    
    Args:
        file_path (str): The path to the XML file.

    Returns:
        list: A list of dictionaries, each containing the label, title, text, subsections, and subsubsections of a section.
    
    Example:
        >>> extract_sections_and_text_from_xml('/path/to/file.xml')
        [{'label': '1', 'title': 'Introduction', 'text': 'This is the introduction...', 'subsections': []}]
    """
    # Parse the XML file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Namespace to handle XML namespaces
    namespaces = {
        'xocs': 'http://www.elsevier.com/xml/xocs/dtd',
        'ce': 'http://www.elsevier.com/xml/common/dtd',
        'ja': 'http://www.elsevier.com/xml/ja/dtd',
        'mml': 'http://www.w3.org/1998/Math/MathML'
    }

    # Extracting the sections using the item-toc element
    sections = []
    for item in root.findall('.//xocs:item-toc-entry', namespaces):
        section_title = item.find('xocs:item-toc-section-title', namespaces)
        section_label = item.find('xocs:item-toc-label', namespaces)
        section_text = []
        
        # Use the section label to find the corresponding section id in <ce:section>
        if section_label is not None and section_title is not None and section_title.text is not None:
            label_text = section_label.text.strip()
            section_elem = root.find(f".//ce:section[ce:label='{label_text}']", namespaces)
        else:
            # If there's no label, find the section by title only (e.g., References)
            if section_title is not None and section_title.text is not None:
                title_text = section_title.text.strip()
                
                # Use double quotes around the title in the XPath query
                section_elem = root.find(f'.//ce:section[ce:section-title="{title_text}"]', namespaces)
                
                # If title_text contains both single and double quotes, escape single quotes
                if section_elem is None and "'" in title_text:
                    escaped_title_text = title_text.replace("'", "&apos;")
                    section_elem = root.find(f".//ce:section[ce:section-title='{escaped_title_text}']", namespaces)
            else:
                section_elem = None
        
        if section_elem is not None:
            # Get all text under the section element, including paragraphs and other texts
            section_text_parts = []
            subsections = []
            before_subsection_text = True

            # Iterate over all elements within the section
            for elem in section_elem:
                # Check if this element is a subsection
                if elem.tag == f"{{{namespaces['ce']}}}section":
                    # This is a subsection, process it
                    subsection_title_elem = elem.find(f"ce:section-title", namespaces)
                    if subsection_title_elem is not None:
                        subsection_title = subsection_title_elem.text
                        subsection_paragraphs = []
                        subsubsections = []
                        
                        for sub_elem in elem:
                            # If this is a paragraph, append text
                            if sub_elem.tag == f"{{{namespaces['ce']}}}para":
                                paragraph_text = ''.join(sub_elem.itertext())
                                subsection_paragraphs.append(paragraph_text)
                            
                            # If this is a sub-subsection, process it
                            elif sub_elem.tag == f"{{{namespaces['ce']}}}section":
                                subsubsection_title_elem = sub_elem.find(f"ce:section-title", namespaces)
                                if subsubsection_title_elem is not None:
                                    subsubsection_title = subsubsection_title_elem.text
                                    subsubsection_paragraphs = []
                                    for subsub_elem in sub_elem.findall('ce:para', namespaces=namespaces):
                                        paragraph_text = ''.join(subsub_elem.itertext())
                                        subsubsection_paragraphs.append(paragraph_text)
                                    subsubsection_text = ' '.join(subsubsection_paragraphs)
                                    subsubsections.append({
                                        "label": sub_elem.find(f"ce:label", namespaces).text if sub_elem.find(f"ce:label", namespaces) is not None else "",
                                        "title": subsubsection_title,
                                        "text": subsubsection_text
                                    })
                        
                        subsection_text = ' '.join(subsection_paragraphs)
                        subsections.append({
                            "label": elem.find(f"ce:label", namespaces).text if elem.find(f"ce:label", namespaces) is not None else "",
                            "title": subsection_title,
                            "text": subsection_text,
                            "subsubsections": subsubsections
                        })
                else:
                    # Collect text before any subsection starts
                    if before_subsection_text and elem.tag == f"{{{namespaces['ce']}}}para":
                        paragraph_text = ''.join(elem.itertext())
                        section_text_parts.append(paragraph_text)

            section_text = ' '.join(section_text_parts)
            
            sections.append({
                "label": section_label.text if section_label is not None else "",
                "title": section_title.text if section_title is not None else "",
                "text": section_text,
                "subsections": subsections
            })

    # Extract the data availability section separately
    data_availability = root.find('.//ce:data-availability', namespaces)
    if data_availability is not None:
        data_availability_text = ''.join(data_availability.itertext())
        sections.append({
            "label": "",
            "title": "Data Availability",
            "text": data_availability_text,
            "subsections": []
        })

    return sections

# Function to postprocess sections, subsections, and subsubsections
def postprocess_sections(data):
    """
    Postprocesses sections, subsections, and subsubsections by removing duplicate labels and ensuring unique content.

    Args:
        data (list): A list of dictionaries, each containing the label, title, text, subsections, and subsubsections of a section.
    
    Returns:
        list: A list of dictionaries, each containing the label, title, text, subsections, and subsubsections of a section.

    Example:
        >>> reorganized_sections = postprocess_sections(sections)
        # Save the reorganized sections to a JSON file
        import json
        # Define the file path for the output
        output_file_path = '../example.json'
        
        # Open the file in write mode and dump the data
        with open(output_file_path, 'w') as file:
            json.dump(reorganized_sections, file, indent=4)  # Added indentation for better readability
        
        for section in reorganized_sections:
            print(section['label'], section['title'])
            for subsection in section['subsections']:
                print("    ", subsection['label'], subsection['title'])
                for subsubsection in subsection['subsubsections']:
                    print("        ", subsubsection['label'], subsubsection['title'])
    """
    reorganized_data = []
    
    labels_to_remove = set()
    
    for section in data:
        # Skip if the section is marked for removal
        if section["label"] in labels_to_remove:
            continue
        
        new_section = {
            "label": section["label"],
            "title": section["title"],
            "text": section["text"],
            "subsections": []
        }
        
        # Iterate through subsections to reorganize them
        for subsection in data:
            # Check if the subsection label starts with the section label and follows the x.x format
            if subsection["label"].startswith(section["label"] + ".") and len(subsection["label"].split('.')) == 2:
                new_subsection = {
                    "label": subsection["label"],
                    "title": subsection["title"],
                    "text": subsection["text"],
                    "subsubsections": []
                }
                labels_to_remove.add(subsection["label"])
                
                # Iterate through subsubsections to reorganize them under the appropriate subsection
                for subsubsection in data:
                    if subsubsection["label"].startswith(new_subsection["label"] + "."):
                        new_subsubsection = {
                            "label": subsubsection["label"],
                            "title": subsubsection["title"],
                            "text": subsubsection["text"]
                        }
                        labels_to_remove.add(subsubsection["label"])
                        new_subsection["subsubsections"].append(new_subsubsection)
                
                # Add the subsection only if it is unique or has no subsubsections
                if new_subsection["subsubsections"]:
                    # If subsubsections exist, avoid duplicate content
                    new_subsection["text"] = ""
                new_section["subsections"].append(new_subsection)
        
        reorganized_data.append(new_section)
    
    return reorganized_data


# search the "github.com" across all the text in all the sections, subsections, and subsubsections
# and extract the full github url, like https://github.com/username/repository
def extract_github_urls(text):
    # Regular expression to match only the main GitHub repository URLs
    github_url_pattern = r"https?://github\.com/[\w-]+/[\w-]+"
    
    # Find all matching GitHub repository URLs in the text
    github_urls = re.findall(github_url_pattern, text)
    
    return github_urls

def extract_full_github_urls(text):

    github_url_pattern = r"https?://github\.com/[^\s]+"

    github_urls = re.findall(github_url_pattern, text)
    return github_urls


def cleanup_abstract(abstract):
    """
    Cleans up an abstract string by standardizing spacing.

    Args:
        abstract (str): The abstract of a journal article, which may contain irregular spacing,
                        including multiple spaces, leading spaces, or trailing spaces.

    Returns:
        str: A cleaned string where all excessive spaces are replaced with a single space,
             and any leading or trailing spaces are removed. This is essential for preparing
             text data for further analysis or display, ensuring uniformity in the formatting
             of abstracts.

    Example:
        >>> cleanup_abstract("  This  is   an example   abstract.  ")
        'This is an example abstract.'
    """
    # Check if the input is a string
    if not isinstance(abstract, str):
        raise ValueError("Input must be a string.")
    
    return re.sub(r'\s+', ' ', abstract).strip()

def cleanup(abstract):
    """
    Cleans up an string by standardizing spacing.

    Args:
        abstract (str): The abstract of a journal article, which may contain irregular spacing,
                        including multiple spaces, leading spaces, or trailing spaces.

    Returns:
        str: A cleaned string where all excessive spaces are replaced with a single space,
             and any leading or trailing spaces are removed. This is essential for preparing
             text data for further analysis or display, ensuring uniformity in the formatting
             of abstracts.

    Example:
        >>> cleanup_abstract("  This  is   an example   abstract.  ")
        'This is an example abstract.'
    """
    # Check if the input is a string
    if not isinstance(abstract, str):
        raise ValueError("Input must be a string.")
    
    return re.sub(r'\s+', ' ', abstract).strip()


def get_context_with_url(location_text, url, context_up_range=2, context_down_range=2):
    """
    Extracts the sentence containing the URL along with a specified number of surrounding sentences.

    Args:
        location_text (str): The input text containing the URL.
        url (str): The URL to find in the text.
        context_range (int): The number of sentences before and after the target sentence to include.

    Returns:
        str: The context containing the URL along with the surrounding sentences, or a message if URL is not found.
    """
    # Step 1: Find the position of the URL
    sentence_index = location_text.find(url)

    # If the URL is found, proceed
    if sentence_index != -1:
        # Step 2: Split the text into sentences
        sentences = re.split(r'(?<=[.!?])\s+', location_text)

        # Step 3: Find the index of the sentence containing the URL
        target_index = None
        for index, sentence in enumerate(sentences):
            if url in sentence:
                target_index = index
                break

        # Step 4: Extract the surrounding context (few sentences before and after)
        if target_index is not None:
            start_index = max(0, target_index - context_up_range)  # Make sure index is not negative
            end_index = min(len(sentences), target_index + context_down_range + 1)  # Make sure index does not exceed list length

            # Get the sentences within the specified range
            surrounding_sentences = sentences[start_index:end_index]

            # Join the sentences to form the context
            context_info = " ".join(surrounding_sentences)
            return context_info
        else:
            return "URL not found in any sentence."
    else:
        return "URL not found in the text."
    


def extract_abstract_from_xml(file_path):
    """
    Extracts the abstract from an XML file.
    
    Args:
        file_path (str): The path to the XML file.

    Returns:
        str: The abstract text, or an empty string if no abstract is found.
    
    Example:
        >>> extract_abstract_from_xml('/path/to/file.xml')
        'This is the abstract...'
    """
    # Parse the XML file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Namespace to handle XML namespaces
    namespaces = {
        'xocs': 'http://www.elsevier.com/xml/xocs/dtd',
        'ce': 'http://www.elsevier.com/xml/common/dtd',
        'ja': 'http://www.elsevier.com/xml/ja/dtd',
        'mml': 'http://www.w3.org/1998/Math/MathML'
    }

    # Extract the abstract
    abstract = ""
    abstract_elem = root.find(".//ce:abstract", namespaces)
    if abstract_elem is not None:
        # Concatenate all text within the abstract element
        abstract = "".join(abstract_elem.itertext()).strip()

    return abstract
