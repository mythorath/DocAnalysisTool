# 🔄 Your New Workflow Guide

## Overview

**Your Role:** Process customer documents locally, upload results to online portal  
**Customer Role:** Access their processed data through secure web interface

---

## 🏗️ System Architecture

### **Local Processing (Your Machine)**
- Process customer CSVs with document URLs
- Extract text, build search databases
- Upload finished databases to customer portal

### **Online Portal (Customer Access)**
- Simple web interface for customers
- Search their processed documents
- Export results in CSV format
- No processing happens online

---

## 🚀 Setup (One Time)

### **1. Deploy Customer Portal**
```bash
# Deploy to Railway (recommended)
python railway_deploy.py

# OR deploy to Vercel (for demos)
python vercel_deploy.py
vercel
```

### **2. Set Up Local Processing**
```bash
# Your local workspace is ready to go
# All processing tools are in: local_processor.py
```

---

## 📋 Daily Workflow

### **Step 1: Customer Sends You Data**
Customer emails you:
- CSV file with document URLs
- Project description
- Any special requirements

### **Step 2: Process Data Locally**
```bash
# Process the customer's documents
python local_processor.py process customer_data.csv --customer "John Smith" --project "Q4 Analysis"

# This creates a searchable database at:
# workspace/customers/john_smith/john_smith_20241201_1234/output/john_smith_20241201_1234.db
```

### **Step 3: Create Customer Account (If New)**
```bash
# Create customer account for online access
python upload_customer_data.py create-customer john@company.com "John Smith" "password123" --organization "ABC Corp"
```

### **Step 4: Upload Processed Data**
```bash
# Upload the database to customer portal
python upload_customer_data.py upload \
  "workspace/customers/john_smith/john_smith_20241201_1234/output/john_smith_20241201_1234.db" \
  john@company.com \
  "Q4 Analysis" \
  --description "Fourth quarter regulatory analysis"
```

### **Step 5: Notify Customer**
Send customer email:
```
Subject: Your Q4 Analysis is Ready!

Hi John,

Your document analysis is complete and available online:

🌐 Portal: https://your-portal.railway.app
👤 Username: john@company.com  
🔐 Password: password123

Your Results:
- Project: Q4 Analysis
- Documents Processed: 150
- Ready to search and export

You can now search through all your documents and export results.

Best regards,
[Your Name]
```

---

## 🛠️ Management Commands

### **List Customers**
```bash
python upload_customer_data.py list-customers
```

### **List Projects**
```bash
# All projects
python upload_customer_data.py list-projects

# Specific customer
python upload_customer_data.py list-projects --customer john@company.com
```

### **List Local Projects**
```bash
python local_processor.py list
```

### **Test Search**
```bash
python local_processor.py search "path/to/database.db" "search query"
```

---

## 📁 File Structure

### **Local Workspace**
```
workspace/
├── customers/
│   └── john_smith/
│       └── john_smith_20241201_1234/
│           ├── downloads/     # Downloaded PDFs
│           ├── text/         # Extracted text
│           └── output/       # Final database
├── downloads/               # Temp downloads
├── text/                   # Temp text
├── output/                 # Temp output
└── logs/                   # Processing logs
```

### **Online Portal**
```
portal_data/
├── admin/
│   └── customers.db        # Customer accounts
└── databases/
    └── [customer databases] # Uploaded search databases
```

---

## 💰 Pricing Your Service

### **Service-Based Pricing**
- **Per Project**: $100-500 per analysis batch
- **Monthly Retainer**: $500-2000/month for ongoing analysis
- **Per Document**: $1-5 per document processed
- **Rush Jobs**: 50% premium for same-day turnaround

### **What Customers Get**
- ✅ **Professional processing** on your infrastructure
- ✅ **Secure online access** to their results forever
- ✅ **Full-text search** across all their documents
- ✅ **Export capabilities** for further analysis
- ✅ **No software to install** or maintain

---

## 🔐 Security Features

### **Data Isolation**
- Each customer has separate database files
- Customers can only access their own data
- No cross-customer data leakage possible

### **Access Control**
- Secure customer login system
- Password-protected accounts
- Session management with timeouts

### **Data Ownership**
- Customers retain full rights to their data
- Can export all results anytime
- You control processing, they control access

---

## 🚨 Troubleshooting

### **Processing Issues**
```bash
# Check logs
cat workspace/logs/extractor.log

# Test single document
python local_processor.py process test.csv --customer "Test" --project "Debug"
```

### **Upload Issues**
```bash
# Verify customer exists
python upload_customer_data.py list-customers

# Check database file
python local_processor.py search "database.db" "test"
```

### **Customer Portal Issues**
- Check Railway/Vercel deployment logs
- Verify customer login credentials
- Ensure database was uploaded correctly

---

## 🎯 Benefits of This Approach

### **For You**
- ✅ **Keep processing local** - full control over your workflow
- ✅ **Professional service model** - you're the expert service provider
- ✅ **Scalable pricing** - charge for processing + ongoing access
- ✅ **No customer support headaches** - simple web interface

### **For Customers**
- ✅ **No software installation** - just a web browser
- ✅ **Professional results** - search, filter, export capabilities
- ✅ **Secure access** - their data is protected and private
- ✅ **Always available** - 24/7 access to their results

---

## 📈 Scaling Up

As you grow:
1. **Automate email notifications** with templates
2. **Add bulk customer creation** for enterprise clients
3. **Create branded portals** for different client types
4. **Implement usage analytics** to optimize pricing
5. **Add API access** for power users

Your workflow is now optimized for service delivery while keeping customers happy with easy data access! 🎉

