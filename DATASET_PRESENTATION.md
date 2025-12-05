# Dataset Folder: Complete Output Presentation

## 📁 Dataset Structure

```
Dataset/
├── Dataset.txt                          [24,157 lines - Raw contract text]
├── Business_Compliance_Dataset.pdf      [PDF Report]
├── contracts_index.json                 [Contract metadata & versioning]
├── regulations.json                     [Regulation database]
└── contracts/
    ├── CT001-v1.txt                     [Original EU SaaS Agreement]
    ├── CT001-v2.txt                     [Amended EU SaaS Agreement]
    ├── CT002-v1.txt                     [Original India Hosting Contract]
    └── CT002-v2.txt                     [Amended India Hosting Contract]
```

---

## 📋 Files Overview

### 1. **Dataset.txt** (24,157 lines)
**Purpose**: Raw input - 145 service agreements with full contract text

**Structure**:
- Contract #001 - #145
- Each contract contains:
  - Header (ID, Type, Parties, Date)
  - 7 Standard Clauses:
    1. Scope of Services
    2. Confidentiality
    3. Data Protection (AI Act, GDPR, PCI DSS, HIPAA, etc.)
    4. Compliance & Audit Rights
    5. Termination
    6. Liability Limitation
    7. Governing Law
  - Signatories with titles

**Sample Contract**:
```
Contract #001 | Service Agreement | Rodriguez Figueroa and Sanchez ↔ Doyle Ltd | Date: March 24, 2025
- Provider: Rodriguez Figueroa and Sanchez
- Client: Doyle Ltd
- Regulations: AI Act, GDPR, PCI DSS
- Audit Rights: Yes (Doyle Ltd)
- Termination: 30 days notice for material breach
```

---

### 2. **contracts_index.json** (Metadata Database)
**Purpose**: Contract registry with version tracking

**Content Structure**:
```json
{
  "CT001": {
    "name": "EU SaaS Service Agreement",
    "jurisdiction": "EU",
    "version": 2,                    // Version control tracking
    "file": "contracts/CT001-v2.txt",
    "applied": ["REG-EU-001"]        // Applied regulations
  },
  "CT002": {
    "name": "India Hosting Contract",
    "jurisdiction": "IN",
    "version": 2,
    "file": "contracts/CT002-v2.txt",
    "applied": ["REG-IN-001"]
  }
}
```

**Key Features**:
- ✅ Version control (v1 → v2)
- ✅ Jurisdiction tracking (EU, IN)
- ✅ Amendment history (applied regulations)
- ✅ File path management

---

### 3. **regulations.json** (Regulation Database)
**Purpose**: Regulation catalog for compliance checking

**Regulations Defined**:

#### REG-EU-001: GDPR Consent Logging
```json
{
  "id": "REG-EU-001",
  "title": "GDPR Consent Logging",
  "jurisdiction": "EU",
  "summary": "Requires timestamp-based consent tracking.",
  "keywords": ["consent", "personal data", "logging"]
}
```
- **Applicability**: EU contracts
- **Key Requirement**: Timestamp consent tracking
- **Impact**: Contract CT001 already amended (v2)

#### REG-IN-001: India Data Localisation
```json
{
  "id": "REG-IN-001",
  "title": "India Data Localisation",
  "jurisdiction": "IN",
  "summary": "Requires sensitive personal data stored within India.",
  "keywords": ["localisation", "cross-border", "personal data"]
}
```
- **Applicability**: India contracts
- **Key Requirement**: Data stored within India only
- **Impact**: Contract CT002 already amended (v2)

#### REG-MOCK-60afb7: Global Privacy Profiling Disclosure
```json
{
  "id": "REG-MOCK-60afb7",
  "title": "Global Privacy Profiling Disclosure",
  "jurisdiction": "GLOBAL",
  "summary": "Requires organisations to notify users of automated profiling.",
  "keywords": ["profiling", "notice", "transparency"]
}
```
- **Applicability**: All contracts
- **Key Requirement**: User notification of profiling
- **Status**: Ready for application

---

### 4. **contracts_index.json** Contract Versions

#### CT001-v1.txt → CT001-v2.txt (EU SaaS Service Agreement)
**Amendment Status**: ✅ AMENDED (REG-EU-001 applied)
- **Regulation Applied**: GDPR Consent Logging
- **Changes**: Added timestamp-based consent tracking provisions
- **Jurisdiction**: EU
- **Timestamp**: Auto-recorded in regulatory.py system

#### CT002-v1.txt → CT002-v2.txt (India Hosting Contract)
**Amendment Status**: ✅ AMENDED (REG-IN-001 applied)
- **Regulation Applied**: India Data Localisation
- **Changes**: Added data localization requirements
- **Jurisdiction**: IN
- **Timestamp**: Auto-recorded in regulatory.py system

---

## 📊 Data Statistics

| Metric | Value |
|--------|-------|
| **Total Contracts** | 145 |
| **Raw Text Lines** | 24,157 |
| **Versioned Contracts** | 2 (CT001, CT002) |
| **Total Regulations** | 3 |
| **Active Regulations** | 2 applied |
| **Pending Regulations** | 1 (REG-MOCK-60afb7) |

---

## 🔄 Workflow: Input → Processing → Output

### Dataset Input Flow:
```
1. Dataset.txt
   ↓
2. Extract contracts (145 entries)
   ↓
3. Parse clauses (7 per contract)
   ↓
4. Apply regulations (regulatory.py)
   ↓
5. Create amendments (v1 → v2)
   ↓
6. Update contracts_index.json
   ↓
7. Store in contracts/ folder
```

### Regulation Application:
```
Contract + Regulation → Relevance Score → Amendment Creation
Example: CT001 + REG-EU-001 → Score: 8/10 → CT001-v2.txt (created)
```

---

## 🎯 Key Outputs by System

### System 1: app.py (LLM Analysis)
- **Input**: Dataset.txt (145 contracts)
- **Processing**: Groq LLM reasoning
- **Output**: `processed_results.json` (62 chunks, 835 KB)
- **Format**: Detailed compliance analysis per contract

### System 2: rag_system.py (Vector Search)
- **Input**: Dataset.txt (145 contracts)
- **Processing**: FAISS semantic search
- **Output**: `rag_analysis_report.pdf`
- **Format**: Q&A format retrieval results

### System 3: regulatory.py (Rules-Based)
- **Input**: Dataset.txt + regulations.json
- **Processing**: Keyword + jurisdiction scoring
- **Output**: 
  - `contracts_index.json` (versioning)
  - `contracts/` folder (amended versions)
  - `regulatory_result_pdf.pdf` (report)
- **Format**: Version-controlled amendments

---

## 📁 Dataset Folder File Map

| File | Purpose | Size | Type |
|------|---------|------|------|
| **Dataset.txt** | Raw contract corpus | ~1-2 MB | Text |
| **contracts_index.json** | Contract registry | <1 KB | JSON |
| **regulations.json** | Regulation database | <1 KB | JSON |
| **Business_Compliance_Dataset.pdf** | Visual report | ~500 KB | PDF |
| **contracts/CT001-v1.txt** | Original contract | ~2 KB | Text |
| **contracts/CT001-v2.txt** | Amended contract | ~2.5 KB | Text |
| **contracts/CT002-v1.txt** | Original contract | ~2 KB | Text |
| **contracts/CT002-v2.txt** | Amended contract | ~2.5 KB | Text |

---

## 🔍 Data Quality Features

✅ **Standardization**: All 145 contracts follow identical 7-clause structure
✅ **Metadata**: Each contract tagged with type, parties, date, jurisdiction
✅ **Version Control**: Amendment tracking with file versioning (v1, v2)
✅ **Regulatory Mapping**: Regulations linked to applicable contracts
✅ **Audit Trail**: Timestamp-based amendment recording
✅ **Jurisdiction Coverage**: EU, IN, GLOBAL regulations included

---

## 💡 Use Cases for Dataset

1. **Compliance Audit**: Find non-compliant clauses across 145 contracts
2. **Regulation Tracking**: Map which regulations apply to which contracts
3. **Amendment History**: See before/after versions (CT001-v1 vs v2)
4. **Risk Assessment**: Analyze compliance gaps systematically
5. **Industry Benchmarking**: Compare contract types across vendors
6. **Jurisdiction Analysis**: Filter contracts by applicable laws (EU, IN, etc.)

---

## 🚀 Next Steps for Guide Presentation

**Show Guide:**
1. **Raw Data**: Dataset.txt (sample 5-10 contracts)
2. **Metadata**: contracts_index.json (versioning system)
3. **Regulations**: regulations.json (compliance framework)
4. **Amendments**: CT001-v1 vs CT001-v2 (side-by-side comparison)
5. **PDF Report**: Business_Compliance_Dataset.pdf (visual summary)

**Explain:**
- How 145 raw contracts are standardized
- How regulations are applied to create amendments
- How version control tracks compliance evolution
- How three independent systems analyze the same data

---

**Status**: ✅ Dataset fully processed and ready for presentation
