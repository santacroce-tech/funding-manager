# Bitcoin Treasury Investment Management System

A Django-based admin panel for managing Bitcoin Treasury investment opportunities and investor relationships.

## Features

### Core Functionality
- **Opportunity Management**: Create and manage investment opportunities with funding goals and deadlines
- **Investor Management**: Add investors and assign wallet addresses for cryptocurrency payments
- **Investment Tracking**: Monitor individual investments and overall funding progress
- **Email Notifications**: Automated email system for investor communications
- **Wallet Integration**: Generate and manage cryptocurrency wallet addresses

### Admin Panel Features
- **Progress Bars**: Visual representation of funding progress
- **Custom Actions**: Bulk operations for wallet generation and email notifications
- **Transaction Tracking**: Link to blockchain explorers for transaction verification
- **Status Management**: Automatic status updates based on deadlines and funding progress

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd funding-manager
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the admin panel**
   - Open your browser and go to `http://127.0.0.1:8000/admin/`
   - Login with your superuser credentials

## Usage

### 1. Creating Opportunities
1. Go to **Opportunities** in the admin panel
2. Click **Add Opportunity**
3. Fill in the details:
   - Title and description
   - Company name
   - Total funding goal and currency
   - Minimum investment amount
   - Deadline
4. Save the opportunity

### 2. Adding Investors
1. Go to **Investors** in the admin panel
2. Click **Add Investor**
3. Fill in investor details:
   - Name and email
   - Phone number (optional)
4. Save the investor

### 3. Generating Wallets
1. Select one or more investors from the list
2. Use the **Generate wallet for selected investors** action
3. This will create a wallet address for each selected investor

### 4. Creating Investments
1. Go to **Investments** in the admin panel
2. Click **Add Investment**
3. Select the opportunity and investor
4. Set the investment amount and currency
5. Save the investment (this will automatically send an email notification)

### 5. Managing Investment Status
- **Pending**: Initial status when investment is created
- **Confirmed**: When payment is verified (updates opportunity progress)
- **Rejected**: If payment verification fails
- **Cancelled**: If investment is cancelled

## Email Notifications

The system automatically sends emails for:
- **Investment Created**: When a new investment is assigned
- **Investment Updated**: When investment status changes
- **Deadline Reminders**: Automated reminders for approaching deadlines
- **Opportunity Updates**: When opportunity details are modified

### Email Configuration

For development, emails are sent to the console. For production, update the email settings in `funding_manager/settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

## Management Commands

### Send Deadline Reminders
```bash
# Send reminders for opportunities with deadlines in the next 3 days
python manage.py send_deadline_reminders

# Send reminders for opportunities with deadlines in the next 7 days
python manage.py send_deadline_reminders --days-ahead 7

# Dry run to see what would be sent
python manage.py send_deadline_reminders --dry-run
```

## Models

### Opportunity
- Investment opportunity details
- Funding goals and progress tracking
- Deadline management
- Status tracking (active, funded, cancelled, expired)

### Investor
- Investor personal information
- Associated wallet address
- Investment history

### Investment
- Individual investment records
- Status tracking
- Transaction hash linking
- Automatic progress updates

### Wallet
- Cryptocurrency wallet addresses
- Support for BTC, ETH, USDT, USDC
- Wallet type and status tracking

### EmailNotification
- Email notification history
- Tracking of sent emails
- Notification types and status

## Admin Actions

### Investor Actions
- **Generate wallet**: Create wallet addresses for selected investors
- **Send test email**: Send test emails to selected investors

### Opportunity Actions
- **Send deadline reminders**: Send reminder emails for selected opportunities
- **Update expired opportunities**: Mark expired opportunities as expired

## Customization

### Wallet Integration
The current implementation uses placeholder wallet generation. For production, integrate with:
- Coinbase Commerce
- BitGo
- Other cryptocurrency wallet services

### Email Templates
Email templates are located in `investments/templates/investments/emails/`:
- `investment_created.html`
- `investment_updated.html`
- `deadline_reminder.html`
- `opportunity_update.html`

### Adding New Currencies
To add new cryptocurrencies:
1. Update `CURRENCY_CHOICES` in the Opportunity model
2. Update `WALLET_TYPE_CHOICES` in the Wallet model
3. Modify the wallet generation logic in `WalletService`

## Security Considerations

- Use environment variables for sensitive settings
- Implement proper authentication and authorization
- Use HTTPS in production
- Regularly backup the database
- Monitor email sending limits
- Implement rate limiting for API endpoints

## Production Deployment

1. **Set DEBUG = False** in settings
2. **Configure proper email settings**
3. **Use a production database** (PostgreSQL recommended)
4. **Set up static file serving**
5. **Configure HTTPS**
6. **Set up monitoring and logging**
7. **Implement backup strategies**

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License. 