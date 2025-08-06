# 🚀 Quick Start Guide

## 1. Deploy to Railway (Recommended)

Railway is perfect for production because it supports persistent storage and background processing.

### Step 1: Install Railway CLI
```bash
npm install -g @railway/cli
```

### Step 2: Deploy
```bash
python railway_deploy.py
```

### Step 3: Access Your Platform
- Your platform will be live at the URL provided
- Default admin login: `admin@platform.com` / `admin123`
- **Change the admin password immediately!**

## 2. Deploy to Vercel (For Demos)

Vercel is great for quick demos but has limitations for production use.

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Create Config
```bash
python vercel_deploy.py
```

### Step 3: Deploy
```bash
vercel
```

## 3. First Steps After Deployment

### 1. Secure Your Platform
- Visit your platform URL
- Login as admin: `admin@platform.com` / `admin123`
- **Immediately change the admin password**
- Note down your platform URL

### 2. Create Your First Customer
- In admin dashboard, click "Add Customer"
- Fill in customer details:
  - Email address
  - Full name
  - Organization (optional)
  - Temporary password
- Customer will use email + password to login

### 3. Process Customer Documents
- Click "Process Data" in admin dashboard
- Select the customer
- Enter project name and description
- Upload CSV file with document URLs (must have "Document ID" and "URL" columns)
- Click "Start Processing"

### 4. Customer Access
- Send customer the platform URL and their login credentials
- Customer logs in to see their private dashboard
- Customer can search documents and export results

## 4. Platform URLs

After deployment, you'll have:
- **Platform URL**: Your main platform (get from Railway/Vercel)
- **Admin Dashboard**: `https://your-url.com/admin`
- **Customer Login**: `https://your-url.com/login`

## 5. File Structure

Your platform will create this structure:
```
platform_data/
├── admin/
│   └── platform.db (main database)
├── customers/
│   └── [customer-id]/
│       ├── projects/
│       ├── uploads/
│       └── databases/
└── logs/
```

## 6. Security Features

✅ **Customer Isolation**: Each customer sees only their own data  
✅ **Secure Authentication**: Password hashing and session management  
✅ **Audit Logging**: All actions are logged for security  
✅ **Data Protection**: Encrypted sessions and secure headers  
✅ **Role-Based Access**: Admin vs customer permissions  

## 7. Troubleshooting

### Common Issues:
- **"Admin login failed"**: Use exact credentials `admin@platform.com` / `admin123`
- **"Processing stuck"**: Check that CSV has "Document ID" and "URL" columns
- **"Can't access customer data"**: Verify customer is logged in with correct email
- **"Search not working"**: Ensure document processing completed successfully

### Getting Help:
- Check platform logs in Railway/Vercel dashboard
- Verify environment variables are set correctly
- Ensure your CSV file format is correct

## 8. Next Steps

1. **Test the workflow** with a small batch of documents
2. **Customize branding** in the HTML templates
3. **Set up monitoring** and backups
4. **Scale your infrastructure** as you get more customers
5. **Add custom domains** for professional appearance

## 9. Pricing Your Service

Consider these pricing models:
- **Per-project**: $50-200 per analysis project
- **Monthly subscription**: $100-500/month for unlimited processing
- **Pay-per-document**: $0.10-1.00 per document processed
- **Enterprise**: Custom pricing for large organizations

Your platform is now ready to serve customers! 🎉

