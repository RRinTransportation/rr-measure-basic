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
   - Indicates whether a "data availability" section is present in the paper.

4. **`is_data_mentioned_in_section`**
   - Flags whether the word "data" is mentioned in the section title.

5. **`is_experiment_mentioned_in_section`**
   - Flags whether the word "experiment" is mentioned in the section title.

6. **`is_link_in_availability_statement`**
   - Indicates if there are any links present in the data availability section.

7. **`num_of_links_in_availability_statement`**
   - Specifies the number of links found in the data availability section.

8. **`source_description`**
   - Provides the detailed information about the source of the data, e.g. how the author collected the data.

9. **`real_world`**
   - Indicates whether the dataset relates to real-world collections or observations. If the network is derived from a real-world dataset, it is considered real-world.

10. **`simulation`**
    - Flags whether the dataset or experiment is derived from a simulation.

11. **`dataset_size_description`**
    - Indicates whether there is a description of the dataset size in the paper.

12. **`data_collection_description`**
    - Indicates whether the paper describes the methods or procedures used for collecting the data.

13. **`is_data_mentioned`**
    - Flags whether the paper explicitly mentions data or datasets in its content (abstract, sections).

14. **`setup_files`**
    - True/False. Indicates if setup files (i.e., requirements.txt, build.gradle) are present in the repository.

15. **`docker_files`**
    - True/False. Indicates if Docker files are present in the repository.

16. **`setup_in_readme`**
    - True/False. Indicates if setup instructions, such as packages and versions, are present in the README.

17. **`shell_instructions_readme`**
    - True/False. Indicates if instructions about shell commands are present in the README.

18. **`notebook_instructions_readme`**
    - True/False. Indicates if instructions about notebooks are present in the README.

19. **`code_instructions_readme`**
    - True/False. Indicates if instructions for running code files are present in the README.

20. **`has_readme`**
    - True/False. Indicates if the GitHub repository includes a README.md file.

21. **`cited_by`**
    - Provides the number of citations received by the paper (data extracted from Scopus API).

22. **`number_of_authors`**
    - Indicates the total number of authors involved in the publication.

23. **`country`**
    - Specifies the primary country of the first author.

24. **`institution`**
    - Lists the affiliated institution(s) of the first author.

25. **`corresponding_author_country`**
    - Specifies the country of the corresponding author.

26. **`corresponding_author_name`**
    - Indicates the name of the corresponding author.

27. **`primary_author_name`**
    - Specifies the name of the first author.

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
