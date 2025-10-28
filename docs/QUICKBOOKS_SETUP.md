# QuickBooks OAuth 2.0 Setup Guide

## Overview
This application uses OAuth 2.0 authorization code flow to access QuickBooks Online API data. Users authenticate with their Intuit accounts and grant permission to access their QuickBooks company data.

## QuickBooks Developer Account Setup

### 1. Create a QuickBooks App
1. Go to [QuickBooks Developer Portal](https://developer.intuit.com/)
2. Sign in with your Intuit account
3. Go to **"My Apps"** → **"Create an app"**
4. Select **"QuickBooks Online and Payments"**
5. Name your app (e.g., "In-Takt Portal")

### 2. Configure App Settings

#### Keys & OAuth
1. In your app dashboard, go to **"Keys & OAuth"** tab
2. Note your **Client ID** and **Client Secret**
3. Add to your `.env` file:
   ```bash
   QUICKBOOKS_CLIENT_ID=your_client_id_here
   QUICKBOOKS_CLIENT_SECRET=your_client_secret_here
   QUICKBOOKS_REDIRECT_URI=http://localhost:8000/quickbooks/callback/
   QUICKBOOKS_ENVIRONMENT=sandbox
   ```

#### Redirect URI
Add the following redirect URI:
```
http://localhost:8000/quickbooks/callback/
```

**For Production:**
```
https://yourdomain.com/quickbooks/callback/
```

### 3. Scopes
The application requests the following scope:
- `com.intuit.quickbooks.accounting` - Full access to accounting data

This scope provides access to:
- Company information
- Customers and vendors
- Invoices and bills
- Expenses and purchases
- Chart of accounts
- Financial reports

## Testing with Sandbox

QuickBooks provides a sandbox environment for testing:

1. In your app settings, ensure **Sandbox** mode is enabled
2. Set `QUICKBOOKS_ENVIRONMENT=sandbox` in your `.env`
3. Use sandbox test companies for development
4. **Sandbox API Base URL**: `https://sandbox-quickbooks.api.intuit.com/v3`

## Testing the OAuth Flow

### Step 1: Start Django Server
```bash
cd /home/rgamage/projects/in-takt
source venv/bin/activate
python manage.py runserver
```

### Step 2: Connect to QuickBooks
Visit: http://localhost:8000/quickbooks/login/

This will:
1. Generate a secure state token (CSRF protection)
2. Store state in session
3. Redirect you to Intuit's authorization page

### Step 3: Intuit Login & Authorization
You'll be redirected to QuickBooks where you will:
1. Sign in with your Intuit account
2. Select a company to connect (sandbox or production)
3. Review requested permissions
4. Click "Authorize"

### Step 4: Callback & Token Exchange
After authorization, QuickBooks redirects back to:
```
http://localhost:8000/quickbooks/callback/?code=<auth_code>&realmId=<company_id>&state=<state>
```

The callback handler will:
1. Verify the state token (CSRF protection)
2. Exchange authorization code for access token
3. Store tokens and realm_id (company ID) in Django session
4. Redirect to QuickBooks dashboard

### Step 5: View Dashboard
You should now see your QuickBooks dashboard at:
http://localhost:8000/quickbooks/dashboard/

## Available Endpoints

### OAuth Endpoints
- `/quickbooks/login/` - Initiate QuickBooks OAuth
- `/quickbooks/callback/` - OAuth callback (configured in Intuit)
- `/quickbooks/logout/` - Disconnect from QuickBooks
- `/quickbooks/dashboard/` - QuickBooks data dashboard (HTML)

### API Endpoints (JSON responses)
- `/quickbooks/api/customers/` - List customers
- `/quickbooks/api/invoices/` - List invoices
- `/quickbooks/api/vendors/` - List vendors
- `/quickbooks/api/expenses/` - List expenses
- `/quickbooks/api/accounts/` - List chart of accounts

### Reports API
- `/quickbooks/api/reports/profit-loss/` - Profit & Loss report
  - Parameters: `start_date`, `end_date` (YYYY-MM-DD)
- `/quickbooks/api/reports/balance-sheet/` - Balance Sheet report
  - Parameters: `date` (YYYY-MM-DD)

## API Documentation
All endpoints are documented in Swagger UI:
http://localhost:8000/api/docs/

## Token Management

### Access Token
- **Valid for**: 1 hour
- **Storage**: Django session (`qb_access_token`)
- **Used for**: All API requests

### Refresh Token
- **Valid for**: 100 days
- **Storage**: Django session (`qb_refresh_token`)
- **Used for**: Obtaining new access tokens

### Realm ID (Company ID)
- **Storage**: Django session (`qb_realm_id`)
- **Required for**: All API calls
- **Unique identifier** for the connected QuickBooks company

### Automatic Token Refresh
The dashboard view includes automatic token refresh logic:
```python
if token_expired:
    new_token = qb_service.refresh_access_token(refresh_token)
    session['qb_access_token'] = new_token['access_token']
    session['qb_refresh_token'] = new_token['refresh_token']
```

## QuickBooks Query Language (QQL)

The service class uses QuickBooks Query Language for data retrieval:

### Examples:
```python
# Get all customers
SELECT * FROM Customer MAXRESULTS 100

# Get invoices from specific date range
SELECT * FROM Invoice WHERE TxnDate >= '2024-01-01' MAXRESULTS 100

# Get unpaid invoices
SELECT * FROM Invoice WHERE Balance > '0' MAXRESULTS 100

# Get vendors sorted by name
SELECT * FROM Vendor ORDERBY DisplayName MAXRESULTS 100
```

## Available QuickBooks Entities

The QuickBooks API provides access to:

### Transactions
- Invoice, Bill, Payment, Purchase, SalesReceipt
- Estimate, CreditMemo, RefundReceipt
- Transfer, Deposit, JournalEntry

### Lists
- Customer, Vendor, Employee, Account
- Item, Class, Department, TaxCode

### Reports
- ProfitAndLoss, BalanceSheet, CashFlow
- GeneralLedger, TrialBalance, AgedReceivables

## Troubleshooting

### Error: "Invalid redirect URI"
- Ensure redirect URI is added to your QuickBooks app settings
- URI must match exactly (including http/https and trailing slash)
- Check `QUICKBOOKS_REDIRECT_URI` in `.env`

### Error: "Invalid client credentials"
- Verify `QUICKBOOKS_CLIENT_ID` and `QUICKBOOKS_CLIENT_SECRET`
- Ensure you're using the correct credentials (sandbox vs production)

### Error: "Invalid grant"
- Authorization code has expired (valid for 10 minutes)
- Try the OAuth flow again

### Error: "Token expired"
- Access token is valid for only 1 hour
- Use refresh token to get a new access token
- Implement automatic refresh in your views

### Error: "Company not found"
- realm_id may be incorrect
- User may have disconnected the app from QuickBooks
- Re-authenticate with OAuth flow

### Error: "Insufficient permissions"
- Ensure app has `com.intuit.quickbooks.accounting` scope
- User must grant access during OAuth flow

## Production Deployment

When moving to production:

1. **Update Environment Variable**:
   ```bash
   QUICKBOOKS_ENVIRONMENT=production
   QUICKBOOKS_REDIRECT_URI=https://yourdomain.com/quickbooks/callback/
   ```

2. **Update QuickBooks App Settings**:
   - Switch from Sandbox to Production keys
   - Add production redirect URI
   - Submit app for production review (if required)

3. **Security Considerations**:
   - Use HTTPS for all redirect URIs
   - Store secrets in Azure Key Vault
   - Enable Django session security settings
   - Implement rate limiting
   - Add proper logging and monitoring

4. **Testing**:
   - Test with real QuickBooks company data
   - Verify all API endpoints work correctly
   - Test token refresh mechanism
   - Test error handling

## Rate Limits

QuickBooks API has rate limits:
- **Minor version**: 500 requests per minute, per company
- **Major version**: Rate limits vary by app

Monitor response headers:
- `intuit_tid` - Transaction ID for support
- Rate limit information in response headers

## Best Practices

1. **Cache data** when possible to reduce API calls
2. **Use webhooks** for real-time updates (optional)
3. **Handle token expiration** gracefully
4. **Store realm_id** with user records for multi-company support
5. **Implement retry logic** for transient failures
6. **Log API requests** for debugging and monitoring
7. **Test with sandbox** before deploying to production

## Support & Resources

- [QuickBooks API Documentation](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/account)
- [OAuth 2.0 Guide](https://developer.intuit.com/app/developer/qbo/docs/develop/authentication-and-authorization/oauth-2.0)
- [API Explorer](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/account)
- [Developer Community](https://help.developer.intuit.com/)

## Next Steps

After successful setup:

1. ✅ Test OAuth flow with sandbox company
2. ✅ Verify dashboard displays company information
3. ✅ Test all API endpoints
4. ✅ Implement automatic token refresh in all views
5. ✅ Build HTMX-powered dashboard with live data
6. ✅ Add data visualization with charts
7. ✅ Implement caching for frequently accessed data
8. ✅ Prepare for production deployment
