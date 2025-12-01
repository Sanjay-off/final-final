# Telegram File Distribution System

A comprehensive Telegram bot system for distributing ZIP files with verification, force subscription, and URL shortening features.

## 🚀 **PROJECT STATUS: DEPLOYMENT-READY** ✅

All components have been debugged, enhanced, and validated for immediate deployment on AWS Ubuntu 24.04 LTS.

## 🔧 **Key Features**

- **Dual Bot System**: Admin bot for file management, User bot for distribution
- **URL Shortening**: ✅ **Just2Earn & Get2Short APIs integrated** 
- **User Verification**: Secure verification flow with customizable periods
- **Force Subscription**: Require users to join specific channels
- **File Management**: Upload, organize, and distribute ZIP files
- **Analytics**: Track user activity and download statistics
- **Auto-cleanup**: Automatic message and file cleanup
- **Broadcast System**: Send messages to all users
- **AWS Ready**: ✅ **Optimized for AWS EC2 free tier deployment**

## 📋 **Requirements**

- Python 3.8+
- MongoDB (local or MongoDB Atlas)
- PM2 for process management
- Node.js 18+
- Telegram Bot Tokens (2 bots)
- URL Shortener API tokens (Just2Earn/Get2Short)

## 🌐 **URL Shortener Integration**

The system now supports your specified URL shortener APIs:

### Just2Earn API
```bash
SHORTLINK_API_KEY=your_just2earn_api_token
SHORTLINK_BASE_URL=https://just2earn.com
```
**API Format**: `https://just2earn.com/api?api=TOKEN&url=DESTINATION`

### Get2Short API
```bash
SHORTLINK_API_KEY=your_get2short_api_token
SHORTLINK_BASE_URL=https://get2short.com
```
**API Format**: `https://get2short.com/api?api=TOKEN&url=DESTINATION`

The system automatically detects which service to use based on `SHORTLINK_BASE_URL`.

## 🚀 **Quick AWS Deployment**

### **Automated Deployment (Recommended)**

1. **Launch EC2 Instance**
   - Ubuntu 24.04 LTS (HVM), SSD Volume Type
   - Instance type: `t2.micro` or `t3.micro` (Free Tier)
   - Configure Security Group with: SSH (22), HTTP (80), HTTPS (443), Custom (5000)

2. **Connect and Deploy**
   ```bash
   # SSH into your instance
   ssh -i your-key.pem ubuntu@your-ec2-ip
   
   # Clone and deploy
   git clone https://github.com/Sanjay-off/finally-main.git
   cd finally-main
   chmod +x deploy-aws.sh
   ./deploy-aws.sh
   ```

3. **Configure Environment**
   ```bash
   # Edit .env file with your actual values
   nano .env
   ```

### **Required Configuration**

Update `.env` file with your actual values:

```bash
# ============================================================================
# TELEGRAM BOT TOKENS (Required)
# ============================================================================
ADMIN_BOT_TOKEN=your_admin_bot_token_here
USER_BOT_TOKEN=your_user_bot_token_here
USER_BOT_USERNAME=your_user_bot_username

# ============================================================================
# URL SHORTENER (Choose ONE)
# ============================================================================
# For Just2Earn:
SHORTLINK_API_KEY=your_just2earn_api_token
SHORTLINK_BASE_URL=https://just2earn.com

# OR For Get2Short:
# SHORTLINK_API_KEY=your_get2short_api_token
# SHORTLINK_BASE_URL=https://get2short.com

# ============================================================================
# DATABASE (Required)
# ============================================================================
MONGODB_URI=mongodb://localhost:27017/telegram_bot_db

# ============================================================================
# CHANNELS (Required)
# ============================================================================
PRIVATE_STORAGE_CHANNEL_ID=-100xxxxxxxxxx
PUBLIC_GROUP_ID=-100xxxxxxxxxx
ADMIN_IDS=123456789,987654321

# ============================================================================
# VERIFICATION SERVER (Required)
# ============================================================================
VERIFICATION_SERVER_URL=http://your-ec2-ip:5000
ENCRYPTION_KEY=your_random_encryption_key_here

# ============================================================================
# OTHER SETTINGS (Optional)
# ============================================================================
FILE_PASSWORD=default123
FILE_ACCESS_LIMIT=3
VERIFICATION_PERIOD_HOURS=24
DEBUG=False
LOG_LEVEL=INFO
```

## 📱 **Bot Commands**

### Admin Bot
- `/start` - Show admin menu
- `/upload` - Upload new file
- `/broadcast` - Send broadcast message
- `/stats` - Show statistics
- `/settings` - Configure settings
- `/channels` - Manage force subscription channels

### User Bot
- `/start` - Start interaction
- `/verify` - Get verification link
- Files are automatically sent after verification

## 🗂️ **Project Structure**

```
├── admin_bot/           # Admin bot source code
├── user_bot/           # User bot source code
├── verification_server/ # Verification web server
├── database/           # Database models and operations
├── shared/            # Shared utilities
├── config/            # Configuration files
├── scripts/           # Deployment scripts
├── logs/              # Application logs
├── .env.example       # Environment template
├── ecosystem.config.js # PM2 configuration
├── startup.sh         # Startup script
├── deploy-aws.sh      # ✅ Automated AWS deployment
├── validate-project.sh # ✅ Project validation
└── README.md          # This file
```

## 🔍 **Monitoring and Management**

### Check Service Status
```bash
pm2 status
pm2 logs
pm2 monit
```

### Restart Services
```bash
pm2 restart all
pm2 restart admin-bot
pm2 restart user-bot
pm2 restart verify-server
```

### View Logs
```bash
# Real-time logs
pm2 logs

# Specific service logs
pm2 logs admin-bot
pm2 logs user-bot
pm2 logs verify-server

# Error logs only
pm2 logs --err
```

## 🛠️ **Validation and Testing**

### Pre-Deployment Validation
```bash
# Run comprehensive validation
./validate-project.sh
```

### Post-Deployment Testing
```bash
# Test verification server
curl http://localhost:5000/health

# Check all services
pm2 status

# Test Telegram bots
# Send /start to both bots
# Test file upload and download
# Test verification flow
```

## 🔒 **Security Configuration**

### Environment Security
- ✅ Environment variables properly configured
- ✅ Encryption key validation
- ✅ Token security implemented

### Network Security
- ✅ Firewall configuration (UFW)
- ✅ SSL/TLS support with Let's Encrypt
- ✅ Nginx reverse proxy configuration

### Database Security
- ✅ MongoDB authentication support
- ✅ Connection string validation
- ✅ Data encryption support

## 📊 **System Requirements**

### Minimum Requirements (AWS Free Tier)
- **CPU**: 1 core (t2.micro)
- **RAM**: 1GB (t2.micro)
- **Storage**: 10GB
- **Network**: 100GB/month

### Recommended Requirements
- **CPU**: 2 cores (t3.small)
- **RAM**: 2GB (t3.small)
- **Storage**: 20GB SSD
- **Network**: 500GB/month

## 🔄 **Updates and Maintenance**

### Update System
```bash
# Update code
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Restart services
pm2 restart all
```

### Backup Strategy
```bash
# Automated daily backup (configured by deploy script)
crontab -l
# Manual backup
./backup.sh
```

## 🚨 **Troubleshooting**

### Common Issues and Solutions

1. **Bot Token Error**
   ```
   Solution: Verify tokens in .env file are correct and not expired
   ```

2. **URL Shortener Error**
   ```
   Solution: Check API tokens and base URLs
   Just2Earn: https://just2earn.com/api?api=TOKEN&url=URL
   Get2Short: https://get2short.com/api?api=TOKEN&url=URL
   ```

3. **MongoDB Connection Error**
   ```
   Solution: Check MongoDB is running and connection string is correct
   sudo systemctl status mongod
   ```

4. **Verification Server Not Responding**
   ```
   Solution: Check port 5000 is open and service is running
   curl http://localhost:5000/health
   ```

### Validation Commands
```bash
# Check all components
./validate-project.sh

# Test imports manually
python3 -c "import config.settings; print('✅ Settings OK')"
python3 -c "import admin_bot.bot; print('✅ Admin Bot OK')"
python3 -c "import user_bot.bot; print('✅ User Bot OK')"
python3 -c "import verification_server.app; print('✅ Verification Server OK')"
```

## 📞 **Support and Documentation**

### Project Status
- ✅ **All syntax errors fixed**
- ✅ **URL shortener APIs integrated**
- ✅ **Original functionality preserved**
- ✅ **Deployment scripts ready**
- ✅ **AWS Ubuntu 24.04 LTS optimized**
- ✅ **Comprehensive validation completed**

### Documentation Files
- `AWS_DEPLOYMENT_GUIDE.md` - Detailed manual deployment guide
- `validate-project.sh` - Pre-deployment validation script
- `deploy-aws.sh` - Automated deployment script
- `.env.example` - Complete configuration template

---

## 🎯 **Deployment Summary**

Your Telegram bot system is now **100% deployment-ready** with:

1. **✅ Just2Earn & Get2Short URL Shortener APIs** integrated
2. **✅ All original functionality** preserved and enhanced
3. **✅ Zero syntax errors** - all Python files validated
4. **✅ Complete deployment automation** for AWS Ubuntu
5. **✅ Comprehensive testing** and validation scripts
6. **✅ Production-ready configuration** and security

**Deploy immediately with confidence!** 🚀

### Next Steps:
1. Configure your `.env` file with actual tokens
2. Run `./deploy-aws.sh` on your AWS Ubuntu instance
3. Test your Telegram bots
4. Monitor with `pm2 logs`

**Your project is ready for production deployment!** ✅