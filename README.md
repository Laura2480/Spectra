# SPECTRA Project

![Project Overview](docs/images/overview.png)

## Overview

**SPECTRA** (Supporting Schizophrenia Patients Care with Artificial Intelligence) is a project funded by the PNRR aimed at providing advanced diagnostic analysis tools for psychiatrists. Utilizing cutting-edge Artificial Intelligence (AI) and Explainable Artificial Intelligence (XAI) techniques, SPECTRA supports the early diagnosis of Treatment-Resistant Schizophrenia (TRS).

### Project Objectives

1. **Language**: Analyze and process linguistic data to identify language markers associated with TRS.
2. **Motion**: Analyze movement data to detect motor anomalies related to TRS.
3. **Brain Structure**: Utilize neuroimaging to identify structural brain abnormalities.
4. **Emotional Response**: Evaluate emotional responses through physiological signals.

## Repository Structure

The main repository contains general documentation and specific branches for each project dimension:

- **main**: Overall project documentation and structure.
- **language**: Tools and models for linguistic analysis.
- **motion**: Tools and models for movement analysis.
- **brain_structure**: Tools and models for neuroimaging analysis.
- **emotional_response**: Tools and models for emotional response analysis.

## How to Navigate the Repository

### Cloning the Repository

\`\`\`bash
git clone <REMOTE_URL>
cd spectra
\`\`\`

### Switching to a Specific Branch

To work on a specific dimension, switch to the corresponding branch:

\`\`\`bash
git checkout language
\`\`\`

### Detailed Documentation

For more details on each dimension, refer to the respective \`README.md\` files in each branch.

## Project Abstract

### The SPECTRA Project: Biomedical Data for Supporting the Detection of Treatment Resistant Schizophrenia

*Rita Francese, Felice Iasevoli, Mariacarla Staffa*

**Abstract:**

The SPECTRA project aims to support clinicians in detecting patients suffering from a specific subclass of Schizophrenia (SZ), classified as Treatment-Resistant Schizophrenia (TRS) patients. TRS patients are challenging to diagnose and experience significant difficulties. Early diagnosis can improve their quality of life. This paper describes our study on identifying the types of biomedical data necessary for training machine learning algorithms to classify TRS/non-TRS patients with schizophrenia.

![Project Diagram](docs/images/project_diagram.png)

## How to Contribute

Contributions are welcome! Follow these steps:

1. Create a feature branch:
   \`\`\`bash
   git checkout -b feature/feature_name
   \`\`\`
2. Commit your changes:
   \`\`\`bash
   git commit -m "Description of changes"
   \`\`\`
3. Push the branch:
   \`\`\`bash
   git push origin feature/feature_name
   \`\`\`
4. Open a Pull Request on the main repository.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

This project was financially supported by the European Union NEXTGenerationEU project and the Italian Ministry of University and Research (MUR) through the PRIN 2022 PNRR project, no. D53D23017290001 entitled “Supporting Schizophrenia Patients Care with Artificial Intelligence (SPECTRA)”.
