# Metadata Overview for Paper Analysis

This document outlines the key components and metadata fields used in the analysis of 10,000 research papers, particularly regarding GitHub links and data availability statements. Our data aims to provide a computational and measurable framework for analyzing the connections between research papers and their code/data availability, particularly in the realm of reproducibility and open science.


## Metadata Fields
The metadata is consolidated in the `full-meta-dataset` file, which provides details for the analyzed papers.

### Key Fields
1. **`is_github`**
   - Indicates whether any GitHub links are present in the paper (main paper, excluding the references).
   
2. **`num_of_github_urls`**
   - Specifies the number of GitHub links found in the paper (main paper, excluding the references).

3. **`is_availability`**
   - Indicates whether a ``data availability`` section is present in the paper.

4. **`is_data_mentioned_in_section`**
   - Flags whether the word ``data`` is mentioned in the section title.

5. **`is_experiment_mentioned_in_section`**
   - Flags whether the word ``experiment`` is mentioned in the section title.

6. **`is_link_in_availability_statement`**
   - Indicates if there are any links present in the data availability section.

7. **`num_of_links_in_availability_statement`**
   - Specifies the number of links found in the data availability section.

8. **`setup_files`**
   - True/False. Setup files (ie requirements.txt, build.gradle) present in the repo.

9. **`docker_files`**
   - True/False. Docker files present in the repo.

10. **`setup_in_readme`**
   - True/False. Setup instructions, ie packages and versions, present in the README.

11. **`shell_instructions_readme`**
   - True/False. Instructions about shell commands present in the README.

12. **`notebook_instructions_readme`**
   - True/False. Instructions about notebooks present in the README.

13. **`code_instructions_readme`**
   - True/False. Instructions for running code files present in the README.

14. **`has_readme`**
   - True/False. Github repo includes a readme.md.

## JSON Files
### `url_data.json`
- **Purpose**: Contains the URLs mentioned in the data availability statement.

### `github_data.json`
- **Purpose**: Contains URLs in the main text that include `github.com` links.
- **Note**: Not all GitHub links are necessarily authored by the paper's authors; they may link to other repositories.
- **Typical Case**: GitHub URLs in the format `github.com/username/repository` cover most cases.
- **Corner Case**: Nested paths like `https://github.com/google-research/google-research/tree/master/simulation_research` might require checking the full URL (`full_github_url`) to ensure they refer to the paper's tool and not a general open-source package.

### Use Case Notes

- For GitHub URLs:
  - The `full_github_url` field is essential for pinpointing the appropriate repository, especially in cases of nested paths or ambiguous ownership.
