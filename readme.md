# 📊 QC Transformation Pipeline

A simple internal Streamlit application to transform **QC Mode** and **CGC CSV** files and generate a structured Excel report.

---

# 🚀 Overview

This tool allows users to:

* Upload **QC Mode CSV**
* Upload **CGC CSV**
* Run transformation pipeline
* Generate Excel report with multiple sheets
* Download final output

The application is designed for **internal team usage** 

---

# 📁 Project Structure

```
QC_transformation_module/

app.py
requirements.txt
README.md
.gitignore

pipelines/
    main_file.py
    image_level.py
    shop_category.py
    summary.py
    notes.py
    excel_generation.py

utility/
      grading.py
      recommendation.py
```

---

# ⚙️ Requirements

* Python 3.9+
* Streamlit
* Pandas
* Numpy
* OpenPyXL

---

# 📦 Installation

## Step 1: Clone Repository

```
git clone https://github.com/Imtrying007/qc_mode_reports.git


---

## Step 2: Create Virtual Environment

### Windows

```
python -m venv venv
venv\Scripts\activate
```

### Mac/Linux

```
python3 -m venv venv
source venv/bin/activate
```

---

## Step 3: Install Dependencies

```
pip install -r requirements.txt
```

---

# ▶️ Run Application

```
streamlit run app.py
```

Application will start at:

```
http://localhost:8501
```

---

# 📊 How the Application Works

### 1️⃣ Upload Files

* QC Mode CSV
* CGC CSV

### 2️⃣ Click Run Transformation

Pipeline executes in sequence:

```
main_file.py
image_level.py
shop_category.py
summary.py
notes.py
excel_generation.py
```

### 3️⃣ Download Excel

Final Excel file is generated with multiple sheets.

---

# 📄 Output Excel

Generated file:

```
qc_transformation_output.xlsx
```

### Sheets Included

| Sheet Name | Description                   |
| ---------- | ----------------------------- |
| shopwise   | Shop category aggregation     |
| image_wise | Image-level analysis          |
| summary    | Overall QC summary            |
| notes      | AI incorrect category summary |

---

# 🧠 Pipeline Flow

```
QC Mode CSV
CGC CSV
      ↓
main_file.py
      ↓
Analytic DataFrame
      ↓
image_level.py
shop_category.py
summary.py
notes.py
      ↓
excel_generation.py
      ↓
Final Excel Output
```

---

# 🛠 Tech Stack

* Python
* Pandas
* Streamlit
* OpenPyXL

---

# 👨‍💻 Usage

This tool is intended for:

* QC teams
* Internal data transformation
* Competition analysis
* Category performance tracking
* Excel report generation

---

# 📌 Key Features

* Simple UI
* No login required
* No database required
* In-memory processing
* Fast execution
* Multiple Excel sheets
* Internal deployment friendly
* Supports 10–15 users

---

# 📦 requirements.txt

```
streamlit
pandas
numpy
openpyxl
```

---

# 🚀 Deployment Options

### Local Deployment

```
streamlit run app.py
```

### Streamlit Community Cloud

1. Push code to GitHub
2. Go to Streamlit Cloud
3. Select repository
4. Deploy app

---

# 🧾 License

Internal Use Only

---

# 👤 Author

Shubham Dwivedi

QC Transformation Module
