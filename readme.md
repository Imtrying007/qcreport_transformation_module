## 📊 QC Transformation & Ingestion Pipeline

A **Streamlit-based data engineering pipeline** that transforms QC Mode and CGC CSV files into structured Excel reports and serves as an **ingestion layer for the QC Portal**.

It is designed as a **modular ETL system for QC analytics, reporting, and downstream data consumption**.

live demo url : https://qcreporttransformationmodule.streamlit.app/
---

## 🚀 What This System Does

* Ingests QC Mode and CGC CSV files
* Processes data through a modular ETL pipeline
* Generates structured **multi-sheet Excel reports**
* Produces analytics for QC validation and reporting
* Acts as an **input ingestion layer for QC Portal workflows**

---

## 🧠 Key Capabilities

* ⚡ Fast in-memory data processing (no database dependency)
* 🔄 Modular ETL-style architecture
* 📊 Multi-level QC analytics (image, shop, summary)
* 📥 Structured Excel report generation
* 🔌 Dual role: Reporting engine + ingestion pipeline
* 🧩 Easily extensible transformation modules
* 🖥️ Lightweight Streamlit interface for internal users

---

## 🏗️ System Architecture

```id="x3g2p1"
QC Mode CSV + CGC CSV
          ↓
     main_file.py
          ↓
   Cleaned / Unified DataFrame
          ↓
 ┌────────────────────────────┐
 │  Transformation Layer      │
 │                            │
 │  image_level.py            │
 │  shop_category.py          │
 │  summary.py                │
 │  notes.py                  │
 └────────────────────────────┘
          ↓
   excel_generation.py
          ↓
 Excel Report + QC Ingestion Payload
```

---

## 📁 Project Structure

```id="p8n2qa"
QC_transformation_module/

app.py                         → Streamlit UI (entry point)

pipelines/                     → Core ETL pipeline
    main_file.py
    image_level.py
    latem_sheet_process.py
    shop_category.py
    summary.py
    notes.py
    excel_generation.py

utility/                       → Reusable business logic
    core_metrics.py
    grading.py
    recommendation.py
    session_manager.py

requirements.txt
.gitignore
readme.md
```

---

## 📄 Output

### 📦 Generated File

```
qc_transformation_output.xlsx
```

### 📊 Sheets Included

* **shopwise** → Category-level aggregation
* **image_wise** → Image-level QC evaluation
* **summary** → Overall QC performance metrics
* **notes** → Error / incorrect category insights

---

## ⚙️ Tech Stack

* Python
* Pandas
* Streamlit
* OpenPyXL
* NumPy

---

## ▶️ How to Run

```bash id="v9qkz3"
git clone https://github.com/Imtrying007/qc_mode_reports.git
cd qc_mode_reports

python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux

pip install -r requirements.txt

streamlit run app.py
```

Application runs at:

```
http://localhost:8501
```

---

## 🎯 Use Cases

* QC data validation & reporting
* Category performance analysis
* Image-level quality auditing
* Automated Excel report generation
* QC Portal ingestion pipeline
* Internal analytics automation

---

## 🔌 System Role in Data Ecosystem

This project functions as:

> ✔ ETL Processing Layer
> ✔ QC Analytics Engine
> ✔ Reporting System
> ✔ Ingestion Pipeline for QC Portal

---

## 📌 Engineering Highlights

* Modular ETL pipeline design
* Separation of UI and transformation logic
* Scalable pipeline structure for new QC rules
* Stateless in-memory processing (fast execution)
* Production-style folder architecture
* Reusable utility layer for business logic

---

## 🧾 License

Internal Use Only

---

## 👨‍💻 Author

**Shubham Dwivedi**

