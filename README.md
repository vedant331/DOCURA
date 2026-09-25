# DOCURA

## Document Understanding and Assistance System

DOCURA is a document assistance prototype designed to help users upload documents, process their content, and extract selected information that can later be used to assist with supported web forms.

The project focuses on reducing repetitive document-to-form work while keeping the user in control. DOCURA does **not** submit forms automatically.

> **Current status:** DOCURA is currently a working prototype demonstrated on **test/synthetic documents**. It should not be considered a fully validated real-world document processing system.

---

## 1. Project Overview

DOCURA provides a workflow where a user can:

1. Create an account / sign in.
2. Upload a document.
3. Store the uploaded document.
4. Add the document to a processing queue.
5. Process the document using OCR.
6. Extract selected fields from the document.
7. View the extracted information.
8. Use the extracted information as assistance for supported web-form workflows.
9. Review information before using it.
10. Submit the final form manually.

The main purpose of DOCURA is to assist users with repetitive information entry while maintaining user control over the final action.

---

## 2. Current Project Status

### Working

The following workflow has been successfully demonstrated:

```text
Sign In
   ↓
Upload Test Document
   ↓
Store Document
   ↓
Processing Queue
   ↓
Worker
   ↓
Tesseract OCR
   ↓
Field Extraction
   ↓
View Extracted Information
