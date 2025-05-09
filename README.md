# The SPECTRA Project

**SPECTRA** (Supporting Schizophrenia Patients Care with Artificial Intelligence) is a project funded by the PNRR aimed at providing advanced diagnostic analysis tools for psychiatrists. Utilizing cutting-edge Artificial Intelligence (AI) and Explainable Artificial Intelligence (XAI) techniques, SPECTRA supports the early diagnosis of Treatment-Resistant Schizophrenia (TRS).

---

## Gait Analysis

![Gait Analysis Overview](assests/images/gait_analysis.png)

- Examines **hip, knee, ankle, neck** movements and **walk metrics** (stride length, step width, velocity).
- Detects variability in cadence and stride, highlighting potential SZ-related motor impairments.

### Gait Analysis Methodology

![Gait Analysis 2](assests/images/gait_analysis_2.png)
1. **Multicamera Acquisition** (standard/stereo cameras)
2. **Skeleton Tracking** (MediaPipe, StackHourglass, etc.)
3. **Pattern Extraction** (Transformer-based embeddings)

### Gait Feature Extraction & Explanation

![Gait Analysis SHAP](assests/images/gait_analysis_shap.png)

- **Feature Extraction**: Derive relevant motor features (posture, variability, step length).
- **SHAP Explanation**: Visualize how specific gait features influence classification decisions.

---

## Contact

For more information or inquiries:  
**Email**: [francese@unisa.it](mailto:francese@unisa.it)

---

## License and Acknowledgments

- **Funding**: PRIN PNRR 2022, European Union NextGenerationEU.  
- **Collaborating Institutions**: University of Salerno, University of Naples “Federico II,” Parthenope University of Naples.  
- **License**: For licensing details, see the [LICENSE](LICENSE) file in this repository.

Thank you for exploring **The SPECTRA Project**! We appreciate your interest and contributions. 
