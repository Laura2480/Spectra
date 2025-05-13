# Taldetect FE
# 🧠 taldetect-fe
**taldetect-fe** is the front-end of the taldetect system, designed to analyze doctor-patient conversations and generate automated reports based on the TALD (Typical Atypical Language Dimension) scale.
It leverages language models (LLMs), advanced audio processing, and NLP to support clinical evaluation through structured communication analysis.

![Homepage](https://github.com/user-attachments/assets/ee8464fd-8eb3-41f7-931d-47baa33d8b94)

👉 This frontend powers the backend available at this link:
**[https://github.com/giampierus/taldetect-be/tree/7f4d488f8fb0b6eaccd3bee20f472cef76036792]**

## ✨ Key Features

- 🎙️ Automatic transcription of audio with **Whisper**
- 🧠 NLP and linguistic analysis with **spaCy** and **Transformers**
- 📈 Automatic extraction of **TALD scores**
- 📄 Generation of readable, printable multi-page PDF reports
- 🔍 Recognition of **linguistic patterns** like echolalia, verbigeration, repetitions, etc.
- 🔐 JWT authentication integrated with Firebase
- ☁️ Connection to MongoDB Atlas for data storage
- 📬 Report delivery via email
- 🌐 Quick API access even in cloud/Colab environments (via `ngrok`)
- 🌐 Quick Client access in Cloud/Google and firebase environments via web app link
- 🔐 Automatic SSL by firebase deploy
---

## 🛠 Tech Stack

| Category        | Key Libraries and Tools                                     |
|-----------------|-------------------------------------------------------------|
| Web Client      | Angular, NodeJS, Angular Material, Bootstrap, Google Charts |
| Provider        | Google Cloud and Firebase                                   |
---

MIT License.
© 2025 — taldetect project developed with ❤️ for research and mental health.
