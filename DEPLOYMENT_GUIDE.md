# Deployment Guide: Render + Cloudinary

## Table of Contents

1. [Cloudinary Setup](#cloudinary-setup)
2. [Render Setup](#render-setup)
3. [Local Testing](#local-testing)
4. [Troubleshooting](#troubleshooting)

---

## CLOUDINARY SETUP

### Step 1: Create Cloudinary Account

1. Go to https://cloudinary.com
2. Click **Sign Up** and complete registration
3. Verify your email
4. Go to your **Dashboard**
5. Copy these credentials (you'll need them):
   - **Cloud Name**
   - **API Key**
   - **API Secret** (keep this secret!)

### Step 2: Local Development Setup

1. Copy `.env.example` to `.env`:

   ```bash
   cp .env.example .env
   ```

2. Fill in your Cloudinary credentials in `.env`:

   ```env
   CLOUDINARY_CLOUD_NAME=your_cloud_name
   CLOUDINARY_API_KEY=your_api_key
   CLOUDINARY_API_SECRET=your_api_secret
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:

   ```bash
   python manage.py migrate
   ```

5. Create superuser:

   ```bash
   python manage.py createsuperuser
   ```

6. Test locally:
   ```bash
   python manage.py runserver
   ```

---

## RENDER SETUP

### Step 1: Prepare Your Repository

1. Make sure your project is in a GitHub repository
2. Commit all changes:
   ```bash
   git add .
   git commit -m "Add Render and Cloudinary configuration"
   git push origin main
   ```

### Step 2: Create Render Account

1. Go to https://render.com
2. Click **Sign Up**
3. Choose **Sign Up with GitHub**
4. Authorize Render to access your GitHub account

### Step 3: Create a PostgreSQL Database (Free Tier)

1. In Render dashboard, click **New +** → **PostgreSQL**
2. Fill in:
   - **Name**: `premium-job-board-db`
   - **Database**: `jobboard`
   - **User**: `jobboard_user`
   - **Region**: Choose closest to you
   - **PostgreSQL Version**: 15
   - **Plan**: Free
3. Click **Create Database**
4. Wait 2-3 minutes for creation
5. Copy the **External Database URL** (you'll use this)

### Step 4: Deploy Web Service

1. In Render dashboard, click **New +** → **Web Service**
2. Select your GitHub repository
3. Fill in settings:
   - **Name**: `premium-job-board`
   - **Environment**: `Python 3`
   - **Region**: Same as database
   - **Build Command**:
     ```bash
     pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
     ```
   - **Start Command**:
     ```bash
     gunicorn mysite.wsgi:application
     ```
   - **Plan**: Free (or paid if needed)

4. Click **Create Web Service**

### Step 5: Add Environment Variables

1. Go to your Web Service dashboard
2. Click **Environment** tab
3. Add these variables (copy from values below):
   - `SECRET_KEY`: Generate a new one (use: https://djecrety.ir/ or Python `secrets.token_urlsafe(50)`)
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `yourdomain.onrender.com,www.yourdomain.onrender.com`
   - `DATABASE_URL`: Paste the external URL from your PostgreSQL database
   - `CLOUDINARY_CLOUD_NAME`: Your cloud name
   - `CLOUDINARY_API_KEY`: Your API key
   - `CLOUDINARY_API_SECRET`: Your API secret
   - `PYTHONUNBUFFERED`: `1`

4. Click **Save Changes**
5. The service will redeploy automatically

### Step 6: Create Superuser on Render

After deployment completes:

1. Go to Web Service dashboard
2. Click **Shell** tab
3. Run:
   ```bash
   python manage.py createsuperuser
   ```
4. Follow prompts to create admin user

### Step 7: Your Site is Live!

- Your site will be at: `https://your-service-name.onrender.com`
- Admin panel: `https://your-service-name.onrender.com/admin/`

---

## LOCAL TESTING

### Test Before Deploying

1. Create local `.env` file with test credentials
2. Run migrations: `python manage.py migrate`
3. Collect static files: `python manage.py collectstatic --noinput`
4. Run: `python manage.py runserver`
5. Upload a test image to verify Cloudinary works
6. Check admin panel

---

## TROUBLESHOOTING

### Issue: Database migration failed

**Solution:**

1. Go to Render Web Service → Shell
2. Run: `python manage.py migrate --verbosity 2`
3. Check error messages

### Issue: Static files not appearing

**Solution:**

1. In Render dashboard, click your service
2. Go to Deployments
3. Click "Manual Deploy" → "Latest commit"
4. Wait for build to complete

### Issue: Cloudinary images not loading

**Solution:**

1. Verify credentials in Environment Variables
2. Check that images are uploaded to Cloudinary dashboard
3. Ensure `DEFAULT_FILE_STORAGE` is properly configured

### Issue: "Not allowed host" error

**Solution:**

1. Add your Render domain to `ALLOWED_HOSTS`:
   ```
   yourdomain.onrender.com,www.yourdomain.onrender.com
   ```

### Issue: Debug mode still on

**Solution:**

1. Set `DEBUG=False` in Environment Variables
2. Manually redeploy

---

## OPTIONAL: Custom Domain

1. Purchase domain (GoDaddy, Namecheap, etc.)
2. In Render, go to Web Service → Settings → Custom Domains
3. Add your domain
4. Update DNS records as shown (usually CNAME)
5. Wait for DNS validation (24-48 hours)

---

## Important Security Notes

⚠️ **Never commit `.env` file to GitHub**
⚠️ **Generate a new `SECRET_KEY` for production**
⚠️ **Never share API secrets**
⚠️ **Keep `DEBUG=False` in production**

---

## Quick Reference: Environment Variables

```env
SECRET_KEY=<generate-new-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.onrender.com
DATABASE_URL=<from-render-postgresql>
CLOUDINARY_CLOUD_NAME=<your-cloud-name>
CLOUDINARY_API_KEY=<your-api-key>
CLOUDINARY_API_SECRET=<your-api-secret>
PYTHONUNBUFFERED=1
```
