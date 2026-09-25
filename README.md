## 1. Project Overview

DOCURA is a document assistance prototype designed to help users upload documents, process their content, extract selected information, and assist with supported web-form workflows.

The system is designed to reduce repetitive document-to-form work while keeping the user in control. DOCURA assists the user with information but does not submit forms automatically.

---

## 2. Completed Project Scope

The DOCURA prototype includes:

- User registration and authentication
- Document upload
- Document storage
- Document processing queue
- Background document processing
- Tesseract OCR integration
- Field extraction
- User record
- Extracted-field display
- Source/provenance information
- Original document viewing and downloading
- Browser extension workflow
- Backend APIs
- Database integration
- Supabase Storage integration
- Production deployment
- Worker processing mechanism
- Search and export functionality
- Account management

---

## 3. Document Processing

The document processing workflow is:

```text
Document Upload
      ↓
Document Storage
      ↓
Processing Queue
      ↓
Worker
      ↓
Tesseract OCR
      ↓
OCR Text
      ↓
Field Extraction
      ↓
User Record

                    ┌─────────────────────┐
                    │       User          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   DOCURA Frontend   │
                    │ React + TypeScript  │
                    │       + Vite        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   DOCURA Backend    │
                    │       FastAPI       │
                    └──────┬──────┬───────┘
                           │      │
                  ┌────────┘      └─────────┐
                  ▼                         ▼
        ┌───────────────────┐     ┌──────────────────┐
        │ PostgreSQL /      │     │ Supabase Storage │
        │ Supabase Database │     │                  │
        └───────────────────┘     └──────────────────┘
                           │
                           ▼
                    ┌─────────────────┐
                    │ Processing Queue│
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Worker Trigger  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Tesseract OCR   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Field Extraction│
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ User Record     │
                    └─────────────────┘
